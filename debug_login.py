#!/usr/bin/env python3
"""Script de debug para testar login e cadastro"""

import os
import sys

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gramatike_app import create_app
from gramatike_app.models import db, User
from sqlalchemy import or_

app = create_app()

with app.app_context():
    print("=== Debug de Login ===\n")
    
    # Lista todos os usuários
    users = User.query.all()
    print(f"Total de usuários: {len(users)}\n")
    
    for user in users[-5:]:  # Últimos 5 usuários
        print(f"ID: {user.id}")
        print(f"Nome: {user.nome}")
        print(f"Username: {user.username}")
        print(f"Email: {user.email}")
        print(f"Email confirmado: {getattr(user, 'email_confirmed', 'N/A')}")
        print(f"Senha hash: {user.password[:20]}...")
        print(f"Admin: {user.is_admin}")
        print(f"Banido: {getattr(user, 'is_banned', False)}")
        print("-" * 50)
    
    # Teste de verificação de senha
    print("\n=== Teste de Login ===")
    test_username = input("Digite o username ou email para testar: ").strip()
    test_password = input("Digite a senha: ").strip()
    
    user = User.query.filter(
        or_(User.email == test_username, User.username == test_username)
    ).first()
    
    if user:
        print(f"\nUsuário encontrado: {user.username}")
        print(f"Email confirmado: {getattr(user, 'email_confirmed', False)}")
        
        # Testa a senha
        is_valid = user.check_password(test_password)
        print(f"Senha correta: {is_valid}")
        
        if not is_valid:
            print("\n⚠️  PROBLEMA: Senha incorreta")
            print("Possíveis causas:")
            print("1. Senha digitada errada")
            print("2. Hash da senha corrompido no banco")
            print("3. Problema no método check_password")
    else:
        print(f"\n❌ Usuário '{test_username}' não encontrado")
        print("Possíveis usernames:")
        for u in users[-5:]:
            print(f"  - {u.username} ({u.email})")
