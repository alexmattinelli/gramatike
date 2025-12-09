"""
Testes para o fluxo de login e redirecionamento para o feed.

Este módulo testa o fix para o problema relatado onde usuários
não conseguiam acessar a página de feed após fazer login.
"""
import pytest
from gramatike_app import create_app
from gramatike_app.models import db, User
from werkzeug.security import generate_password_hash


@pytest.fixture
def app():
    """Create and configure a test app instance."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()


@pytest.fixture
def test_user(app):
    """Create a test user."""
    with app.app_context():
        # Check if user already exists
        user = User.query.filter_by(username='testuser').first()
        if not user:
            user = User(
                username='testuser',
                email='test@example.com',
                password=generate_password_hash('testpass123'),
                nome='Test User',
                genero='neutro',
                pronome='elu/delu'
            )
            db.session.add(user)
            db.session.commit()
        return user


def test_login_redirects_to_feed(client, test_user):
    """Test that successful login redirects to /feed."""
    response = client.post('/login', data={
        'email': 'testuser',
        'password': 'testpass123'
    }, follow_redirects=False)
    
    assert response.status_code == 302
    assert '/feed' in response.location


def test_login_sets_session_cookie(client, test_user):
    """Test that login sets a session cookie."""
    response = client.post('/login', data={
        'email': 'testuser',
        'password': 'testpass123'
    }, follow_redirects=False)
    
    cookies = response.headers.getlist('Set-Cookie')
    assert any('session=' in cookie for cookie in cookies)


def test_authenticated_user_can_access_feed(client, test_user):
    """Test that authenticated user can access /feed."""
    # Login first
    client.post('/login', data={
        'email': 'testuser',
        'password': 'testpass123'
    })
    
    # Try to access feed
    response = client.get('/feed')
    assert response.status_code == 200


def test_unauthenticated_user_redirected_from_feed(client):
    """Test that unauthenticated user is redirected from /feed."""
    response = client.get('/feed', follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.location


def test_authenticated_user_redirected_from_index(client, test_user):
    """Test that authenticated user is redirected from / to /feed."""
    # Login first
    client.post('/login', data={
        'email': 'testuser',
        'password': 'testpass123'
    })
    
    # Access index
    response = client.get('/', follow_redirects=False)
    assert response.status_code == 302
    assert '/feed' in response.location


def test_login_with_email(client, test_user):
    """Test that login works with email."""
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'testpass123'
    }, follow_redirects=False)
    
    assert response.status_code == 302
    assert '/feed' in response.location


def test_login_with_username(client, test_user):
    """Test that login works with username."""
    response = client.post('/login', data={
        'email': 'testuser',  # field is named 'email' but accepts username
        'password': 'testpass123'
    }, follow_redirects=False)
    
    assert response.status_code == 302
    assert '/feed' in response.location


def test_login_with_wrong_password(client, test_user):
    """Test that login fails with wrong password."""
    response = client.post('/login', data={
        'email': 'testuser',
        'password': 'wrongpassword'
    }, follow_redirects=False)
    
    # Should stay on login page
    assert response.status_code == 200
    assert b'Login' in response.data or b'login' in response.data


def test_login_with_nonexistent_user(client):
    """Test that login fails with nonexistent user."""
    response = client.post('/login', data={
        'email': 'nonexistent',
        'password': 'testpass123'
    }, follow_redirects=False)
    
    # Should stay on login page
    assert response.status_code == 200
    assert b'Login' in response.data or b'login' in response.data


def test_full_login_flow(client, test_user):
    """Test complete login flow from start to feed."""
    # 1. Access login page
    response = client.get('/login')
    assert response.status_code == 200
    
    # 2. Submit login form
    response = client.post('/login', data={
        'email': 'testuser',
        'password': 'testpass123'
    }, follow_redirects=False)
    assert response.status_code == 302
    assert '/feed' in response.location
    
    # 3. Follow redirect to feed
    response = client.get(response.location)
    assert response.status_code == 200
    
    # 4. Verify can access feed directly
    response = client.get('/feed')
    assert response.status_code == 200


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
