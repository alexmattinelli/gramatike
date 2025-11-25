#!/usr/bin/env python3
"""
Script de Diagnóstico para Problemas com Imagens no Gramátike

Este script verifica:
1. Configuração de variáveis de ambiente do Cloudflare R2
2. Conectividade com o Cloudflare R2 Storage
3. Permissões de upload
4. Permissões de leitura pública
5. URLs geradas corretamente

Uso:
    python diagnose_images.py
"""

import os
import sys
import hashlib
import hmac
from datetime import datetime, timezone
from typing import Optional, Tuple
from urllib.parse import urlparse, quote

def print_header(text: str):
    """Imprime um cabeçalho formatado"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_success(text: str):
    """Imprime mensagem de sucesso"""
    print(f"✅ {text}")

def print_error(text: str):
    """Imprime mensagem de erro"""
    print(f"❌ {text}")

def print_warning(text: str):
    """Imprime mensagem de aviso"""
    print(f"⚠️  {text}")

def print_info(text: str):
    """Imprime mensagem informativa"""
    print(f"ℹ️  {text}")

def check_env_vars() -> Tuple[bool, dict]:
    """Verifica se as variáveis de ambiente necessárias estão configuradas"""
    print_header("1. Verificando Variáveis de Ambiente")
    
    required_vars = {
        'CLOUDFLARE_ACCOUNT_ID': None,
        'CLOUDFLARE_R2_ACCESS_KEY_ID': None,
        'CLOUDFLARE_R2_SECRET_ACCESS_KEY': None,
        'CLOUDFLARE_R2_BUCKET': 'gramatike',  # default
        'CLOUDFLARE_R2_PUBLIC_URL': None  # optional
    }
    
    all_present = True
    
    for var, default in required_vars.items():
        value = os.environ.get(var, default)
        if value:
            masked_value = value[:20] + "..." if len(value) > 20 else value
            print_success(f"{var} está configurada: {masked_value}")
            required_vars[var] = value
        elif var == 'CLOUDFLARE_R2_PUBLIC_URL':
            print_warning(f"{var} não está configurada (opcional)")
            required_vars[var] = None
        else:
            print_error(f"{var} NÃO está configurada")
            all_present = False
    
    if not all_present:
        print_error("\nAlgumas variáveis de ambiente estão faltando!")
        print_info("Configure-as no arquivo .env ou como variáveis de ambiente do sistema")
        print_info("Veja CLOUDFLARE_R2_SETUP.md para instruções detalhadas")
        return False, required_vars
    
    print_success("\nTodas as variáveis de ambiente obrigatórias estão configuradas!")
    return True, required_vars

def check_imports() -> bool:
    """Verifica se as bibliotecas necessárias estão instaladas"""
    print_header("2. Verificando Dependências")
    
    try:
        import requests
        print_success("requests instalado")
        return True
    except ImportError:
        print_error("requests não está instalado")
        print_info("Execute: pip install requests")
        return False

def _sign_aws4(method: str, url: str, headers: dict, payload: bytes,
               access_key: str, secret_key: str, region: str = 'auto',
               service: str = 's3') -> dict:
    """Gera assinatura AWS Signature Version 4 para requests ao R2."""
    parsed = urlparse(url)
    host = parsed.netloc
    path = parsed.path or '/'

    t = datetime.now(timezone.utc)
    amz_date = t.strftime('%Y%m%dT%H%M%SZ')
    date_stamp = t.strftime('%Y%m%d')

    canonical_uri = quote(path, safe='/')
    canonical_querystring = ''

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

    algorithm = 'AWS4-HMAC-SHA256'
    credential_scope = f"{date_stamp}/{region}/{service}/aws4_request"
    string_to_sign = (
        f"{algorithm}\n"
        f"{amz_date}\n"
        f"{credential_scope}\n"
        f"{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"
    )

    def sign(key: bytes, msg: str) -> bytes:
        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

    k_date = sign(('AWS4' + secret_key).encode('utf-8'), date_stamp)
    k_region = sign(k_date, region)
    k_service = sign(k_region, service)
    k_signing = sign(k_service, 'aws4_request')

    signature = hmac.new(k_signing, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

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

def test_r2_connection(config: dict) -> bool:
    """Testa conectividade básica com Cloudflare R2"""
    print_header("3. Testando Conexão com Cloudflare R2")
    
    try:
        import requests
        
        account_id = config['CLOUDFLARE_ACCOUNT_ID']
        access_key = config['CLOUDFLARE_R2_ACCESS_KEY_ID']
        secret_key = config['CLOUDFLARE_R2_SECRET_ACCESS_KEY']
        bucket = config['CLOUDFLARE_R2_BUCKET']
        
        if not all([account_id, access_key, secret_key, bucket]):
            print_error("Configuração incompleta")
            return False
        
        # Tenta listar objetos no bucket (HEAD request)
        url = f"https://{account_id}.r2.cloudflarestorage.com/{bucket}"
        
        headers = {}
        auth_headers = _sign_aws4(
            method='HEAD',
            url=url,
            headers=headers,
            payload=b'',
            access_key=access_key,
            secret_key=secret_key
        )
        headers.update(auth_headers)
        
        response = requests.head(url, headers=headers, timeout=10)
        
        if response.status_code in (200, 404):  # 404 is ok, bucket exists but empty
            print_success(f"Conexão com Cloudflare R2 estabelecida")
            print_info(f"Account ID: {account_id}")
            print_info(f"Bucket: {bucket}")
            return True
        elif response.status_code == 403:
            print_error(f"Erro de autenticação: Status {response.status_code}")
            print_info("Verifique CLOUDFLARE_R2_ACCESS_KEY_ID e CLOUDFLARE_R2_SECRET_ACCESS_KEY")
            return False
        else:
            print_error(f"Erro ao conectar: Status {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print_error("Timeout ao conectar com Cloudflare R2")
        print_info("Verifique sua conexão com a internet")
        return False
    except Exception as e:
        print_error(f"Erro ao testar conexão: {e}")
        return False

def test_upload_permission(config: dict) -> Tuple[bool, Optional[str]]:
    """Testa se é possível fazer upload de arquivos"""
    print_header("4. Testando Permissões de Upload")
    
    try:
        import requests
        
        account_id = config['CLOUDFLARE_ACCOUNT_ID']
        access_key = config['CLOUDFLARE_R2_ACCESS_KEY_ID']
        secret_key = config['CLOUDFLARE_R2_SECRET_ACCESS_KEY']
        bucket = config['CLOUDFLARE_R2_BUCKET']
        public_url_base = config.get('CLOUDFLARE_R2_PUBLIC_URL')
        
        # Cria uma imagem de teste (1x1 pixel PNG)
        test_image = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        
        # Tenta fazer upload
        test_path = 'test_diagnostic_image.png'
        url = f"https://{account_id}.r2.cloudflarestorage.com/{bucket}/{test_path}"
        
        headers = {'Content-Type': 'image/png'}
        auth_headers = _sign_aws4(
            method='PUT',
            url=url,
            headers=headers,
            payload=test_image,
            access_key=access_key,
            secret_key=secret_key
        )
        headers.update(auth_headers)
        
        response = requests.put(url, headers=headers, data=test_image, timeout=20)
        
        if response.status_code in (200, 201):
            print_success("Upload de teste realizado com sucesso!")
            
            # Gera URL pública
            if public_url_base:
                public_url = f"{public_url_base.rstrip('/')}/{test_path}"
            else:
                public_url = f"https://pub-{account_id}.r2.dev/{bucket}/{test_path}"
            
            print_info(f"URL pública gerada: {public_url}")
            return True, public_url
        else:
            print_error(f"Falha no upload: Status {response.status_code}")
            print_info(f"Resposta: {response.text[:300]}")
            
            if response.status_code == 404:
                print_warning(f"Bucket '{bucket}' não existe. Crie-o no painel do Cloudflare.")
            elif response.status_code in (401, 403):
                print_warning("Verifique se as credenciais R2 estão corretas")
            
            return False, None
            
    except Exception as e:
        print_error(f"Erro ao testar upload: {e}")
        return False, None

def test_public_access(public_url: str) -> bool:
    """Testa se a imagem pode ser acessada publicamente"""
    print_header("5. Testando Acesso Público às Imagens")
    
    if not public_url:
        print_error("URL pública não disponível (upload falhou)")
        return False
    
    try:
        import requests
        
        # Tenta acessar a imagem publicamente (sem autenticação)
        response = requests.get(public_url, timeout=10)
        
        if response.status_code == 200:
            print_success("Imagem acessível publicamente!")
            print_info(f"URL testada: {public_url}")
            print_info(f"Tamanho da resposta: {len(response.content)} bytes")
            return True
        elif response.status_code == 404:
            print_error("Imagem não encontrada (404)")
            print_warning("Upload pode ter falhado ou path incorreto")
            return False
        elif response.status_code in (401, 403):
            print_error("Acesso negado (403/401)")
            print_warning("Bucket não está configurado para acesso público!")
            print_info("Soluções:")
            print_info("  1. No Cloudflare R2, vá em Settings do bucket")
            print_info("  2. Habilite 'R2.dev subdomain' para acesso público")
            print_info("  3. Ou configure um domínio personalizado")
            print_info("\nVeja CLOUDFLARE_R2_SETUP.md para instruções detalhadas")
            return False
        else:
            print_error(f"Erro ao acessar: Status {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Erro ao testar acesso público: {e}")
        return False

def cleanup_test_image(config: dict):
    """Remove a imagem de teste após os testes"""
    print_header("6. Limpando Arquivos de Teste")
    
    try:
        import requests
        
        account_id = config['CLOUDFLARE_ACCOUNT_ID']
        access_key = config['CLOUDFLARE_R2_ACCESS_KEY_ID']
        secret_key = config['CLOUDFLARE_R2_SECRET_ACCESS_KEY']
        bucket = config['CLOUDFLARE_R2_BUCKET']
        
        test_path = 'test_diagnostic_image.png'
        url = f"https://{account_id}.r2.cloudflarestorage.com/{bucket}/{test_path}"
        
        headers = {}
        auth_headers = _sign_aws4(
            method='DELETE',
            url=url,
            headers=headers,
            payload=b'',
            access_key=access_key,
            secret_key=secret_key
        )
        headers.update(auth_headers)
        
        response = requests.delete(url, headers=headers, timeout=10)
        
        if response.status_code in (200, 204):
            print_success("Imagem de teste removida")
        else:
            print_warning(f"Não foi possível remover a imagem de teste (Status {response.status_code})")
            print_info("Você pode removê-la manualmente no painel do Cloudflare")
            
    except Exception as e:
        print_warning(f"Erro ao limpar: {e}")
        print_info("Você pode remover test_diagnostic_image.png manualmente no Cloudflare R2")

def print_summary(results: dict):
    """Imprime um resumo dos testes"""
    print_header("RESUMO DOS TESTES")
    
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    
    print(f"\nTestes realizados: {total}")
    print(f"Sucesso: {passed}")
    print(f"Falhas: {total - passed}")
    
    if passed == total:
        print_success("\n🎉 Todos os testes passaram! Suas imagens devem funcionar corretamente.")
        print_info("\nSe ainda tiver problemas:")
        print_info("  1. Certifique-se de que a aplicação está usando as mesmas variáveis de ambiente")
        print_info("  2. No Cloudflare Pages, faça um novo deploy após configurar as variáveis")
        print_info("  3. Verifique os logs da aplicação para erros específicos")
    else:
        print_error("\n⚠️  Alguns testes falharam. Revise os erros acima.")
        print_info("\nPróximos passos:")
        print_info("  1. Leia o arquivo CLOUDFLARE_R2_SETUP.md")
        print_info("  2. Configure corretamente o bucket no Cloudflare R2")
        print_info("  3. Execute este script novamente")

def main():
    """Função principal"""
    print_header("DIAGNÓSTICO DE IMAGENS DO GRAMÁTIKE")
    print_info("Este script verifica a configuração do Cloudflare R2 Storage")
    
    results = {}
    
    # 1. Verificar variáveis de ambiente
    env_ok, config = check_env_vars()
    results['env_vars'] = env_ok
    
    if not env_ok:
        print_summary(results)
        return 1
    
    # 2. Verificar dependências
    deps_ok = check_imports()
    results['dependencies'] = deps_ok
    
    if not deps_ok:
        print_summary(results)
        return 1
    
    # 3. Testar conexão
    connection_ok = test_r2_connection(config)
    results['connection'] = connection_ok
    
    if not connection_ok:
        print_summary(results)
        return 1
    
    # 4. Testar upload
    upload_ok, public_url = test_upload_permission(config)
    results['upload'] = upload_ok
    
    # 5. Testar acesso público
    if upload_ok and public_url:
        access_ok = test_public_access(public_url)
        results['public_access'] = access_ok
        
        # 6. Limpar
        cleanup_test_image(config)
    else:
        results['public_access'] = False
    
    # Resumo
    print_summary(results)
    
    return 0 if all(results.values()) else 1

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nTestes interrompidos pelo usuário")
        sys.exit(1)
    except Exception as e:
        print_error(f"\nErro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
