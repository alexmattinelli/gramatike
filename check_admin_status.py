#!/usr/bin/env python3
"""
Verifica o estado real dos usuários admin no banco
"""
from gramatike_app import create_app, db
from gramatike_app.models import User

app = create_app()

with app.app_context():
    print("=" * 60)
    print("🔍 VERIFICAÇÃO DE USUÁRIOS ADMIN")
    print("=" * 60)
    
    # Lista TODOS os usuários
    all_users = User.query.all()
    print(f"\n📊 Total de usuários no banco: {len(all_users)}\n")
    
    if not all_users:
        print("❌ ERRO: Nenhum usuário encontrado no banco!")
        print("   Execute: .venv/bin/python create_superadmin.py")
    else:
        # Mostra cada usuário
        for u in all_users:
            print(f"👤 Usuário: {u.username}")
            print(f"   Email: {u.email}")
            print(f"   ID: {u.id}")
            
            # Verifica atributos de admin
            has_is_admin = hasattr(u, 'is_admin')
            has_is_superadmin = hasattr(u, 'is_superadmin')
            
            print(f"   Tem atributo 'is_admin': {has_is_admin}")
            print(f"   Tem atributo 'is_superadmin': {has_is_superadmin}")
            
            if has_is_admin:
                print(f"   is_admin = {u.is_admin} (tipo: {type(u.is_admin)})")
            else:
                print(f"   ⚠️  FALTA coluna 'is_admin'")
                
            if has_is_superadmin:
                print(f"   is_superadmin = {u.is_superadmin} (tipo: {type(u.is_superadmin)})")
            else:
                print(f"   ⚠️  FALTA coluna 'is_superadmin'")
            
            print()
        
        # Tenta o filtro original
        print("=" * 60)
        print("🔍 Testando filtro de admin:")
        print("=" * 60)
        
        try:
            admins = User.query.filter(
                (User.is_admin == True) | (User.is_superadmin == True)
            ).all()
            print(f"✓ Admins encontrados: {len(admins)}")
            for a in admins:
                print(f"  - {a.username} ({a.email})")
        except Exception as e:
            print(f"✗ ERRO ao filtrar admins: {e}")
            print(f"   Tipo do erro: {type(e).__name__}")
    
    # Verifica a estrutura da tabela
    print("\n" + "=" * 60)
    print("🗄️  ESTRUTURA DA TABELA 'user'")
    print("=" * 60)
    
    try:
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        columns = inspector.get_columns('user')
        
        print(f"\nColunas encontradas ({len(columns)}):")
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")
            
        # Verifica especificamente as colunas de admin
        col_names = [c['name'] for c in columns]
        if 'is_admin' not in col_names:
            print("\n❌ PROBLEMA: Coluna 'is_admin' NÃO existe!")
            print("   Solução: flask db upgrade")
        if 'is_superadmin' not in col_names:
            print("\n❌ PROBLEMA: Coluna 'is_superadmin' NÃO existe!")
            print("   Solução: flask db upgrade")
            
    except Exception as e:
        print(f"Erro ao inspecionar tabela: {e}")
    
    print("\n" + "=" * 60)
    print("💡 DIAGNÓSTICO")
    print("=" * 60)
    
    if not all_users:
        print("\n❌ Banco vazio - execute create_superadmin.py")
    else:
        # Verifica se algum usuário tem as colunas
        sample = all_users[0]
        if not hasattr(sample, 'is_admin') or not hasattr(sample, 'is_superadmin'):
            print("\n❌ PROBLEMA ENCONTRADO:")
            print("   As colunas 'is_admin' e 'is_superadmin' não existem na tabela!")
            print("\n✅ SOLUÇÃO:")
            print("   1. Verifique se há migrations pendentes:")
            print("      flask db current")
            print("   2. Execute as migrations:")
            print("      flask db upgrade")
            print("   3. Execute novamente:")
            print("      .venv/bin/python create_superadmin.py")
        else:
            # Colunas existem, mas valores podem estar errados
            print("\n✓ Colunas de admin existem")
            admin_count = sum(1 for u in all_users if getattr(u, 'is_admin', False) or getattr(u, 'is_superadmin', False))
            if admin_count == 0:
                print(f"\n⚠️  Nenhum usuário tem is_admin=True ou is_superadmin=True")
                print("   Execute: .venv/bin/python create_superadmin.py")
            else:
                print(f"\n✓ Encontrados {admin_count} admin(s)")
                print("   Verifique se você está logado com um desses usuários!")
