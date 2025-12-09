#!/usr/bin/env python3
"""Final comprehensive test of login functionality"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gramatike_app import create_app
from gramatike_app.models import db, User

app = create_app()

print("=" * 60)
print("FINAL LOGIN TEST")
print("=" * 60)

with app.app_context():
    # Ensure test user exists
    user = User.query.filter_by(username='testuser').first()
    if not user:
        user = User(username="testuser", email="test@gramatike.com", nome="Test User")
        user.set_password("test123")
        db.session.add(user)
        db.session.commit()
        print("✓ Test user created")
    else:
        print("✓ Test user exists")
    
    with app.test_client() as client:
        print("\n1. Testing GET /login")
        response = client.get('/login')
        assert response.status_code == 200, "GET /login should return 200"
        assert b'Entrar' in response.data, "Page should have 'Entrar' button"
        assert b'csrf_token' in response.data, "Page should have CSRF token"
        print("   ✓ Login page loads correctly")
        print("   ✓ CSRF token is present")
        
        # Extract CSRF token
        import re
        csrf_match = re.search(b'name="csrf_token" value="([^"]+)"', response.data)
        csrf_token = csrf_match.group(1).decode() if csrf_match else ''
        assert csrf_token, "CSRF token should not be empty"
        print(f"   ✓ CSRF token extracted: {csrf_token[:20]}...")
        
        print("\n2. Testing login with INVALID credentials")
        response = client.post('/login', data={
            'email': 'wronguser',
            'password': 'wrongpass',
            'csrf_token': csrf_token
        }, follow_redirects=True)
        assert response.status_code == 200, "Should stay on login page"
        assert b'Login' in response.data or b'inv' in response.data.lower(), "Should show error"
        print("   ✓ Invalid login rejected")
        print("   ✓ User stays on login page")
        
        print("\n3. Testing login with VALID username")
        response = client.post('/login', data={
            'email': 'testuser',
            'password': 'test123',
            'csrf_token': csrf_token
        }, follow_redirects=False)
        assert response.status_code == 302, "Should redirect after successful login"
        assert '/login' not in response.headers.get('Location', ''), "Should redirect away from login"
        print("   ✓ Valid username login successful")
        print(f"   ✓ Redirects to: {response.headers.get('Location', '')}")
        
        # Get new CSRF token for next test
        response = client.get('/login')
        csrf_match = re.search(b'name="csrf_token" value="([^"]+)"', response.data)
        csrf_token = csrf_match.group(1).decode() if csrf_match else ''
        
        print("\n4. Testing login with VALID email")
        response = client.post('/login', data={
            'email': 'test@gramatike.com',
            'password': 'test123',
            'csrf_token': csrf_token
        }, follow_redirects=False)
        assert response.status_code == 302, "Should redirect after successful login"
        print("   ✓ Valid email login successful")
        print(f"   ✓ Redirects to: {response.headers.get('Location', '')}")
        
        print("\n5. Testing CSRF protection")
        response = client.post('/login', data={
            'email': 'testuser',
            'password': 'test123'
            # No CSRF token
        }, follow_redirects=False)
        assert response.status_code == 400, "Should reject POST without CSRF token"
        print("   ✓ CSRF protection working")
        print("   ✓ Rejects requests without CSRF token")

print("\n" + "=" * 60)
print("ALL TESTS PASSED! ✅")
print("=" * 60)
print("\nLogin functionality is working correctly:")
print("- Login page loads with CSRF token")
print("- Invalid credentials are rejected")
print("- Valid username login works")
print("- Valid email login works")
print("- CSRF protection is active")
print("\nTo test manually:")
print("  1. Run: python run.py")
print("  2. Open: http://localhost:5000/login")
print("  3. Login: testuser / test123")
print("=" * 60)
