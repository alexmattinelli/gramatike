#!/usr/bin/env python3
"""Test script to verify login functionality"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gramatike_app import create_app
from gramatike_app.models import db, User

app = create_app()

with app.app_context():
    print("=== Testing Login Fix ===\n")
    
    # Check if tables exist
    try:
        user_count = User.query.count()
        print(f"✓ Database connected - {user_count} users found\n")
    except Exception as e:
        print(f"✗ Database error: {e}\n")
        sys.exit(1)
    
    # List some users
    users = User.query.limit(5).all()
    if users:
        print("Sample users:")
        for u in users:
            print(f"  - {u.username} ({u.email})")
        print()
    else:
        print("No users in database. Creating a test user...\n")
        # Create a test user
        test_user = User(
            username="testuser",
            email="test@gramatike.com",
            nome="Test User"
        )
        test_user.set_password("test123")
        db.session.add(test_user)
        db.session.commit()
        print(f"✓ Created test user: testuser / test123\n")
    
    # Test the login route
    print("=== Testing Login Route ===")
    with app.test_client() as client:
        # Test GET request
        response = client.get('/login')
        if response.status_code == 200:
            print("✓ GET /login returns 200")
            if b'Entrar' in response.data:
                print("✓ Login page contains 'Entrar' button")
            if b'csrf_token' in response.data:
                print("✓ CSRF token present in form")
            else:
                print("✗ CSRF token missing!")
        else:
            print(f"✗ GET /login returned {response.status_code}")
        
        # Test POST with invalid credentials
        print("\nTesting invalid login...")
        # First get the page to get CSRF token
        get_response = client.get('/login')
        import re
        csrf_match = re.search(b'name="csrf_token" value="([^"]+)"', get_response.data)
        csrf_token = csrf_match.group(1).decode() if csrf_match else ''
        
        response = client.post('/login', data={
            'email': 'invalid@test.com',
            'password': 'wrongpass',
            'csrf_token': csrf_token
        }, follow_redirects=False)
        
        if response.status_code in [200, 302]:
            print(f"✓ POST /login accepted (status: {response.status_code})")
            if b'inv' in response.data.lower() or b'erro' in response.data.lower():
                print("✓ Error message shown for invalid credentials")
        else:
            print(f"✗ POST /login failed with {response.status_code}")
            if response.data:
                print(f"Response: {response.data[:200]}")
        
        # Test with valid credentials
        print("\nTesting valid login...")
        response = client.post('/login', data={
            'email': 'testuser',
            'password': 'test123',
            'csrf_token': csrf_token
        }, follow_redirects=False)
        
        if response.status_code == 302:
            print(f"✓ Valid login redirects (status: {response.status_code})")
            location = response.headers.get('Location', '')
            if '/login' not in location:
                print("✓ Redirects away from login page (login successful!)")
                print(f"  Redirect location: {location}")
        else:
            print(f"Status: {response.status_code}")
            if response.data:
                print(f"Response: {response.data[:200]}")
    
    print("\n=== Test Complete ===")
    print("\nTo test manually:")
    print("1. Run: python run.py")
    print("2. Open http://localhost:5000/login")
    if User.query.filter_by(username='testuser').first():
        print("3. Login with: testuser / test123")
