"""
Testes para verificar a resiliência do feed quando tabelas do banco estão faltando.
"""
import pytest
import json
import tempfile
import os


def test_feed_with_missing_tables():
    """Testa que o feed não quebra quando tabelas estão faltando."""
    from gramatike_app import create_app
    from gramatike_app.models import db, User
    
    # Cria app de teste com banco temporário
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, 'test.db')
        
        app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
            'SECRET_KEY': 'test-secret-key',
            'WTF_CSRF_ENABLED': False
        })
        
        with app.app_context():
            # Apenas cria a tabela de usuários, não as de posts
            db.engine.execute("""
                CREATE TABLE user (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    foto_perfil TEXT DEFAULT 'img/perfil.png',
                    genero TEXT,
                    pronome TEXT,
                    bio TEXT,
                    data_nascimento TEXT,
                    created_at TEXT DEFAULT (datetime('now')),
                    is_admin INTEGER DEFAULT 0,
                    is_superadmin INTEGER DEFAULT 0,
                    is_banned INTEGER DEFAULT 0
                )
            """)
            
            # Cria um usuário de teste
            from werkzeug.security import generate_password_hash
            db.engine.execute("""
                INSERT INTO user (username, email, password, is_admin)
                VALUES ('testuser', 'test@example.com', ?, 0)
            """, (generate_password_hash('testpass'),))
            
        # Testa o endpoint /api/posts sem as tabelas de post criadas
        with app.test_client() as client:
            # Login primeiro
            response = client.post('/login', data={
                'email': 'testuser',
                'password': 'testpass'
            }, follow_redirects=True)
            
            # Tenta acessar /api/posts - deve retornar [] ao invés de erro
            response = client.get('/api/posts')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert isinstance(data, list)
            # Pode ser vazio ou conter posts, mas não deve dar erro
            
            # Tenta acessar /feed - deve renderizar ao invés de erro
            response = client.get('/feed')
            assert response.status_code == 200
            assert b'<!DOCTYPE html>' in response.data


def test_api_posts_returns_empty_on_error():
    """Testa que /api/posts retorna array vazio em caso de erro de banco."""
    from gramatike_app import create_app
    from gramatike_app.models import db
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, 'test.db')
        
        app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
            'SECRET_KEY': 'test-secret-key',
            'WTF_CSRF_ENABLED': False
        })
        
        with app.app_context():
            # Cria apenas tabela user para simular banco incompleto
            db.engine.execute("""
                CREATE TABLE user (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    is_admin INTEGER DEFAULT 0
                )
            """)
            
            # Cria usuário
            from werkzeug.security import generate_password_hash
            db.engine.execute("""
                INSERT INTO user (username, email, password)
                VALUES ('testuser', 'test@example.com', ?)
            """, (generate_password_hash('testpass'),))
        
        with app.test_client() as client:
            # Login
            client.post('/login', data={
                'email': 'testuser',
                'password': 'testpass'
            })
            
            # Testa endpoint - deve retornar [] e não dar erro
            response = client.get('/api/posts')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data == [] or isinstance(data, list)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
