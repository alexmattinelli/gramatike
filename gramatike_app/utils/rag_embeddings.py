"""
Indexação e busca semântica (RAG) usando sentence-transformers + FAISS (CPU).
Suporta corpora com 100k+ textos em lotes; persiste índice e metadados em instance/.
"""
from __future__ import annotations
from typing import List, Dict, Tuple, Optional
import os, json


_MODEL_NAME = os.environ.get('RAG_MODEL', 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
_INDEX_FILE = 'rag_index.faiss'
_META_FILE = 'rag_meta.json'
_HNSW_FILE = 'rag_hnsw.bin'


def _instance_path(*paths) -> str:
    base = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'instance'))
    try:
        os.makedirs(base, exist_ok=True)
    except Exception:
        pass
    return os.path.join(base, *paths)


def _load_faiss():
    try:
        import faiss  # type: ignore
        return faiss
    except Exception:
        return None

def _load_hnsw():
    try:
        import hnswlib  # type: ignore
        return hnswlib
    except Exception:
        return None


class _Encoder:
    def __init__(self):
        self.backend = None
        self.model = None
        # 1) fastembed (leve, sem torch)
        try:
            from fastembed import TextEmbedding  # type: ignore
            self.model = TextEmbedding(model_name=_MODEL_NAME)
            self.backend = 'fastembed'
            return
        except Exception:
            self.model = None
        # 2) sentence-transformers
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore
            self.model = SentenceTransformer(_MODEL_NAME)
            self.backend = 'st'
            return
        except Exception:
            self.model = None
        # 3) TF-IDF (fallback determinístico)
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore
            self.model = TfidfVectorizer(max_features=4096)
            self.backend = 'tfidf'
            return
        except Exception:
            self.model = None

    def encode(self, texts: List[str]):
        import numpy as np
        if self.backend == 'st':
            vecs = self.model.encode(texts, batch_size=64, show_progress_bar=False, convert_to_numpy=True, normalize_embeddings=True)
            if not isinstance(vecs, np.ndarray):
                vecs = np.array(vecs, dtype='float32')
            return vecs.astype('float32')
        if self.backend == 'fastembed':
            # fastembed gera iterável de vetores
            arr = [v for v in self.model.embed(texts)]
            vecs = np.array(arr, dtype='float32')
            # normaliza L2
            norms = np.linalg.norm(vecs, axis=1, keepdims=True) + 1e-12
            vecs = vecs / norms
            return vecs.astype('float32')
        if self.backend == 'tfidf':
            # Para TF-IDF precisamos "ajustar" no corpus completo. Aqui, tratamos chamado único.
            # Chamaremos via _encode_texts em dois modos: treino e transformação.
            raise RuntimeError('TFIDF_DIRECT_CALL')
        raise RuntimeError('Nenhum backend de embedding disponível')


_ENCODER: Optional[_Encoder] = None

def _get_encoder() -> _Encoder:
    global _ENCODER
    if _ENCODER is None:
        _ENCODER = _Encoder()
    return _ENCODER


def _load_index_and_meta():
    faiss = _load_faiss()
    hnsw = _load_hnsw()
    idx_path = _instance_path(_INDEX_FILE)
    meta_path = _instance_path(_META_FILE)
    # Tentativa FAISS
    if faiss is not None and os.path.exists(idx_path) and os.path.exists(meta_path):
        index = faiss.read_index(idx_path)
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
        except Exception:
            # meta corrompido: renomeia e inicia vazio
            try:
                os.replace(meta_path, meta_path + '.bad')
            except Exception:
                pass
            return index, []
        return index, meta
    # Tentativa HNSW
    hnsw_path = _instance_path(_HNSW_FILE)
    if hnsw is not None and os.path.exists(hnsw_path) and os.path.exists(meta_path):
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
        except Exception:
            try:
                os.replace(meta_path, meta_path + '.bad')
            except Exception:
                pass
            meta = []
        # inferir dimensão a partir do primeiro vetor salvo? Não temos; usaremos do índice serializado
        # hnswlib consegue carregar sem dimensão explícita
        # Criar objeto temporário para load
        # Precisamos da dimensão; armazenamos na meta sentinel quando criarmos
        dim = None
        if meta and isinstance(meta[0], dict) and meta[0].get('_hnsw_dim'):
            dim = int(meta[0]['_hnsw_dim'])
        if dim is None:
            # tentativa: fallback para 768 (comum em modelos leves)
            dim = 768
        p = hnsw.Index(space='cosine', dim=dim)
        p.load_index(hnsw_path)
        p.set_ef(200)
        return p, meta
    # Fallback NumPy
    npy_path = _instance_path('rag_index.npy')
    if os.path.exists(npy_path) and os.path.exists(meta_path):
        import numpy as np
        vecs = np.load(npy_path).astype('float32')
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
        except Exception:
            try:
                os.replace(meta_path, meta_path + '.bad')
            except Exception:
                pass
            meta = []
        return vecs, meta
    return None, []


def _save_index_and_meta(index, meta):
    faiss = _load_faiss()
    hnsw = _load_hnsw()
    idx_path = _instance_path(_INDEX_FILE)
    meta_path = _instance_path(_META_FILE)
    # FAISS
    if faiss is not None and hasattr(index, 'ntotal'):
        faiss.write_index(index, idx_path)
    # HNSW
    elif hnsw is not None and hasattr(index, 'save_index'):
        hnsw_path = _instance_path(_HNSW_FILE)
        index.save_index(hnsw_path)
    else:
        # Fallback: salvar matriz numpy
        import numpy as np
        npy_path = _instance_path('rag_index.npy')
        arr = index if isinstance(index, np.ndarray) else None
        if arr is None:
            raise RuntimeError('Índice inválido no modo NumPy')
        np.save(npy_path, arr)
    # Escreve meta de forma atômica para evitar truncamento
    try:
        tmp_path = meta_path + '.tmp'
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(meta, f, ensure_ascii=False)
        os.replace(tmp_path, meta_path)
    except Exception:
        # fallback direto
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(meta, f, ensure_ascii=False)


def _encode_texts(texts: List[str], tfidf_fit: bool = False, tfidf_state: Optional[dict] = None):
    import numpy as np
    enc = _get_encoder()
    # 1) sentence-transformers / fastembed
    if enc.backend in ('st','fastembed'):
        return enc.encode(texts)
    # 2) TF-IDF se disponível
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore
        if enc.backend == 'tfidf':
            if tfidf_fit:
                vec = enc.model.fit_transform(texts)
                state = {
                    'vocabulary_': enc.model.vocabulary_,
                    'idf_': enc.model.idf_.tolist(),
                }
                if tfidf_state is not None:
                    tfidf_state.update(state)
            else:
                if not tfidf_state:
                    raise RuntimeError('TFIDF sem estado')
                model = TfidfVectorizer(max_features=4096)
                model.vocabulary_ = tfidf_state['vocabulary_']
                model.idf_ = np.array(tfidf_state['idf_'])
                model._tfidf._idf_diag = None
                vec = model.transform(texts)
            arr = vec.astype('float32').toarray()
            norms = np.linalg.norm(arr, axis=1, keepdims=True) + 1e-12
            arr = arr / norms
            return arr.astype('float32')
    except Exception:
        pass
    # 3) Fallback hashing (sem sklearn/torch)
    import re
    dim = 768
    M = np.zeros((len(texts), dim), dtype='float32')
    token_re = re.compile(r"\w+", re.UNICODE)
    for i, t in enumerate(texts):
        s = (t or '').lower()
        toks = token_re.findall(s)
        for w in toks:
            M[i, (hash(w) % dim)] += 1.0
        for a, b in zip(toks, toks[1:]):
            M[i, (hash(a+'_'+b) % dim)] += 1.0
        n = float(np.linalg.norm(M[i]))
        if n > 0:
            M[i] /= n
    return M


def _ensure_index(dim: int):
    faiss = _load_faiss()
    if faiss is not None:
        return faiss.IndexFlatIP(dim)  # inner product com vetores normalizados = cos sim
    hnsw = _load_hnsw()
    if hnsw is not None:
        # criamos vazio; capacidade será definida nos chamadores ao criar do zero
        # retornamos apenas um marcador para sinalizar uso de hnsw
        return ('hnsw', dim)
    # Fallback: retornamos uma matriz vazia (NumPy) para concatenação
    import numpy as np
    return np.zeros((0, dim), dtype='float32')


def _gather_corpus_from_db(limit: Optional[int] = None) -> List[Dict]:
    """Coleta documentos do DB (EduContent) como lista de dicts.
    Retorno item: { 'source': 'EduContent', 'id': <pk>, 'title': str, 'url': str, 'text': str }
    """
    from gramatike_app.models import EduContent
    docs: List[Dict] = []
    # EduContent
    try:
        q = EduContent.query.order_by(EduContent.created_at.desc())
        if limit: q = q.limit(limit)
        for r in q.all():
            text = (r.corpo or r.resumo or '')
            if (text or '').strip():
                docs.append({'source':'EduContent','id':r.id,'title':r.titulo or '', 'url': r.url or '', 'text': text, 'tag': 'edu'})
    except Exception:
        pass
    # Removido: LuneKnowledge
    return docs


def build_index_from_db(limit: Optional[int] = None) -> Tuple[int, int]:
    """Reconstrói o índice a partir do DB, com chunking. Retorna (n_chunks, dim)."""
    docs = _gather_corpus_from_db(limit=limit)
    if not docs:
        raise RuntimeError('Corpus vazio.')
    # Chunking
    records: List[Dict] = []
    for d in docs:
        chunks = _chunk_text(d.get('text') or '')
        for ch in chunks:
            rec = dict(d)
            rec['text'] = ch
            records.append(rec)
    texts = [r['text'] for r in records]
    if not texts:
        raise RuntimeError('Sem texto para indexar.')
    tfidf_state = {}
    try:
        vecs = _encode_texts(texts, tfidf_fit=True, tfidf_state=tfidf_state)
    except Exception:
        # tenta sem TF-IDF (ST/fastembed)
        tfidf_state = {}
        vecs = _encode_texts(texts)
    dim = vecs.shape[1]
    # Backend preferido: FAISS > HNSW > NumPy
    faiss = _load_faiss(); hnsw = _load_hnsw()
    if faiss is not None:
        index = faiss.IndexFlatIP(dim)
        index.add(vecs)
    elif hnsw is not None:
        p = hnsw.Index(space='cosine', dim=dim)
        p.init_index(max_elements=vecs.shape[0], ef_construction=200, M=48)
        p.add_items(vecs)
        p.set_ef(200)
        index = p
        # guardar dimensão no meta sentinel
        records = [{'_hnsw_dim': dim}] + records
    else:
        import numpy as np
        index = np.concatenate([np.zeros((0, dim), dtype='float32'), vecs], axis=0)
    # anexa sentinels no topo
    sentinels = []
    if tfidf_state:
        sentinels.append({'_tfidf_state': tfidf_state})
    if hnsw is not None and not any(isinstance(x, dict) and x.get('_hnsw_dim') for x in records[:1]):
        # já adicionamos acima quando hnsw foi usado
        pass
    if sentinels:
        records = sentinels + records
    _save_index_and_meta(index, records)
    return len(records), vecs.shape[1]


def _chunk_text(text: str, max_len: int = 1200) -> List[str]:
    s = (text or '').strip()
    if not s:
        return []
    if len(s) <= max_len:
        return [s]
    parts: List[str] = []
    cur = []
    cur_len = 0
    for para in s.split('\n'):
        p = para.strip()
        if not p:
            continue
        if cur_len + len(p) + 1 > max_len:
            parts.append(' '.join(cur).strip())
            cur = [p]; cur_len = len(p)
        else:
            cur.append(p); cur_len += len(p) + 1
    if cur:
        parts.append(' '.join(cur).strip())
    return parts


def _append_to_index(docs: List[Dict]) -> int:
    """Acrescenta documentos ao índice existente (ou cria). Retorna quantos foram adicionados."""
    if not docs:
        return 0
    records = []
    for d in docs:
        t = (d.get('text') or '').strip()
        if not t:
            continue
        chunks = _chunk_text(t)
        for ch in chunks:
            rec = dict(d)
            rec['text'] = ch
            records.append(rec)
    texts = [r['text'] for r in records]
    if not texts:
        return 0
    # se meta contém sentinel TF-IDF, vamos usar esse estado
    _, meta = _load_index_and_meta()
    tfidf_state = {}
    if meta and isinstance(meta[0], dict) and meta[0].get('_tfidf_state'):
        tfidf_state = meta[0]['_tfidf_state'] or {}
    try:
        vecs = _encode_texts(texts, tfidf_fit=not bool(tfidf_state), tfidf_state=tfidf_state)
        # se recém ajustamos, prepend sentinel
        if tfidf_state and not (meta and meta[0].get('_tfidf_state')):
            meta = [{'_tfidf_state': tfidf_state}] + (meta or [])
    except Exception:
        vecs = _encode_texts(texts)
    index, meta = _load_index_and_meta()
    if index is None:
        # criar novo índice
        faiss = _load_faiss(); hnsw = _load_hnsw()
        if faiss is not None:
            index = faiss.IndexFlatIP(vecs.shape[1])
            index.add(vecs)
        elif hnsw is not None:
            p = hnsw.Index(space='cosine', dim=vecs.shape[1])
            p.init_index(max_elements=vecs.shape[0], ef_construction=200, M=48)
            p.add_items(vecs)
            p.set_ef(200)
            index = p
            meta = [{'_hnsw_dim': vecs.shape[1]}]
        else:
            import numpy as np
            index = np.concatenate([np.zeros((0, vecs.shape[1]), dtype='float32'), vecs], axis=0)
            meta = []
    else:
        # Adicionar a um índice existente
        try:
            # FAISS
            if hasattr(index, 'add') and hasattr(index, 'ntotal'):
                index.add(vecs)
            # HNSW
            elif hasattr(index, 'add_items') and hasattr(index, 'get_max_elements'):
                cur = index.get_current_count()
                cap = index.get_max_elements()
                need = cur + vecs.shape[0]
                if need > cap:
                    index.resize_index(need)
                index.add_items(vecs)
                index.set_ef(200)
            else:
                # NumPy fallback
                import numpy as np
                index = np.concatenate([index, vecs], axis=0)
        except Exception:
            # fallback de segurança
            import numpy as np
            index = np.concatenate([index, vecs], axis=0)
    # Atenção: manter a mesma ordem
    # Garante sentinels no topo (TF-IDF, HNSW)
    sentinels = []
    if meta and isinstance(meta[0], dict) and (meta[0].get('_tfidf_state') or meta[0].get('_hnsw_dim')):
        sentinels.append(meta[0])
        meta = meta[1:]
    meta = (sentinels or []) + meta + records
    _save_index_and_meta(index, meta)
    return len(texts)


def ingest_docs(docs: List[Dict]) -> int:
    """Ingestão incremental. docs: [{title, text, url, source, id}]"""
    # saneamento mínimo
    clean = []
    for d in docs:
        t = (d.get('text') or '').strip()
        if not t:
            continue
        clean.append({
            'source': d.get('source') or 'ext',
            'id': d.get('id'),
            'title': d.get('title') or '',
            'url': d.get('url') or '',
            'text': t,
            'tag': d.get('tag') or ''
        })
    return _append_to_index(clean)


def index_exists() -> bool:
    # Existe índice FAISS ou fallback NumPy + meta
    has_faiss = os.path.exists(_instance_path(_INDEX_FILE)) and os.path.exists(_instance_path(_META_FILE))
    has_npy = os.path.exists(_instance_path('rag_index.npy')) and os.path.exists(_instance_path(_META_FILE))
    return has_faiss or has_npy


def search_similar(query: str, k: int = 5) -> List[Dict]:
    index, meta = _load_index_and_meta()
    if index is None or not meta:
        return []
    # TF-IDF sentinel
    tfidf_state = {}
    if meta and isinstance(meta[0], dict) and meta[0].get('_tfidf_state'):
        tfidf_state = meta[0]['_tfidf_state'] or {}
        meta = meta[1:]
    # HNSW sentinel
    if meta and isinstance(meta[0], dict) and meta[0].get('_hnsw_dim'):
        # não precisamos fazer nada além de pular
        meta = meta[1:]
    vec = _encode_texts([query])  # (1, d)
    import numpy as np
    out: List[Dict] = []
    if hasattr(index, 'search'):
        D, I = index.search(vec, min(k, len(meta)))  # I: índices; D: similaridades
        pairs = list(zip(I[0].tolist(), D[0].tolist()))
    elif hasattr(index, 'knn_query'):
        # HNSW
        labels, distances = index.knn_query(vec, k=min(k, len(meta)))
        pairs = list(zip(labels[0].tolist(), (1.0 - distances[0]).tolist()))  # cosine -> proximidade
    else:
        # NumPy fallback: produto interno (cos sim, pois vetores normalizados)
        sims = index @ vec.T  # (N,1)
        sims = sims.reshape(-1)
        topk = min(k, sims.shape[0])
        idxs = np.argpartition(-sims, topk-1)[:topk]
        # Ordena por similaridade desc
        idxs = idxs[np.argsort(-sims[idxs])]
        pairs = [(int(i), float(sims[int(i)])) for i in idxs]
    for idx, score in pairs:
        if idx < 0 or idx >= len(meta):
            continue
        m = meta[idx]
        out.append({
            'title': m.get('title') or '(sem título)',
            'url': m.get('url') or '',
            'text': (m.get('text') or '')[:800].strip(),
            'score': float(score),
            'source': m.get('source') or 'ext',
            'tag': m.get('tag') or ''
        })
    return out


def get_index_stats() -> Dict:
    """Retorna estatísticas do índice atual: backend, dimensão, número de chunks e tag hints."""
    index, meta = _load_index_and_meta()
    stats = {'backend': 'none', 'dim': 0, 'chunks': 0}
    if index is None or not meta:
        return stats
    # pular sentinels para contar chunks
    mm = list(meta)
    if mm and isinstance(mm[0], dict) and (mm[0].get('_tfidf_state') or mm[0].get('_hnsw_dim')):
        mm = mm[1:]
    stats['chunks'] = len(mm)
    # Backend
    if hasattr(index, 'ntotal'):
        stats['backend'] = 'faiss'
        try:
            stats['dim'] = index.d
        except Exception:
            stats['dim'] = 0
    elif hasattr(index, 'get_current_count'):
        stats['backend'] = 'hnsw'
        try:
            stats['chunks'] = index.get_current_count()
        except Exception:
            pass
        # dimensão vem do sentinel
        if meta and isinstance(meta[0], dict) and meta[0].get('_hnsw_dim'):
            stats['dim'] = int(meta[0]['_hnsw_dim'])
    else:
        stats['backend'] = 'numpy'
        try:
            import numpy as np  # type: ignore
            stats['chunks'] = int(getattr(index, 'shape', [0, 0])[0])
            stats['dim'] = int(getattr(index, 'shape', [0, 0])[1])
        except Exception:
            pass
    return stats
