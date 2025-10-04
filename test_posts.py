#!/usr/bin/env python
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gramatike_app import create_app
from gramatike_app.models import Post, db
from datetime import datetime

def main():
    try:
        app = create_app()
        
        with app.app_context():
            # Verificar se há posts na base de dados
            posts = Post.query.all()
            print(f"Número de posts encontrados: {len(posts)}")
            
            if len(posts) == 0:
                print("Não há posts na base de dados. Criando posts de exemplo...")
                
                # Criar alguns posts de exemplo
                posts_exemplo = [
                    Post(
                        usuario="Alex", 
                        conteudo="Este é o primeiro post da Gramátike! 🎉", 
                        imagem="", 
                        data=datetime.now()
                    ),
                    Post(
                        usuario="Maria", 
                        conteudo="Oi pessoal! Que bom estar aqui na comunidade Gramátike 💜 #bemvinde", 
                        imagem="", 
                        data=datetime.now()
                    ),
                    Post(
                        usuario="João", 
                        conteudo="Adorando essa plataforma inclusiva! #linguagemneutra #inclusão #gramatike", 
                        imagem="", 
                        data=datetime.now()
                    ),
                    Post(
                        usuario="Ana", 
                        conteudo="Primeira vez aqui! Alguém pode me explicar como funciona? 😊", 
                        imagem="", 
                        data=datetime.now()
                    )
                ]
                
                for post in posts_exemplo:
                    db.session.add(post)
                
                try:
                    db.session.commit()
                    print("✅ Posts de exemplo criados com sucesso!")
                    
                    # Verificar novamente
                    posts = Post.query.all()
                    print(f"Agora temos {len(posts)} posts na base de dados.")
                    
                except Exception as e:
                    print(f"❌ Erro ao salvar posts: {e}")
                    db.session.rollback()
                    
            else:
                print("Posts encontrados:")
                for i, post in enumerate(posts, 1):
                    print(f"{i}. {post.usuario}: {post.conteudo[:50]}...")
                    print(f"   Data: {post.data}")
                    
    except Exception as e:
        print(f"❌ Erro ao executar: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
