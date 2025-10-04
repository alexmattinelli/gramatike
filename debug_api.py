#!/usr/bin/env python
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gramatike_app import create_app
from gramatike_app.models import Post, db

def debug_api():
    app = create_app()
    
    # Listar todas as rotas registradas
    print("🔍 Rotas registradas na aplicação:")
    with app.app_context():
        for rule in app.url_map.iter_rules():
            methods = ','.join(rule.methods)
            print(f"  {rule.endpoint}: {rule.rule} [{methods}]")
    
    print("\n" + "="*50)
    
    # Testar a rota /api/posts diretamente
    with app.test_client() as client:
        print("🧪 Testando GET /api/posts...")
        try:
            response = client.get('/api/posts')
            print(f"Status: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            print(f"Data: {response.get_data(as_text=True)}")
            
            if response.status_code == 200:
                try:
                    import json
                    data = json.loads(response.get_data(as_text=True))
                    print(f"Posts retornados: {len(data)}")
                    for post in data:
                        print(f"  - {post.get('usuario')}: {post.get('conteudo', '')[:50]}...")
                except json.JSONDecodeError as e:
                    print(f"Erro ao fazer parse do JSON: {e}")
            else:
                print(f"❌ Erro na requisição: {response.get_data(as_text=True)}")
                
        except Exception as e:
            print(f"❌ Erro ao testar API: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_api()
