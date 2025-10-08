#!/usr/bin/env python
"""
Cache monitoring script for Gramátike
Shows cache statistics and health information
"""

import os
import sys
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gramatike_app.utils.web_cache import CACHE_PATH, _load

def format_bytes(bytes_size):
    """Format bytes to human-readable size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"

def main():
    print("=" * 60)
    print("Gramátike Cache Monitor")
    print("=" * 60)
    
    if not os.path.exists(CACHE_PATH):
        print("\n❌ Cache file not found")
        print(f"   Location: {CACHE_PATH}")
        print("\n   Cache will be created on first use.")
        return
    
    # Get file stats
    file_size = os.path.getsize(CACHE_PATH)
    modified_time = datetime.fromtimestamp(os.path.getmtime(CACHE_PATH))
    
    print(f"\n📁 Cache File: {CACHE_PATH}")
    print(f"   Size: {format_bytes(file_size)}")
    print(f"   Last Modified: {modified_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load cache data
    try:
        cache_data = _load()
        total_entries = len(cache_data)
        
        print(f"\n📊 Cache Statistics:")
        print(f"   Total Entries: {total_entries}")
        
        if total_entries == 0:
            print("\n   No cached entries found.")
            return
        
        # Analyze entries
        now = datetime.now().timestamp()
        expired = 0
        active = 0
        entries_by_prefix = {}
        
        for key, item in cache_data.items():
            expires_at = item.get('expires_at', 0)
            
            if expires_at and now > expires_at:
                expired += 1
            else:
                active += 1
            
            # Group by prefix (before first colon)
            prefix = key.split(':')[0] if ':' in key else 'other'
            entries_by_prefix[prefix] = entries_by_prefix.get(prefix, 0) + 1
        
        print(f"   Active: {active}")
        print(f"   Expired: {expired}")
        
        print(f"\n📦 Entries by Type:")
        for prefix, count in sorted(entries_by_prefix.items(), key=lambda x: x[1], reverse=True):
            bar_length = min(30, count * 2)
            bar = '█' * bar_length
            print(f"   {prefix:20} {count:3} {bar}")
        
        # Show sample entries
        print(f"\n🔍 Sample Cache Keys:")
        for i, key in enumerate(list(cache_data.keys())[:5]):
            item = cache_data[key]
            expires_at = item.get('expires_at', 0)
            ttl = max(0, expires_at - now) if expires_at else 0
            status = '✓ Active' if ttl > 0 else '✗ Expired'
            print(f"   {i+1}. {key[:50]:50} {status} (TTL: {int(ttl)}s)")
        
        if total_entries > 5:
            print(f"   ... and {total_entries - 5} more")
        
        print("\n" + "=" * 60)
        
    except json.JSONDecodeError as e:
        print(f"\n❌ Error reading cache file: {e}")
        print("   Cache file may be corrupted.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
