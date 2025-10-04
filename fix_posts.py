#!/usr/bin/env python
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gramatike_app import create_app
from gramatike_app.models import Post, db
from datetime import datetime
import json

def verificar_e_corrigir_posts():
    app = create_app()
    
    with app.app_context():
        try:
            # 1. Verificar tabelas existentes
            print("🔍 Verificando tabelas...")
            print("Tabelas no banco:")
            for table in db.metadata.tables.keys():
                print(f"  - {table}")
            
            # 2. Verificar posts existentes
            posts = Post.query.all()
            print(f"\n📊 Posts existentes: {len(posts)}")
            
            if posts:
                for i, post in enumerate(posts, 1):
                    print(f"{i}. {post.usuario}: {post.conteudo[:30]}... ({post.data})")
            
            # 3. Se não há posts, criar alguns de exemplo
            if len(posts) == 0:
                print("\n➕ Criando posts de exemplo...")
                posts_exemplo = [
                    {
                        'usuario': 'Gramatike',
                        'conteudo': 'Bem-vindes à Gramátike! 🎉 Nossa comunidade inclusiva.',
                        'imagem': '',
                        'data': datetime.now()
                    },
                    {
                        'usuario': 'Alex',
                        'conteudo': 'Testando a plataforma! #gramatike #linguagemneutra',
                        'imagem': '',
                        'data': datetime.now()
                    },
                    {
                        'usuario': 'Maria',
                        'conteudo': 'Que bom ter um espaço inclusivo para compartilhar ideias! 💜',
                        'imagem': '',
                        'data': datetime.now()
                    }
                ]
                
                for post_data in posts_exemplo:
                    post = Post(**post_data)
                    db.session.add(post)
                
                db.session.commit()
                print("✅ Posts de exemplo criados!")
                
                # Verificar novamente
                posts = Post.query.all()
                print(f"Total de posts agora: {len(posts)}")
            
            # 4. Testar a API /api/posts
            print("\n🧪 Testando API /api/posts...")
            with app.test_client() as client:
                response = client.get('/api/posts')
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.get_json()
                        print(f"Posts retornados pela API: {len(data) if data else 0}")
                        if data:
                            for post in data:
                                print(f"  - {post.get('usuario')}: {post.get('conteudo', '')[:30]}...")
                    except Exception as e:
                        print(f"Erro ao fazer parse JSON: {e}")
                        print(f"Resposta bruta: {response.get_data(as_text=True)}")
                else:
                    print(f"❌ Erro na API: {response.get_data(as_text=True)}")
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    verificar_e_corrigir_posts()
