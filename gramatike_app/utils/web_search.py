from typing import Optional, Tuple, List, Dict
from .web_cache import get as cache_get, set as cache_set

# Lazy import for requests - may not be available in Pyodide
_requests = None

def _get_requests():
    global _requests
    if _requests is None:
        try:
            import requests
            _requests = requests
        except ImportError:
            _requests = False
    return _requests if _requests else None

def wiki_search_summary(term: str, lang: str = 'pt') -> Optional[Tuple[str, str, str]]:
    """
    Busca um resumo curto na Wikipedia para o termo informado.
    Retorna (title, extract, url) ou None se não encontrado.
    """
    try:
        requests = _get_requests()
        if requests is None:
            return None
        ck = f"wiki:{lang}:{term.strip().lower()}"
        cached = cache_get(ck)
        if cached:
            return tuple(cached)
        s = term.strip()
        if not s:
            return None
        base = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/"
        # Wikipedia summary espera o título com espaços como underscores
        import urllib.parse
        url = base + urllib.parse.quote(s.replace(' ', '_'))
        r = requests.get(url, timeout=12)
        if not r.ok:
            return None
        j = r.json()
        extract = (j.get('extract') or '').strip()
        title = (j.get('title') or s).strip()
        page_url = (j.get('content_urls', {}).get('desktop', {}).get('page') or f"https://{lang}.wikipedia.org/wiki/" + urllib.parse.quote(title.replace(' ', '_')))
        if extract:
            val = (title, extract, page_url)
            cache_set(ck, val, ttl_seconds=600)
            return val
    except Exception:
        return None
    return None


def crossref_search_works(query: str, rows: int = 3) -> List[Dict]:
    """Pesquisa títulos/artigos no Crossref e retorna uma lista de citações simples.
    Cada item: { 'title': str, 'year': int|None, 'doi': str|None, 'url': str|None, 'source': 'Crossref' }
    """
    try:
        requests = _get_requests()
        if requests is None:
            return []
        ck = f"crossref:{query.strip().lower()}:{rows}"
        cached = cache_get(ck)
        if cached:
            return cached
        params = {
            'query': query,
            'rows': max(1, min(rows, 10))
        }
        r = requests.get('https://api.crossref.org/works', params=params, timeout=12)
        if not r.ok:
            return []
        j = r.json()
        items = (j.get('message', {}).get('items') or [])[:rows]
        out = []
        for it in items:
            title = ' / '.join(it.get('title') or []) or (it.get('container-title') or [''])[0]
            year = None
            if it.get('issued', {}).get('date-parts'):
                try:
                    year = int(it['issued']['date-parts'][0][0])
                except Exception:
                    year = None
            out.append({
                'title': (title or '').strip(),
                'year': year,
                'doi': it.get('DOI'),
                'url': (it.get('URL') or (('https://doi.org/' + it.get('DOI')) if it.get('DOI') else None)),
                'source': 'Crossref'
            })
        cache_set(ck, out, ttl_seconds=600)
        return out
    except Exception:
        return []


def arxiv_search(query: str, max_results: int = 3) -> List[Dict]:
    """Pesquisa no arXiv e retorna lista com título, ano e link do PDF.
    Cada item: { 'title': str, 'year': int|None, 'url': str, 'source': 'arXiv' }
    """
    try:
        ck = f"arxiv:{query.strip().lower()}:{max_results}"
        cached = cache_get(ck)
        if cached:
            return cached
        import importlib
        feedparser = importlib.import_module('feedparser')  # carregamento dinâmico
        import urllib.parse
        q = urllib.parse.quote(query)
        url = f'http://export.arxiv.org/api/query?search_query=all:{q}&start=0&max_results={max(1, min(max_results, 10))}'
        d = feedparser.parse(url)
        out = []
        for e in d.entries[:max_results]:
            title = (e.title or '').strip()
            year = None
            if getattr(e, 'published', None):
                try:
                    year = int(e.published[:4])
                except Exception:
                    year = None
            link = e.link
            # tenta PDF
            pdf = None
            for l in getattr(e, 'links', []):
                if l.get('type') == 'application/pdf':
                    pdf = l.get('href'); break
            out.append({'title': title, 'year': year, 'url': pdf or link, 'source': 'arXiv'})
        cache_set(ck, out, ttl_seconds=600)
        return out
    except Exception:
        return []


def pubmed_search(query: str, retmax: int = 3) -> List[Dict]:
    """Pesquisa no PubMed (E-utilities) e retorna itens com título, ano e URL.
    Cada item: { 'title': str, 'year': int|None, 'url': str, 'source': 'PubMed' }
    """
    try:
        requests = _get_requests()
        if requests is None:
            return []
        ck = f"pubmed:{query.strip().lower()}:{retmax}"
        cached = cache_get(ck)
        if cached:
            return cached
        import urllib.parse, xml.etree.ElementTree as ET
        q = urllib.parse.quote(query)
        # Busca IDs
        esearch = f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmax={max(1, min(retmax, 10))}&term={q}'
        r = requests.get(esearch, timeout=12)
        if not r.ok:
            return []
        root = ET.fromstring(r.text)
        ids = [el.text for el in root.findall('.//IdList/Id')][:retmax]
        if not ids:
            return []
        # Buscar detalhes
        ids_str = ','.join(ids)
        efetch = f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={ids_str}&retmode=xml'
        rr = requests.get(efetch, timeout=12)
        if not rr.ok:
            return []
        rroot = ET.fromstring(rr.text)
        out = []
        for art in rroot.findall('.//PubmedArticle'):
            title_el = art.find('.//ArticleTitle')
            title = (title_el.text if title_el is not None else '').strip()
            year = None
            yel = art.find('.//JournalIssue/PubDate/Year')
            if yel is not None and yel.text and yel.text.isdigit():
                try:
                    year = int(yel.text)
                except Exception:
                    year = None
            pmid_el = art.find('.//PMID')
            pmid = pmid_el.text if pmid_el is not None else None
            url = f'https://pubmed.ncbi.nlm.nih.gov/{pmid}/' if pmid else None
            out.append({'title': title, 'year': year, 'url': url, 'source': 'PubMed'})
        out = out[:retmax]
        cache_set(ck, out, ttl_seconds=600)
        return out
    except Exception:
        return []

