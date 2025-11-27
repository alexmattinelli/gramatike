#!/usr/bin/env python3
"""Script para resetar senha de usuário no D1 do Cloudflare"""

import subprocess
import sys
from werkzeug.security import generate_password_hash

def run_d1_query(query):
    """Executa uma query no D1 via wrangler"""
    cmd = [
        "wrangler", "d1", "execute", "gramatike",
        "--command", query
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("✅ Query executada com sucesso!")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar query: {e}")
        print(f"stderr: {e.stderr}")
        return False

print("=== Reset de Senha no D1 (Cloudflare) ===\n")

username = input("Digite o username do usuário: ").strip()
if not username:
    print("❌ Username não pode estar vazio!")
    sys.exit(1)

nova_senha = input("Digite a nova senha: ").strip()
if len(nova_senha) < 6:
    print("❌ Senha muito curta! Mínimo 6 caracteres.")
    sys.exit(1)

# Gera o hash da senha
password_hash = generate_password_hash(nova_senha)
print(f"\n🔐 Hash gerado: {password_hash[:30]}...")

# Atualiza a senha no D1
query = f"UPDATE user SET password = '{password_hash}' WHERE username = '{username}'"

print(f"\n📝 Executando update no D1...")
if run_d1_query(query):
    print(f"\n✅ Senha resetada com sucesso para {username}!")
    print(f"\nAgora você pode fazer login com:")
    print(f"  Username: {username}")
    print(f"  Senha: {nova_senha}")
else:
    print(f"\n❌ Falha ao resetar senha!")
