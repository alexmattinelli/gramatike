#!/usr/bin/env python3
"""Script para listar usuários e verificar problemas de login"""

import os
import sys

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gramatike_app import create_app
from gramatike_app.models import db, User

app = create_app()

with app.app_context():
    print("=== Usuários Cadastrados ===\n")
    
    # Lista todos os usuários
    users = User.query.order_by(User.created_at.desc()).all()
    print(f"Total de usuários: {len(users)}\n")
    
    print("Últimos 10 usuários cadastrados:")
    print("-" * 80)
    for user in users[:10]:
        print(f"ID: {user.id}")
        print(f"Username: {user.username}")
        print(f"Email: {user.email}")
        print(f"Nome: {user.nome or 'N/A'}")
        print(f"Email confirmado: {getattr(user, 'email_confirmed', 'N/A')}")
        print(f"Senha hash existe: {bool(user.password)}")
        print(f"Hash length: {len(user.password) if user.password else 0}")
        print(f"Admin: {user.is_admin}")
        print(f"Banido: {getattr(user, 'is_banned', False)}")
        print(f"Criado em: {user.created_at}")
        print("-" * 80)
    
    # Verifica se há usuários com problemas
    print("\n=== Verificação de Problemas ===\n")
    
    # Usuários sem senha
    no_password = User.query.filter((User.password == None) | (User.password == '')).all()
    if no_password:
        print(f"⚠️  {len(no_password)} usuário(s) SEM SENHA:")
        for u in no_password:
            print(f"   - {u.username} (ID: {u.id})")
    else:
        print("✅ Todos os usuários têm senha definida")
    
    # Usuários banidos
    banned = User.query.filter_by(is_banned=True).all()
    if banned:
        print(f"\n⚠️  {len(banned)} usuário(s) BANIDO(S):")
        for u in banned:
            print(f"   - {u.username} (ID: {u.id})")
    else:
        print("\n✅ Nenhum usuário banido")
    
    print("\n=== Para testar login ===")
    print("Execute: /workspaces/gramatike/.venv/bin/python debug_login.py")
    print("Ou use: /workspaces/gramatike/.venv/bin/python reset_user_password.py")
