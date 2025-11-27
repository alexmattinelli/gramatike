#!/usr/bin/env python3
"""Script para consultar usuários no D1 do Cloudflare via wrangler"""

import subprocess
import json
import sys

def run_d1_query(query):
    """Executa uma query no D1 via wrangler"""
    cmd = [
        "wrangler", "d1", "execute", "gramatike",
        "--command", query,
        "--json"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar query: {e}")
        print(f"stderr: {e.stderr}")
        return None
    except json.JSONDecodeError as e:
        print(f"Erro ao parsear JSON: {e}")
        print(f"stdout: {result.stdout}")
        return None

# Lista todos os usuários
print("=== Usuários no D1 (Cloudflare) ===\n")

result = run_d1_query("SELECT id, username, email, nome, email_confirmed, is_admin, is_banned, created_at FROM user ORDER BY created_at DESC LIMIT 10")

if result and isinstance(result, list) and len(result) > 0:
    data = result[0]
    if 'results' in data:
        users = data['results']
        print(f"Total de usuários encontrados: {len(users)}\n")
        
        for user in users:
            print(f"ID: {user.get('id')}")
            print(f"Username: {user.get('username')}")
            print(f"Email: {user.get('email')}")
            print(f"Nome: {user.get('nome', 'N/A')}")
            print(f"Email confirmado: {user.get('email_confirmed')}")
            print(f"Admin: {user.get('is_admin')}")
            print(f"Banido: {user.get('is_banned')}")
            print(f"Criado em: {user.get('created_at')}")
            print("-" * 80)
    else:
        print("Resposta inesperada do D1:", data)
else:
    print("Nenhum resultado retornado ou erro na query")

print("\n=== Para resetar senha de um usuário no D1 ===")
print("Use o script: wrangler d1 execute gramatike --command \"UPDATE user SET password='<hash>' WHERE username='<username>'\"")
print("Ou use o dashboard do Cloudflare D1")
