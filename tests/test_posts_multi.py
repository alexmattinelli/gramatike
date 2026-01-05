#!/usr/bin/env python3
"""Teste simples para /api/posts_multi (integração)"""
from io import BytesIO
from gramatike_app import create_app
from gramatike_app.models import User, Post, PostImage, db


def run_test():
    app = create_app()
    with app.app_context():
        # garantir tabelas
        try:
            db.create_all()
        except Exception:
            pass

        user = User.query.filter_by(username='test_integration').first()
        if not user:
            user = User(username='test_integration', email='test@local')
            try:
                user.set_password('password123')
            except Exception:
                user.password = 'password123'
            db.session.add(user)
            db.session.commit()

        client = app.test_client()
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True

        multipart = {
            'conteudo': 'Teste automatizado posts_multi',
            'imagens': [
                (BytesIO(b"fakeimage1content"), 'a1.png'),
                (BytesIO(b"fakeimage2content"), 'a2.jpg')
            ]
        }

        resp = client.post('/api/posts_multi', data=multipart)
        assert resp.status_code == 201, f"Status inesperado: {resp.status_code}"
        j = resp.get_json() or {}
        assert j.get('imagens') and len(j['imagens']) >= 2, f"Resposta sem imagens: {j}"

        post = Post.query.filter_by(usuarie_id=user.id).order_by(Post.id.desc()).first()
        assert post is not None, 'Post não criado no DB'
        images = PostImage.query.filter_by(post_id=post.id).all()
        assert len(images) >= 2, f'Esperava 2 PostImage, encontrou {len(images)}'

        print('TEST_PASS: /api/posts_multi criado com sucesso (id=', post.id, ')')


if __name__ == '__main__':
    run_test()
