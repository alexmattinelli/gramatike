#!/usr/bin/env python
"""Test script to verify caching functionality"""

import os
import sys
import time

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gramatike_app.utils import web_cache

def test_cache_basic():
    """Test basic cache set/get functionality"""
    print("Testing basic cache functionality...")
    
    # Clear any existing cache
    cache_file = web_cache.CACHE_PATH
    if os.path.exists(cache_file):
        os.remove(cache_file)
    
    # Test set and get
    test_key = "test:key1"
    test_value = {"data": "test", "number": 42}
    
    web_cache.set(test_key, test_value, ttl_seconds=10)
    result = web_cache.get(test_key)
    
    assert result == test_value, f"Expected {test_value}, got {result}"
    print("✓ Basic cache set/get works")
    
    # Test TTL expiration
    print("Testing TTL expiration (2 second TTL)...")
    web_cache.set("test:expire", "will expire", ttl_seconds=2)
    
    # Should be available immediately
    result = web_cache.get("test:expire")
    assert result == "will expire", "Cache should return value before expiration"
    print("✓ Value available before expiration")
    
    # Wait for expiration
    time.sleep(3)
    result = web_cache.get("test:expire")
    assert result is None, "Cache should return None after expiration"
    print("✓ Value expired after TTL")
    
    # Test cache key uniqueness
    print("Testing cache key uniqueness...")
    web_cache.set("key1", "value1", ttl_seconds=60)
    web_cache.set("key2", "value2", ttl_seconds=60)
    
    assert web_cache.get("key1") == "value1"
    assert web_cache.get("key2") == "value2"
    print("✓ Multiple cache keys work independently")
    
    print("\n✅ All cache tests passed!")

if __name__ == "__main__":
    test_cache_basic()
