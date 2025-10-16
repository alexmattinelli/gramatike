#!/usr/bin/env python3
"""
Verification script to confirm resumo TEXT migration was applied successfully.
Run this after deploying the migration to production.

Usage:
    export DATABASE_URL="postgresql://..."
    python3 verify_resumo_migration.py
"""

import os
import sys
from sqlalchemy import create_engine, text

def verify_resumo_column_type():
    """Verify that resumo column is TEXT type in the database."""
    
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable not set")
        print("Usage: export DATABASE_URL='postgresql://...' && python3 verify_resumo_migration.py")
        return False
    
    # Normalize postgres:// to postgresql://
    if database_url.startswith('postgres://'):
        database_url = 'postgresql+psycopg2://' + database_url[len('postgres://'):]
    
    print("🔍 Verifying resumo column type...")
    print(f"Database: {database_url[:50]}...")
    print()
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Query information_schema to get column type
            result = conn.execute(text("""
                SELECT 
                    column_name,
                    data_type,
                    character_maximum_length
                FROM information_schema.columns
                WHERE table_name = 'edu_content'
                  AND column_name = 'resumo'
            """))
            
            row = result.fetchone()
            
            if not row:
                print("❌ FAIL: resumo column not found in edu_content table")
                return False
            
            column_name, data_type, max_length = row
            
            print(f"Column name: {column_name}")
            print(f"Data type: {data_type}")
            print(f"Max length: {max_length if max_length else 'unlimited'}")
            print()
            
            if data_type.lower() == 'text':
                print("✅ SUCCESS: resumo column is TEXT (unlimited length)")
                print()
                print("📋 Migration Status:")
                print("   ✅ Database schema updated correctly")
                print("   ✅ Column type matches model definition")
                print("   ✅ No character limit enforced")
                print()
                print("📋 Next steps:")
                print("   1. Test saving content with 500+ character resumo in admin panel")
                print("   2. Verify no StringDataRightTruncation errors in logs")
                print("   3. Confirm admin workflow is restored")
                return True
            else:
                print(f"❌ FAIL: resumo column is still {data_type.upper()}")
                if max_length:
                    print(f"   Max length: {max_length} characters")
                print()
                print("🔧 Action required:")
                print("   1. Run: flask db upgrade")
                print("   2. Check migration logs for errors")
                print("   3. Verify current migration: flask db current")
                print("   4. Expected migration: 72c95270b966")
                return False
                
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print()
        print("Possible causes:")
        print("   - Database connection failed")
        print("   - Invalid DATABASE_URL")
        print("   - Network connectivity issues")
        print("   - Missing psycopg2 package")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Resumo TEXT Migration Verification")
    print("=" * 60)
    print()
    
    success = verify_resumo_column_type()
    
    print()
    print("=" * 60)
    
    if success:
        print("✅ VERIFICATION PASSED")
    else:
        print("❌ VERIFICATION FAILED")
    
    print("=" * 60)
    
    sys.exit(0 if success else 1)
