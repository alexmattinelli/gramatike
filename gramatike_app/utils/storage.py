import os
import time
import logging
import hmac
import hashlib
from datetime import datetime, timezone
from typing import Optional

import requests

# Configurar logger
logger = logging.getLogger(__name__)


def _env(name: str, default: Optional[str] = None) -> Optional[str]:
    try:
        return os.environ.get(name, default)
    except Exception:
        return default


def is_r2_configured() -> bool:
    """
    Verifica se as variáveis de ambiente do Cloudflare R2 estão configuradas.
    Retorna True se todas as variáveis necessárias estiverem presentes.
    """
    account_id = _env('CLOUDFLARE_ACCOUNT_ID')
    access_key_id = _env('CLOUDFLARE_R2_ACCESS_KEY_ID')
    secret_access_key = _env('CLOUDFLARE_R2_SECRET_ACCESS_KEY')
    bucket = _env('CLOUDFLARE_R2_BUCKET', 'gramatike')
    return bool(account_id and access_key_id and secret_access_key and bucket)


# Alias para compatibilidade com código existente
def is_supabase_configured() -> bool:
    """
    Verifica se o storage está configurado (agora usa Cloudflare R2).
    Mantido para compatibilidade com código existente.
    """
    return is_r2_configured()


def _sign_aws4(method: str, url: str, headers: dict, payload: bytes,
               access_key: str, secret_key: str, region: str = 'auto',
               service: str = 's3') -> dict:
    """
    Gera assinatura AWS Signature Version 4 para requests ao R2.
    Cloudflare R2 é compatível com S3 API.
    """
    from urllib.parse import urlparse, quote

    parsed = urlparse(url)
    host = parsed.netloc
    path = parsed.path or '/'

    # Timestamp para a requisição
    t = datetime.now(timezone.utc)
    amz_date = t.strftime('%Y%m%dT%H%M%SZ')
    date_stamp = t.strftime('%Y%m%d')

    # Canonical request
    canonical_uri = quote(path, safe='/')
    canonical_querystring = ''

    # Headers canônicos
    signed_headers_list = ['host', 'x-amz-content-sha256', 'x-amz-date']
    if 'content-type' in {k.lower() for k in headers}:
        signed_headers_list.append('content-type')
    signed_headers_list.sort()

    payload_hash = hashlib.sha256(payload).hexdigest()

    canonical_headers_dict = {
        'host': host,
        'x-amz-content-sha256': payload_hash,
        'x-amz-date': amz_date,
    }
    for k, v in headers.items():
        if k.lower() == 'content-type':
            canonical_headers_dict['content-type'] = v

    canonical_headers = ''
    for h in signed_headers_list:
        canonical_headers += f"{h}:{canonical_headers_dict[h]}\n"

    signed_headers = ';'.join(signed_headers_list)

    canonical_request = (
        f"{method}\n"
        f"{canonical_uri}\n"
        f"{canonical_querystring}\n"
        f"{canonical_headers}\n"
        f"{signed_headers}\n"
        f"{payload_hash}"
    )

    # String to sign
    algorithm = 'AWS4-HMAC-SHA256'
    credential_scope = f"{date_stamp}/{region}/{service}/aws4_request"
    string_to_sign = (
        f"{algorithm}\n"
        f"{amz_date}\n"
        f"{credential_scope}\n"
        f"{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"
    )

    # Signing key
    def sign(key: bytes, msg: str) -> bytes:
        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

    k_date = sign(('AWS4' + secret_key).encode('utf-8'), date_stamp)
    k_region = sign(k_date, region)
    k_service = sign(k_region, service)
    k_signing = sign(k_service, 'aws4_request')

    signature = hmac.new(k_signing, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

    # Authorization header
    authorization_header = (
        f"{algorithm} "
        f"Credential={access_key}/{credential_scope}, "
        f"SignedHeaders={signed_headers}, "
        f"Signature={signature}"
    )

    return {
        'Authorization': authorization_header,
        'x-amz-date': amz_date,
        'x-amz-content-sha256': payload_hash,
    }


def upload_bytes_to_r2(path: str, data: bytes, content_type: Optional[str] = None) -> Optional[str]:
    """
    Envia bytes para o Cloudflare R2 no caminho informado e retorna a URL pública.
    Requer CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_R2_ACCESS_KEY_ID, CLOUDFLARE_R2_SECRET_ACCESS_KEY
    e CLOUDFLARE_R2_BUCKET.
    
    Args:
        path: Caminho do arquivo no bucket (ex: 'posts/1/12345_image.jpg')
        data: Bytes do arquivo a ser enviado
        content_type: MIME type do arquivo (ex: 'image/jpeg')
    
    Returns:
        URL pública do arquivo se upload for bem-sucedido, None caso contrário
    
    Nota: Se retornar None, verifique as credenciais e configuração do bucket.
          Veja CLOUDFLARE_R2_SETUP.md para instruções de configuração.
    """
    account_id = _env('CLOUDFLARE_ACCOUNT_ID')
    access_key_id = _env('CLOUDFLARE_R2_ACCESS_KEY_ID')
    secret_access_key = _env('CLOUDFLARE_R2_SECRET_ACCESS_KEY')
    bucket = _env('CLOUDFLARE_R2_BUCKET', 'gramatike')
    public_url_base = _env('CLOUDFLARE_R2_PUBLIC_URL')
    
    if not (account_id and access_key_id and secret_access_key and bucket):
        logger.warning("Cloudflare R2 não configurado: variáveis de ambiente faltando")
        logger.warning("Configure CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_R2_ACCESS_KEY_ID, CLOUDFLARE_R2_SECRET_ACCESS_KEY e CLOUDFLARE_R2_BUCKET")
        logger.warning("Veja CLOUDFLARE_R2_SETUP.md para instruções")
        return None
    
    try:
        # URL do endpoint S3 compatível do R2
        # Formato: https://<ACCOUNT_ID>.r2.cloudflarestorage.com/<bucket>/<path>
        clean_path = path.lstrip('/')
        url = f"https://{account_id}.r2.cloudflarestorage.com/{bucket}/{clean_path}"
        
        headers = {}
        if content_type:
            headers['Content-Type'] = content_type
        
        # Gera assinatura AWS4 para autenticação
        auth_headers = _sign_aws4(
            method='PUT',
            url=url,
            headers=headers,
            payload=data,
            access_key=access_key_id,
            secret_key=secret_access_key,
            region='auto',
            service='s3'
        )
        headers.update(auth_headers)
        
        logger.info(f"Uploading to Cloudflare R2: {path} ({len(data)} bytes)")
        resp = requests.put(url, headers=headers, data=data, timeout=30)
        
        if resp.status_code in (200, 201):
            # URL pública - usa domínio personalizado se configurado
            if public_url_base:
                public_url = f"{public_url_base.rstrip('/')}/{clean_path}"
            else:
                # Fallback para URL do R2 público (requer bucket público configurado)
                public_url = f"https://pub-{account_id}.r2.dev/{bucket}/{clean_path}"
            logger.info(f"Upload successful: {public_url}")
            return public_url
        else:
            logger.error(f"Upload failed: HTTP {resp.status_code}")
            logger.error(f"Response: {resp.text[:500]}")
            
            # Mensagens de ajuda específicas por código de erro
            if resp.status_code == 404:
                logger.error(f"Bucket '{bucket}' não encontrado. Crie-o no painel do Cloudflare.")
            elif resp.status_code in (401, 403):
                logger.error("Erro de autenticação. Verifique CLOUDFLARE_R2_ACCESS_KEY_ID e CLOUDFLARE_R2_SECRET_ACCESS_KEY.")
            
            return None
            
    except requests.exceptions.Timeout:
        logger.error("Timeout ao fazer upload para Cloudflare R2")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro de rede ao fazer upload: {e}")
        return None
    except Exception as e:
        logger.error(f"Erro inesperado ao fazer upload: {e}")
        return None


# Alias para compatibilidade com código existente
def upload_bytes_to_supabase(path: str, data: bytes, content_type: Optional[str] = None) -> Optional[str]:
    """
    Envia bytes para o storage (agora usa Cloudflare R2).
    Mantido para compatibilidade com código existente.
    """
    return upload_bytes_to_r2(path, data, content_type)


def build_avatar_path(user_id: int, filename: str) -> str:
    """
    Gera um caminho de upload estável para avatares: avatars/<user_id>/<timestamp>_<filename>
    (a pasta 'avatars' aqui é apenas parte do path; o bucket é CLOUDFLARE_R2_BUCKET)
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
