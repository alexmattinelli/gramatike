#!/usr/bin/env python3
"""
Script para inicializar ou verificar o banco de dados Gramátike.
Útil para recuperação após exclusão acidental de tabelas.
"""
import os
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

def init_local_database():
    """Inicializa banco de dados local SQLite"""
    from gramatike_app import create_app
    from gramatike_app.models import db
    
    # Configura para usar SQLite local (pode ser sobrescrito por DATABASE_URL)
    if not os.environ.get('DATABASE_URL'):
        os.environ['DATABASE_URL'] = 'sqlite:///instance/app.db'
    
    app = create_app()
    
    with app.app_context():
        print("🔍 Verificando estrutura do banco de dados...")
        
        try:
            # Tenta verificar se as tabelas existem
            from gramatike_app.models import User
            user_count = User.query.count()
            print(f"✅ Banco de dados OK - {user_count} usuáries encontrades")
            return True
        except Exception as e:
            print(f"⚠️  Problema detectado no banco de dados")
            print("🔧 Criando/recriando tabelas...")
            
            try:
                # Cria todas as tabelas
                db.create_all()
                print("✅ Tabelas criadas com sucesso!")
                return True
            except Exception as create_error:
                print(f"❌ Erro ao criar tabelas")
                print(f"   Verifique as permissões e o caminho do banco de dados")
                return False

def verify_d1_instructions():
    """Mostra instruções para verificar/inicializar D1"""
    print("\n" + "="*70)
    print("📋 INSTRUÇÕES PARA CLOUDFLARE D1")
    print("="*70)
    print("""
Para verificar ou criar o banco D1 (produção), execute:

1. Verificar se o banco existe:
   wrangler d1 info gramatike

2. Se não existir, criar:
   wrangler d1 create gramatike
   
3. Atualizar o database_id no wrangler.toml com o ID retornado

4. Criar as tabelas:
   wrangler d1 execute gramatike --file=./schema.d1.sql

5. Verificar tabelas criadas:
   wrangler d1 execute gramatike --command="SELECT name FROM sqlite_master WHERE type='table';"

6. Fazer deploy:
   npm run deploy

📖 Documentação completa em: README.md (seção "Banco de Dados")
""")

def main():
    """Função principal"""
    print("🚀 Gramátike - Inicializador de Banco de Dados\n")
    
    # Verifica ambiente
    if os.environ.get('CLOUDFLARE_WORKERS'):
        print("⚠️  Ambiente Cloudflare Workers detectado")
        print("Use wrangler para gerenciar o banco D1")
        verify_d1_instructions()
        return 0
    
    # Inicializa banco local
    success = init_local_database()
    
    if success:
        print("\n✅ Banco de dados pronto para uso!")
        print("\n💡 Próximos passos:")
        print("   - Para criar um superadmin: python create_superadmin.py")
        print("   - Para rodar a aplicação: python run.py")
        return 0
    else:
        print("\n❌ Falha ao inicializar banco de dados")
        print("   Verifique os logs acima para mais detalhes")
        return 1

if __name__ == '__main__':
    sys.exit(main())
