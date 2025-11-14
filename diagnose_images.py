#!/usr/bin/env python3
"""
Script de Diagnóstico para Problemas com Imagens no Gramátike

Este script verifica:
1. Configuração de variáveis de ambiente do Supabase
2. Conectividade com o Supabase Storage
3. Permissões de upload
4. Permissões de leitura pública
5. URLs geradas corretamente

Uso:
    python diagnose_images.py
"""

import os
import sys
import io
from typing import Optional, Tuple

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
        'SUPABASE_URL': None,
        'SUPABASE_SERVICE_ROLE_KEY': None,
        'SUPABASE_BUCKET': 'avatars'  # default
    }
    
    all_present = True
    
    for var, default in required_vars.items():
        value = os.environ.get(var, default)
        if value:
            masked_value = value[:20] + "..." if len(value) > 20 else value
            print_success(f"{var} está configurada: {masked_value}")
            required_vars[var] = value
        else:
            print_error(f"{var} NÃO está configurada")
            all_present = False
    
    if not all_present:
        print_error("\nAlgumas variáveis de ambiente estão faltando!")
        print_info("Configure-as no arquivo .env ou como variáveis de ambiente do sistema")
        print_info("Veja SUPABASE_BUCKET_SETUP.md para instruções detalhadas")
        return False, required_vars
    
    print_success("\nTodas as variáveis de ambiente estão configuradas!")
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

def test_supabase_connection(config: dict) -> bool:
    """Testa conectividade básica com Supabase"""
    print_header("3. Testando Conexão com Supabase")
    
    try:
        import requests
        
        base_url = config['SUPABASE_URL']
        service_key = config['SUPABASE_SERVICE_ROLE_KEY']
        
        if not base_url or not service_key:
            print_error("Configuração incompleta")
            return False
        
        # Tenta acessar a API do Supabase
        url = base_url.rstrip('/') + '/rest/v1/'
        headers = {
            'apikey': service_key,
            'Authorization': f'Bearer {service_key}'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print_success(f"Conexão com Supabase estabelecida: {base_url}")
            return True
        else:
            print_error(f"Erro ao conectar: Status {response.status_code}")
            print_info(f"Resposta: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print_error("Timeout ao conectar com Supabase")
        print_info("Verifique sua conexão com a internet e a URL do Supabase")
        return False
    except Exception as e:
        print_error(f"Erro ao testar conexão: {e}")
        return False

def test_upload_permission(config: dict) -> Tuple[bool, Optional[str]]:
    """Testa se é possível fazer upload de arquivos"""
    print_header("4. Testando Permissões de Upload")
    
    try:
        import requests
        
        base_url = config['SUPABASE_URL']
        service_key = config['SUPABASE_SERVICE_ROLE_KEY']
        bucket = config['SUPABASE_BUCKET']
        
        # Cria uma imagem de teste (1x1 pixel PNG)
        test_image = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        
        # Tenta fazer upload
        test_path = 'test_diagnostic_image.png'
        url = base_url.rstrip('/') + f'/storage/v1/object/{bucket}/{test_path}'
        
        headers = {
            'Authorization': f'Bearer {service_key}',
            'apikey': service_key,
            'Content-Type': 'image/png',
            'x-upsert': 'true'
        }
        
        response = requests.put(url, headers=headers, data=test_image, timeout=20)
        
        if response.status_code in (200, 201):
            print_success("Upload de teste realizado com sucesso!")
            public_url = base_url.rstrip('/') + f'/storage/v1/object/public/{bucket}/{test_path}'
            print_info(f"URL pública gerada: {public_url}")
            return True, public_url
        else:
            print_error(f"Falha no upload: Status {response.status_code}")
            print_info(f"Resposta: {response.text[:300]}")
            
            if response.status_code == 404:
                print_warning(f"Bucket '{bucket}' não existe. Crie-o no painel do Supabase.")
            elif response.status_code == 401 or response.status_code == 403:
                print_warning("Verifique se a service_role key está correta")
            
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
            print_info("  1. No Supabase, vá em Storage → seu bucket → Policies")
            print_info("  2. Crie uma política de 'SELECT' para acesso público")
            print_info("  3. Ou marque o bucket como 'Public bucket' nas configurações")
            print_info("\nVeja SUPABASE_BUCKET_SETUP.md para instruções detalhadas")
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
        
        base_url = config['SUPABASE_URL']
        service_key = config['SUPABASE_SERVICE_ROLE_KEY']
        bucket = config['SUPABASE_BUCKET']
        
        test_path = 'test_diagnostic_image.png'
        url = base_url.rstrip('/') + f'/storage/v1/object/{bucket}/{test_path}'
        
        headers = {
            'Authorization': f'Bearer {service_key}',
            'apikey': service_key
        }
        
        response = requests.delete(url, headers=headers, timeout=10)
        
        if response.status_code in (200, 204):
            print_success("Imagem de teste removida")
        else:
            print_warning(f"Não foi possível remover a imagem de teste (Status {response.status_code})")
            print_info("Você pode removê-la manualmente no painel do Supabase")
            
    except Exception as e:
        print_warning(f"Erro ao limpar: {e}")
        print_info("Você pode remover test_diagnostic_image.png manualmente no Supabase")

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
        print_info("  2. No Vercel, faça um novo deploy após configurar as variáveis")
        print_info("  3. Verifique os logs da aplicação para erros específicos")
    else:
        print_error("\n⚠️  Alguns testes falharam. Revise os erros acima.")
        print_info("\nPróximos passos:")
        print_info("  1. Leia o arquivo SUPABASE_BUCKET_SETUP.md")
        print_info("  2. Configure corretamente o bucket no Supabase")
        print_info("  3. Execute este script novamente")

def main():
    """Função principal"""
    print_header("DIAGNÓSTICO DE IMAGENS DO GRAMÁTIKE")
    print_info("Este script verifica a configuração do Supabase Storage")
    
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
    connection_ok = test_supabase_connection(config)
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
