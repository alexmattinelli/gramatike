import os
import time
import logging
from typing import Optional

import requests

# Configurar logger
logger = logging.getLogger(__name__)


def _env(name: str, default: Optional[str] = None) -> Optional[str]:
    try:
        return os.environ.get(name, default)
    except Exception:
        return default


def is_supabase_configured() -> bool:
    """
    Verifica se as variáveis de ambiente do Supabase estão configuradas.
    Retorna True se todas as variáveis necessárias estiverem presentes.
    """
    base_url = _env('SUPABASE_URL')
    service_key = _env('SUPABASE_SERVICE_ROLE_KEY')
    bucket = _env('SUPABASE_BUCKET', 'avatars')
    return bool(base_url and service_key and bucket)


def upload_bytes_to_supabase(path: str, data: bytes, content_type: Optional[str] = None) -> Optional[str]:
    """
    Envia bytes para o Supabase Storage no caminho informado e retorna a URL pública.
    Requer SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY e SUPABASE_BUCKET (padrão: 'avatars').
    
    Args:
        path: Caminho do arquivo no bucket (ex: 'posts/1/12345_image.jpg')
        data: Bytes do arquivo a ser enviado
        content_type: MIME type do arquivo (ex: 'image/jpeg')
    
    Returns:
        URL pública do arquivo se upload for bem-sucedido, None caso contrário
    
    Nota: Se retornar None, o bucket pode não estar configurado para acesso público.
          Veja SUPABASE_BUCKET_SETUP.md para instruções de configuração.
    """
    base_url = _env('SUPABASE_URL')
    service_key = _env('SUPABASE_SERVICE_ROLE_KEY')
    bucket = _env('SUPABASE_BUCKET', 'avatars')
    
    if not (base_url and service_key and bucket):
        logger.warning("Supabase não configurado: variáveis de ambiente faltando")
        logger.warning("Configure SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY e SUPABASE_BUCKET")
        logger.warning("Veja SUPABASE_BUCKET_SETUP.md para instruções")
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
        
        logger.info(f"Uploading to Supabase: {path} ({len(data)} bytes)")
        resp = requests.put(url, headers=headers, data=data, timeout=20)
        
        if resp.status_code in (200, 201):
            # URL pública padrão (requer bucket com política pública)
            public_url = base_url.rstrip('/') + f"/storage/v1/object/public/{bucket}/{path.lstrip('/')}"
            logger.info(f"Upload successful: {public_url}")
            return public_url
        else:
            logger.error(f"Upload failed: HTTP {resp.status_code}")
            logger.error(f"Response: {resp.text[:500]}")
            
            # Mensagens de ajuda específicas por código de erro
            if resp.status_code == 404:
                logger.error(f"Bucket '{bucket}' não encontrado. Crie-o no painel do Supabase.")
            elif resp.status_code in (401, 403):
                logger.error("Erro de autenticação. Verifique SUPABASE_SERVICE_ROLE_KEY.")
            
            return None
            
    except requests.exceptions.Timeout:
        logger.error("Timeout ao fazer upload para Supabase")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro de rede ao fazer upload: {e}")
        return None
    except Exception as e:
        logger.error(f"Erro inesperado ao fazer upload: {e}")
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


def build_dinamica_image_path(user_id: int, filename: str) -> str:
    """
    Gera um caminho de upload para imagens de dinâmicas: dinamicas/<user_id>/<timestamp>_<filename>
    """
    ts = int(time.time())
    safe_name = filename.replace(' ', '_')
    return f"dinamicas/{user_id}/{ts}_{safe_name}"
