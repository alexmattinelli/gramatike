"""
Test for to_d1_null function to verify it properly handles undefined values
and prevents D1_TYPE_ERROR.
"""

import sys
import os

# Add the parent directory to path so we can import gramatike_d1
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gramatike_d1.db import to_d1_null, sanitize_for_d1


def test_to_d1_null_with_none():
    """Test that None is properly converted"""
    result = to_d1_null(None)
    # In non-Pyodide environment, should return None
    assert result is None, f"Expected None, got {result}"
    print("✓ to_d1_null(None) returns None")


def test_to_d1_null_with_basic_types():
    """Test that basic Python types are preserved"""
    # Test int
    result = to_d1_null(42)
    assert result == 42 and isinstance(result, int), f"Expected int 42, got {result}"
    print("✓ to_d1_null(42) returns 42")
    
    # Test str
    result = to_d1_null("hello")
    assert result == "hello" and isinstance(result, str), f"Expected str 'hello', got {result}"
    print("✓ to_d1_null('hello') returns 'hello'")
    
    # Test float
    result = to_d1_null(3.14)
    assert result == 3.14 and isinstance(result, float), f"Expected float 3.14, got {result}"
    print("✓ to_d1_null(3.14) returns 3.14")
    
    # Test bool
    result = to_d1_null(True)
    assert result is True and isinstance(result, bool), f"Expected bool True, got {result}"
    print("✓ to_d1_null(True) returns True")
    
    result = to_d1_null(False)
    assert result is False and isinstance(result, bool), f"Expected bool False, got {result}"
    print("✓ to_d1_null(False) returns False")


def test_to_d1_null_with_string_undefined():
    """Test that literal string 'undefined' is converted to None"""
    # This is a critical test - sometimes APIs return the string 'undefined'
    result = to_d1_null('undefined')
    # In the new implementation, string 'undefined' should be converted to None
    assert result is None, f"Expected None for string 'undefined', got {result}"
    print("✓ to_d1_null('undefined') returns None")


def test_sanitize_for_d1():
    """Test sanitize_for_d1 function"""
    # Test None
    result = sanitize_for_d1(None)
    assert result is None, f"Expected None, got {result}"
    print("✓ sanitize_for_d1(None) returns None")
    
    # Test basic types
    result = sanitize_for_d1(42)
    assert result == 42, f"Expected 42, got {result}"
    print("✓ sanitize_for_d1(42) returns 42")
    
    result = sanitize_for_d1("test")
    assert result == "test", f"Expected 'test', got {result}"
    print("✓ sanitize_for_d1('test') returns 'test'")
    
    # Test string 'undefined'
    result = sanitize_for_d1('undefined')
    assert result is None, f"Expected None for string 'undefined', got {result}"
    print("✓ sanitize_for_d1('undefined') returns None")


def test_create_post_params():
    """Simulate the parameters passed to create_post"""
    # Simulate typical values
    usuarie_id = 123
    usuarie = "testuser"
    conteudo = "Test post content"
    imagem = None
    
    # Sanitize
    s_usuarie_id = sanitize_for_d1(usuarie_id)
    s_usuarie = sanitize_for_d1(usuarie)
    s_conteudo = sanitize_for_d1(conteudo)
    s_imagem = sanitize_for_d1(imagem)
    
    # Apply to_d1_null
    d1_usuarie_id = to_d1_null(s_usuarie_id)
    d1_usuarie = to_d1_null(s_usuarie)
    d1_conteudo = to_d1_null(s_conteudo)
    d1_imagem = to_d1_null(s_imagem)
    
    # Verify none are None except imagem
    assert d1_usuarie_id == 123, f"Expected 123, got {d1_usuarie_id}"
    assert d1_usuarie == "testuser", f"Expected 'testuser', got {d1_usuarie}"
    assert d1_conteudo == "Test post content", f"Expected 'Test post content', got {d1_conteudo}"
    assert d1_imagem is None, f"Expected None, got {d1_imagem}"
    
    print("✓ create_post parameter simulation passed")


if __name__ == "__main__":
    print("\n=== Testing to_d1_null and sanitize_for_d1 ===\n")
    
    test_to_d1_null_with_none()
    test_to_d1_null_with_basic_types()
    test_to_d1_null_with_string_undefined()
    test_sanitize_for_d1()
    test_create_post_params()
    
    print("\n=== All tests passed! ===\n")
    print("Note: These tests run in a non-Pyodide environment.")
    print("In production (Cloudflare Workers with Pyodide), to_d1_null")
    print("will convert None to JavaScript null (JS_NULL) instead.")
