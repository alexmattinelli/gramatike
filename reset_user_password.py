#!/usr/bin/env python3
"""Script para resetar a senha de um usuário específico"""

import os
import sys

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gramatike_app import create_app
from gramatike_app.models import db, User
from sqlalchemy import or_

app = create_app()

with app.app_context():
    print("=== Reset de Senha ===\n")
    
    # Lista últimos usuários
    users = User.query.order_by(User.created_at.desc()).limit(10).all()
    print("Últimos usuários cadastrados:")
    for i, user in enumerate(users, 1):
        print(f"{i}. {user.username} ({user.email}) - ID: {user.id}")
    
    print("\n")
    username_or_email = input("Digite o username ou email do usuário: ").strip()
    
    user = User.query.filter(
        or_(User.email == username_or_email, User.username == username_or_email)
    ).first()
    
    if not user:
        print(f"❌ Usuário '{username_or_email}' não encontrado!")
        sys.exit(1)
    
    print(f"\n✅ Usuário encontrado: {user.username} (ID: {user.id})")
    print(f"   Email: {user.email}")
    print(f"   Nome: {user.nome or 'N/A'}")
    
    nova_senha = input("\nDigite a nova senha: ").strip()
    
    if len(nova_senha) < 6:
        print("❌ Senha muito curta! Mínimo 6 caracteres.")
        sys.exit(1)
    
    try:
        user.set_password(nova_senha)
        db.session.commit()
        print(f"\n✅ Senha resetada com sucesso para {user.username}!")
        
        # Testa a nova senha
        if user.check_password(nova_senha):
            print("✅ Verificação: Nova senha funcionando corretamente!")
        else:
            print("⚠️  ALERTA: Falha ao verificar a nova senha!")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erro ao resetar senha: {e}")
        sys.exit(1)
