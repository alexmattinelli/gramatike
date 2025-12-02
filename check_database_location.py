#!/usr/bin/env python3
"""
Verifica qual banco de dados está sendo usado
"""
from gramatike_app import create_app
from config import Config

app = create_app()

print("=" * 60)
print("🗄️  CONFIGURAÇÃO DO BANCO DE DADOS")
print("=" * 60)

print(f"\nDatabase URI configurado:")
db_uri = Config.SQLALCHEMY_DATABASE_URI
print(f"  {db_uri}\n")

if 'sqlite' in db_uri.lower():
    import os
    # Extrai o caminho do arquivo
    db_path = db_uri.replace('sqlite:///', '')
    print(f"Tipo: SQLite")
    print(f"Arquivo: {db_path}")
    print(f"Caminho absoluto: {os.path.abspath(db_path)}")
    print(f"Arquivo existe: {os.path.exists(db_path)}")
    if os.path.exists(db_path):
        size = os.path.getsize(db_path)
        print(f"Tamanho: {size} bytes")
elif 'postgres' in db_uri.lower():
    print(f"Tipo: PostgreSQL")
    # Esconde credenciais
    parts = db_uri.split('@')
    if len(parts) > 1:
        print(f"Host: {parts[1]}")
else:
    print(f"Tipo: Desconhecido")

print("\n" + "=" * 60)
print("📁 ARQUIVOS SQLITE NO PROJETO")
print("=" * 60)

import os
import glob

# Procura por arquivos .db
db_files = glob.glob('**/*.db', recursive=True)
if db_files:
    print(f"\nEncontrados {len(db_files)} arquivo(s) .db:")
    for f in db_files:
        size = os.path.getsize(f)
        print(f"  - {f} ({size} bytes)")
else:
    print("\nNenhum arquivo .db encontrado")

print("\n" + "=" * 60)
print("💡 AÇÃO NECESSÁRIA")
print("=" * 60)

print("\nVocê disse que já tem um superadmin, mas o banco está vazio.")
print("Isso significa uma das seguintes situações:")
print("\n1. Você está olhando um banco diferente (ex: produção vs desenvolvimento)")
print("2. O banco foi resetado/deletado recentemente")
print("3. A variável DATABASE_URL está apontando para um banco novo/vazio")
print("\n✅ SOLUÇÃO: Execute o comando para criar o superadmin:")
print("   .venv/bin/python create_superadmin.py")
