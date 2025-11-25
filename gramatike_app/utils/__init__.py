# Utility functions for gramatike_app

# Lazy import cache for libraries that may not be available in Pyodide/serverless
_lazy_imports = {}


def get_requests():
    """Lazily import requests library. Returns None if not available (e.g., in Pyodide)."""
    if 'requests' not in _lazy_imports:
        try:
            import requests
            _lazy_imports['requests'] = requests
        except ImportError:
            _lazy_imports['requests'] = None
    return _lazy_imports['requests']


def get_pil():
    """Lazily import PIL Image. Returns None if not available (e.g., in Pyodide)."""
    if 'PIL' not in _lazy_imports:
        try:
            from PIL import Image
            _lazy_imports['PIL'] = Image
        except ImportError:
            _lazy_imports['PIL'] = None
    return _lazy_imports['PIL']


def get_bs4():
    """Lazily import BeautifulSoup. Returns None if not available (e.g., in Pyodide)."""
    if 'bs4' not in _lazy_imports:
        try:
            from bs4 import BeautifulSoup
            _lazy_imports['bs4'] = BeautifulSoup
        except ImportError:
            _lazy_imports['bs4'] = None
    return _lazy_imports['bs4']
