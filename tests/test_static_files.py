#!/usr/bin/env python
"""
Unit test to verify static files are accessible and prevent 404 errors.
Tests that previously missing files now exist and return 200 status.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_style_css_exists():
    """Test that style.css file exists"""
    from api.index import app
    
    with app.test_client() as client:
        resp = client.get('/static/style.css')
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        assert resp.content_type.startswith('text/css'), f"Expected CSS content type, got {resp.content_type}"
    
    print("✅ style.css is accessible (200 OK)")


def test_perfil_png_exists():
    """Test that default profile image exists"""
    from api.index import app
    
    with app.test_client() as client:
        resp = client.get('/static/img/perfil.png')
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        assert resp.content_type.startswith('image/'), f"Expected image content type, got {resp.content_type}"
        assert len(resp.data) > 0, "Image data should not be empty"
    
    print("✅ img/perfil.png is accessible (200 OK)")


def test_favicon_exists():
    """Test that favicon files exist (regression test)"""
    from api.index import app
    
    with app.test_client() as client:
        # Test PNG favicon from static path
        resp = client.get('/static/favicon.png')
        assert resp.status_code == 200, f"favicon.png - Expected 200, got {resp.status_code}"
        
        # Test ICO favicon from static path
        resp = client.get('/static/favicon.ico')
        assert resp.status_code == 200, f"favicon.ico - Expected 200, got {resp.status_code}"
    
    print("✅ Favicons are accessible (200 OK)")


def test_favicon_root_routes():
    """Test that favicon files are accessible from root path (fix for browser 404s)"""
    from api.index import app
    
    with app.test_client() as client:
        # Test PNG favicon from root (browsers request this automatically)
        resp = client.get('/favicon.png', follow_redirects=True)
        assert resp.status_code == 200, f"/favicon.png - Expected 200, got {resp.status_code}"
        assert resp.content_type.startswith('image/'), f"Expected image content type, got {resp.content_type}"
        
        # Test ICO favicon from root (browsers request this automatically)
        resp = client.get('/favicon.ico', follow_redirects=True)
        assert resp.status_code == 200, f"/favicon.ico - Expected 200, got {resp.status_code}"
        
        # Test that these are redirects (302) before following
        resp_no_redirect = client.get('/favicon.png', follow_redirects=False)
        assert resp_no_redirect.status_code == 302, f"Expected redirect (302), got {resp_no_redirect.status_code}"
    
    print("✅ Root-level favicon routes work correctly (302 redirect -> 200 OK)")


def test_perfil_image_valid():
    """Test that perfil.png is a valid image"""
    from PIL import Image
    import io
    from api.index import app
    
    with app.test_client() as client:
        resp = client.get('/static/img/perfil.png')
        
        # Try to open as PIL Image
        img = Image.open(io.BytesIO(resp.data))
        assert img.format == 'PNG', f"Expected PNG format, got {img.format}"
        assert img.size[0] > 0 and img.size[1] > 0, "Image dimensions should be positive"
    
    print(f"✅ perfil.png is a valid {img.size[0]}x{img.size[1]} PNG image")


def main():
    print("=" * 70)
    print("UNIT TESTS - STATIC FILES FIX")
    print("=" * 70)
    print()
    
    tests = [
        test_style_css_exists,
        test_perfil_png_exists,
        test_favicon_exists,
        test_favicon_root_routes,
        test_perfil_image_valid,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            print(f"Running: {test.__name__}...")
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
        print()
    
    print("=" * 70)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 70)
    
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
