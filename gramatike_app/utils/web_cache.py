import os, json, time
from typing import Any, Optional

CACHE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'app_web_cache.json')

def _ensure_dir(path: str):
    d = os.path.dirname(path)
    if not os.path.exists(d):
        os.makedirs(d, exist_ok=True)

def _load() -> dict:
    try:
        with open(CACHE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f) or {}
    except Exception:
        return {}

def _save(data: dict):
    _ensure_dir(CACHE_PATH)
    with open(CACHE_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)

def get(key: str) -> Optional[Any]:
    data = _load()
    item = data.get(key)
    if not item:
        return None
    expires = item.get('expires_at')
    if expires is not None and time.time() > float(expires):
        # expired; purge lazily
        try:
            data.pop(key, None)
            _save(data)
        except Exception:
            pass
        return None
    return item.get('value')

def set(key: str, value: Any, ttl_seconds: int = 600):
    data = _load()
    data[key] = {
        'value': value,
        'expires_at': (time.time() + max(1, int(ttl_seconds)))
    }
    _save(data)
