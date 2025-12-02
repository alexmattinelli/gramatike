#!/usr/bin/env python3
"""
Script de diagnóstico para o Dashboard Admin
Verifica dados, tabelas e possíveis problemas
"""

import os
import sys

# Configure o ambiente antes de importar a app
os.environ.setdefault('FLASK_APP', 'gramatike_app')

from gramatike_app import create_app, db
from gramatike_app.models import (
    User, Estudo, EduContent, ExerciseTopic, ExerciseSection, 
    EduTopic, Report, EduNovidade, Divulgacao, BlockedWord
)
from datetime import datetime

def check_table(model, name):
    """Verifica se uma tabela existe e tem dados"""
    try:
        count = model.query.count()
        print(f"✓ {name}: {count} registros")
        if count > 0:
            latest = model.query.order_by(model.id.desc()).first()
            print(f"  └─ Último registro: ID={latest.id}")
        return True
    except Exception as e:
        print(f"✗ {name}: ERRO - {str(e)[:100]}")
        return False

def check_admin_users():
    """Verifica se existem usuários admin"""
    try:
        admins = User.query.filter(
            (User.is_admin == True) | (User.is_superadmin == True)
        ).all()
        print(f"\n📊 USUÁRIOS ADMIN:")
        print(f"   Total: {len(admins)}")
        for admin in admins:
            print(f"   - {admin.nome} ({admin.email}) - Admin: {admin.is_admin}, Super: {admin.is_superadmin}")
        return len(admins) > 0
    except Exception as e:
        print(f"✗ Erro ao verificar admins: {e}")
        return False

def check_database_url():
    """Verifica a URL do banco de dados"""
    from config import Config
    db_url = Config.SQLALCHEMY_DATABASE_URI
    print(f"\n🗄️  DATABASE:")
    print(f"   URL: {db_url[:50]}..." if len(db_url) > 50 else f"   URL: {db_url}")
    if 'sqlite' in db_url.lower():
        print(f"   Tipo: SQLite (desenvolvimento)")
    elif 'postgres' in db_url.lower():
        print(f"   Tipo: PostgreSQL (produção)")
    else:
        print(f"   Tipo: Desconhecido")

def main():
    """Executa todos os diagnósticos"""
    print("=" * 60)
    print("🔍 DIAGNÓSTICO DO DASHBOARD ADMIN")
    print("=" * 60)
    
    # Cria a aplicação
    app = create_app()
    
    with app.app_context():
        # 1. Verifica banco de dados
        check_database_url()
        
        print("\n" + "=" * 60)
        print("📋 VERIFICANDO TABELAS E DADOS")
        print("=" * 60 + "\n")
        
        # 2. Verifica cada tabela
        tables = [
            (User, "Users"),
            (Estudo, "Estudos (Gramátike)"),
            (EduContent, "EduContent (Artigos, Apostilas, etc)"),
            (EduTopic, "EduTopic (Tópicos Edu)"),
            (ExerciseTopic, "ExerciseTopic (Tópicos de Exercício)"),
            (ExerciseSection, "ExerciseSection (Seções)"),
            (Report, "Reports (Denúncias)"),
            (EduNovidade, "EduNovidade (Novidades)"),
            (Divulgacao, "Divulgacao (Cards de Destaque)"),
            (BlockedWord, "BlockedWord (Palavras Bloqueadas)"),
        ]
        
        all_ok = True
        for model, name in tables:
            ok = check_table(model, name)
            if not ok:
                all_ok = False
        
        print("\n" + "=" * 60)
        
        # 3. Verifica usuários admin
        has_admins = check_admin_users()
        
        print("\n" + "=" * 60)
        print("📈 RESUMO")
        print("=" * 60)
        
        if all_ok and has_admins:
            print("✓ Todas as tabelas estão OK")
            print("✓ Existem usuários admin cadastrados")
            print("\n💡 Se o dashboard não está aparecendo corretamente:")
            print("   1. Verifique se você está logado com um usuário admin")
            print("   2. Limpe o cache do navegador (Ctrl+Shift+R)")
            print("   3. Verifique o console do navegador (F12) por erros JavaScript")
            print("   4. Verifique os logs do servidor Flask por erros 500")
        else:
            print("⚠️  PROBLEMAS DETECTADOS:")
            if not all_ok:
                print("   - Algumas tabelas estão vazias ou com erro")
                print("   - Execute as migrations: flask db upgrade")
            if not has_admins:
                print("   - Não há usuários admin cadastrados")
                print("   - Execute: python create_superadmin.py")
        
        print("\n" + "=" * 60)

if __name__ == '__main__':
    main()
