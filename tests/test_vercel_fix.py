#!/usr/bin/env python
"""
Unit test to verify Vercel deployment fix.
Tests Pillow 10+ compatibility and app initialization.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_pillow_compatibility():
    """Test that textbbox works (Pillow 10+ compatibility)"""
    from PIL import Image, ImageDraw, ImageFont
    
    im = Image.new('RGB', (100, 100))
    draw = ImageDraw.Draw(im)
    font = ImageFont.load_default()
    
    # This should work with Pillow 10+
    bbox = draw.textbbox((0, 0), 'Test', font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    
    assert tw > 0, "Text width should be positive"
    assert th > 0, "Text height should be positive"
    print("✅ Pillow textbbox() works correctly")


def test_app_import():
    """Test that app can be imported without errors"""
    from api.index import app
    
    assert app is not None, "App should be created"
    assert callable(app), "App should be callable (WSGI)"
    print("✅ App imports successfully")


def test_health_endpoint():
    """Test health endpoint works"""
    from api.index import app
    
    with app.test_client() as client:
        resp = client.get('/api/health')
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        assert resp.json == {'status': 'ok'}, f"Unexpected response: {resp.json}"
    
    print("✅ Health endpoint works")


def test_read_only_filesystem():
    """Test app handles read-only filesystem gracefully"""
    import os
    
    # Clear modules
    for mod in list(sys.modules.keys()):
        if 'gramatike_app' in mod or 'api.index' in mod:
            del sys.modules[mod]
    
    # Mock os.makedirs to simulate read-only filesystem
    original_makedirs = os.makedirs
    
    def mock_makedirs(*args, **kwargs):
        raise PermissionError("Read-only file system")
    
    os.makedirs = mock_makedirs
    
    try:
        # This should not crash
        from api.index import app
        assert app is not None, "App should be created even with read-only filesystem"
        print("✅ App handles read-only filesystem gracefully")
    finally:
        os.makedirs = original_makedirs


def main():
    print("=" * 70)
    print("UNIT TESTS - VERCEL DEPLOYMENT FIX")
    print("=" * 70)
    print()
    
    tests = [
        test_pillow_compatibility,
        test_app_import,
        test_health_endpoint,
        test_read_only_filesystem,
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
            failed += 1
        print()
    
    print("=" * 70)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 70)
    
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
