import os
from typing import List, Dict, Iterator, Tuple

SUPPORTED_EXT = {'.txt', '.md', '.markdown', '.pdf'}


def iter_files(root: str) -> Iterator[str]:
    for base, _, files in os.walk(root):
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in SUPPORTED_EXT:
                yield os.path.join(base, f)


def _read_text(path: str) -> str:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        try:
            with open(path, 'r', encoding='latin-1') as f:
                return f.read()
        except Exception:
            return ''


def _read_pdf(path: str) -> str:
    try:
        import fitz  # PyMuPDF
    except Exception:
        return ''
    try:
        doc = fitz.open(path)
        parts: List[str] = []
        for page in doc:
            txt = page.get_text("text") or ''
            if txt:
                parts.append(txt)
        doc.close()
        return "\n".join(parts)
    except Exception:
        return ''


def extract_text(path: str) -> Tuple[str, str]:
    """Retorna (title, text) extraídos do arquivo."""
    name = os.path.basename(path)
    title = os.path.splitext(name)[0]
    ext = os.path.splitext(name)[1].lower()
    if ext == '.pdf':
        txt = _read_pdf(path)
    else:
        txt = _read_text(path)
    return title, txt or ''


def build_docs_from_folder(folder: str, tag: str = 'local') -> List[Dict]:
    docs: List[Dict] = []
    for p in iter_files(folder):
        title, text = extract_text(p)
        if not text.strip():
            continue
        docs.append({
            'source': 'local',
            'id': None,
            'title': title,
            'url': p,
            'text': text,
            'tag': tag
        })
    return docs
