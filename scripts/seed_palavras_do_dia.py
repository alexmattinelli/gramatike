#!/usr/bin/env python3
"""
Script para popular o banco de dados com palavras do dia iniciais.
"""
import sys
import os

# Adiciona o diretório pai ao path para importar gramatike_app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gramatike_app import create_app
from gramatike_app.models import db, PalavraDoDia, User

def seed_palavras_do_dia():
    """Adiciona palavras iniciais ao banco de dados."""
    app = create_app()
    
    with app.app_context():
        # Verifica se já existem palavras
        count = PalavraDoDia.query.count()
        if count > 0:
            print(f"⚠️  Já existem {count} palavras cadastradas. Deseja continuar? (s/n)")
            resposta = input().lower()
            if resposta != 's':
                print("Cancelado.")
                return
        
        # Busca um admin para ser o autor (ou usa o primeiro usuário)
        admin = User.query.filter_by(is_admin=True).first()
        if not admin:
            admin = User.query.first()
        
        if not admin:
            print("❌ Nenhum usuário encontrado. Crie um usuário primeiro.")
            return
        
        palavras = [
            {
                'palavra': 'elu',
                'significado': 'Elu é um pronome neutro usado por pessoas que não se identificam nem com o masculino nem com o feminino.',
                'ordem': 1
            },
            {
                'palavra': 'todes',
                'significado': 'Todes é a forma neutra de "todos/todas", usada para incluir todas as identidades de gênero de forma respeitosa.',
                'ordem': 2
            },
            {
                'palavra': 'amigue',
                'significado': 'Amigue é a forma neutra de "amigo/amiga", demonstrando respeito e inclusão independente da identidade de gênero.',
                'ordem': 3
            },
            {
                'palavra': 'pessoa não binárie',
                'significado': 'Pessoa não binárie é alguém cuja identidade de gênero não se enquadra exclusivamente no masculino ou feminino.',
                'ordem': 4
            },
            {
                'palavra': 'linguagem neutra',
                'significado': 'Linguagem neutra é uma forma de comunicação que busca incluir todas as identidades de gênero, sem favorecer o masculino ou feminino.',
                'ordem': 5
            }
        ]
        
        for p in palavras:
            # Verifica se já existe
            existe = PalavraDoDia.query.filter_by(palavra=p['palavra']).first()
            if existe:
                print(f"⚠️  Palavra '{p['palavra']}' já existe, pulando...")
                continue
            
            nova_palavra = PalavraDoDia(
                palavra=p['palavra'],
                significado=p['significado'],
                ordem=p['ordem'],
                ativo=True,
                created_by=admin.id
            )
            db.session.add(nova_palavra)
            print(f"✅ Adicionada: {p['palavra']}")
        
        db.session.commit()
        print(f"\n🎉 Palavras do Dia cadastradas com sucesso!")
        
        # Lista todas as palavras
        todas = PalavraDoDia.query.order_by(PalavraDoDia.ordem.asc()).all()
        print(f"\n📝 Total de palavras cadastradas: {len(todas)}")
        for palavra in todas:
            print(f"   {palavra.ordem}. {palavra.palavra} - {'✓ ativo' if palavra.ativo else '✗ inativo'}")

if __name__ == '__main__':
    seed_palavras_do_dia()
