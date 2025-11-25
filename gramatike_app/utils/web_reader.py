from urllib.parse import urlparse

# Lazy import for requests and BeautifulSoup - may not be available in Pyodide
_requests = None
_bs4 = None

def _get_requests():
    global _requests
    if _requests is None:
        try:
            import requests
            _requests = requests
        except ImportError:
            _requests = False
    return _requests if _requests else None

def _get_bs4():
    global _bs4
    if _bs4 is None:
        try:
            from bs4 import BeautifulSoup
            _bs4 = BeautifulSoup
        except ImportError:
            _bs4 = False
    return _bs4 if _bs4 else None

def is_allowed(url: str, allowed_domains: list[str]) -> bool:
    try:
        host = (urlparse(url).hostname or '').lower()
        if not host:
            return False
        for d in allowed_domains or []:
            dom = (d or '').lower().lstrip('.')
            if not dom:
                continue
            if host == dom or host.endswith('.'+dom) or host.endswith(dom):
                return True
        return False
    except Exception:
        return False

def fetch_page_text(url: str, max_chars: int = 10000) -> str:
    requests = _get_requests()
    BeautifulSoup = _get_bs4()
    if requests is None or BeautifulSoup is None:
        return ""  # Return empty string if dependencies not available
    r = requests.get(url, timeout=15, headers={'User-Agent': 'GramatikeBot/1.0'})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')
    # Remove scripts/styles/nav
    for tag in soup(['script','style','nav','header','footer','noscript']):
        tag.decompose()
    text = ' '.join(soup.stripped_strings)
    return text[:max_chars]
