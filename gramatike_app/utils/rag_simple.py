from typing import List, Dict, Tuple
from sqlalchemy import or_
from gramatike_app.models import db, EduContent


def _score_text(q: str, title: str = '', resumo: str = '', corpo: str = '', extract: str = '') -> int:
    ql = (q or '').lower()
    score = 0
    for field in (title or '', resumo or '', corpo or '', extract or ''):
        fl = (field or '').lower()
        if not fl:
            continue
        if ql in fl:
            score += 5
        # contagem simples de termos por espaço
        for tok in [t for t in ql.split() if len(t) > 2]:
            if tok in fl:
                score += 1
    return score


def retrieve_context(query: str, limit: int = 4) -> Tuple[List[Dict], List[str]]:
    """Busca trechos relevantes de EduContent.
    Retorna (items, sources) onde items tem: title, url, text, source.
    """
    items: List[Dict] = []
    sources: List[str] = []
    q = (query or '').strip()
    if not q:
        return items, sources

    like = f"%{q}%"

    # EduContent (titulo, resumo, corpo)
    try:
        ec_rows = (EduContent.query
                   .filter(or_(EduContent.titulo.ilike(like), EduContent.resumo.ilike(like), EduContent.corpo.ilike(like)))
                   .order_by(EduContent.created_at.desc())
                   .limit(50)
                   .all())
    except Exception:
        ec_rows = []

    for r in ec_rows:
        text = (r.resumo or '')
        if not text:
            text = (r.corpo or '')[:600]
        sc = _score_text(q, title=r.titulo or '', resumo=r.resumo or '', corpo=r.corpo or '')
        items.append({
            'title': r.titulo or '(sem título)',
            'url': r.url or '',
            'text': (text or '').strip(),
            'score': sc,
            'source': 'EduContent'
        })

    # Removido: LuneKnowledge

    # Ordena por score e frescor aproximado (já usamos created_at/last_seen_at nas queries)
    items.sort(key=lambda x: x.get('score', 0), reverse=True)
    items = items[:max(1, min(limit, 6))]

    # Coleta fontes deduplicadas
    seen = set()
    for it in items:
        u = (it.get('url') or '').strip()
        if u and u not in seen:
            sources.append(u)
            seen.add(u)

    return items, sources
