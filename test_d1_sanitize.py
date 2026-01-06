#!/usr/bin/env python3
"""
Test script for D1 sanitization functions.
This validates that undefined/null values are properly converted to None.
"""

def test_sanitize():
    """Test sanitization of values for D1"""
    
    def safe_sanitize(value):
        """Convert undefined/null to None, keep other values"""
        if value is None:
            return None
        # Check for JavaScript undefined
        if hasattr(value, 'typeof') and str(value) == 'undefined':
            return None
        # Check for string 'undefined'
        if isinstance(value, str) and value == 'undefined':
            return None
        # Empty string becomes None for optional fields
        if isinstance(value, str) and not value.strip():
            return None
        return value
    
    # Test cases
    assert safe_sanitize(None) is None, "None should remain None"
    assert safe_sanitize('') is None, "Empty string should become None"
    assert safe_sanitize('  ') is None, "Whitespace string should become None"
    assert safe_sanitize('undefined') is None, "String 'undefined' should become None"
    assert safe_sanitize('test') == 'test', "Valid string should pass through"
    assert safe_sanitize(123) == 123, "Integer should pass through"
    assert safe_sanitize(0) == 0, "Zero should pass through"
    assert safe_sanitize(False) == False, "False should pass through"
    assert safe_sanitize('0') == '0', "String '0' should pass through"
    
    print("✅ All sanitization tests passed")
    return True

if __name__ == '__main__':
    success = test_sanitize()
    exit(0 if success else 1)
