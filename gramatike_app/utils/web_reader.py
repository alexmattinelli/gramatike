from urllib.parse import urlparse

from gramatike_app.utils import get_requests, get_bs4


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
    requests = get_requests()
    BeautifulSoup = get_bs4()
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
