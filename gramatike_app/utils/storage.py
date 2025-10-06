import os
import time
from typing import Optional

import requests


def _env(name: str, default: Optional[str] = None) -> Optional[str]:
    try:
        return os.environ.get(name, default)
    except Exception:
        return default


def upload_bytes_to_supabase(path: str, data: bytes, content_type: Optional[str] = None) -> Optional[str]:
    """
    Envia bytes para o Supabase Storage no caminho informado e retorna a URL pública.
    Requer SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY e SUPABASE_BUCKET (padrão: 'avatars').
    """
    base_url = _env('SUPABASE_URL')
    service_key = _env('SUPABASE_SERVICE_ROLE_KEY')
    bucket = _env('SUPABASE_BUCKET', 'avatars')
    if not (base_url and service_key and bucket):
        return None
    try:
        # Ex.: https://<project>.supabase.co/storage/v1/object/<bucket>/<path>
        # Setar x-upsert para substituir/atualizar sem erro
        url = base_url.rstrip('/') + f"/storage/v1/object/{bucket}/{path.lstrip('/')}"
        headers = {
            'Authorization': f'Bearer {service_key}',
            'apikey': service_key,
            'x-upsert': 'true',
        }
        if content_type:
            headers['Content-Type'] = content_type
        resp = requests.put(url, headers=headers, data=data, timeout=20)
        if resp.status_code in (200, 201):
            # URL pública padrão (requer bucket com política pública)
            public_url = base_url.rstrip('/') + f"/storage/v1/object/public/{bucket}/{path.lstrip('/')}"
            return public_url
        # Alguns projetos retornam 200 com body vazio; se não for 2xx, falha
        return None
    except Exception:
        return None


def build_avatar_path(user_id: int, filename: str) -> str:
    """
    Gera um caminho de upload estável para avatares: avatars/<user_id>/<timestamp>_<filename>
    (a pasta 'avatars' aqui é apenas parte do path; o bucket é SUPABASE_BUCKET)
    """
    ts = int(time.time())
    safe_name = filename.replace(' ', '_')
    return f"avatars/{user_id}/{ts}_{safe_name}"


def build_post_image_path(user_id: int, filename: str) -> str:
    """
    Gera um caminho de upload para imagens de posts: posts/<user_id>/<timestamp>_<filename>
    """
    ts = int(time.time())
    safe_name = filename.replace(' ', '_')
    return f"posts/{user_id}/{ts}_{safe_name}"


def build_apostila_path(filename: str) -> str:
    """
    Gera um caminho de upload para apostilas (PDFs): apostilas/<timestamp>_<filename>
    """
    ts = int(time.time())
    safe_name = filename.replace(' ', '_')
    return f"apostilas/{ts}_{safe_name}"


def build_divulgacao_path(filename: str) -> str:
    """
    Gera um caminho de upload para divulgação: divulgacao/<timestamp>_<filename>
    """
    ts = int(time.time())
    safe_name = filename.replace(' ', '_')
    return f"divulgacao/{ts}_{safe_name}"
