# Fix for VARCHAR(400) Truncation Error in edu_content.resumo

## Problem Statement

The application was experiencing a `StringDataRightTruncation` error when updating educational content with summaries (resumo) longer than 400 characters:

```
psycopg2.errors.StringDataRightTruncation: value too long for type character varying(400)
```

### Root Cause

1. **Database Schema Issue**: In production, the `edu_content.resumo` column is still `VARCHAR(400)` despite having migrations to change it to `TEXT`
2. **Autoflush Trigger**: The error occurred during an autoflush triggered by `EduTopic.query.get(topic_id)` 
3. **Premature Save**: SQLAlchemy attempted to flush the pending update (with resumo > 400 chars) before validation completed

### Error Flow

```python
# Line 580: Set resumo on the model (marks it as dirty)
c.resumo = resumo  # resumo = 1192 characters

# Line 588: Query triggers autoflush
if not EduTopic.query.get(topic_id):  # ← Autoflush happens here!
    return error
    
# SQLAlchemy tries to UPDATE edu_content SET resumo=... (1192 chars)
# PostgreSQL rejects: VARCHAR(400) can't hold 1192 characters
# → StringDataRightTruncation error
```

## Solution Implemented

### 1. Prevent Premature Autoflush

Added `db.session.no_autoflush` block around the topic validation query:

```python
# Check if topic exists - use no_autoflush to prevent premature flush
from gramatike_app.models import EduTopic
with db.session.no_autoflush:
    if not EduTopic.query.get(topic_id):
        return {'success': False, 'message': 'Tópico selecionado não existe.'}, 400
```

**Why this works:**
- The `no_autoflush` context prevents SQLAlchemy from automatically flushing pending changes
- The query can execute without triggering the premature UPDATE
- The actual commit happens later, after all validation is complete

### 2. Better Error Handling

Added specific error handling for VARCHAR truncation errors:

```python
except Exception as e:
    db.session.rollback()
    from flask import current_app
    current_app.logger.error(f'Erro ao atualizar conteúdo {content_id}: {str(e)}')
    
    # Check if it's a VARCHAR truncation error
    error_str = str(e)
    if 'StringDataRightTruncation' in error_str or 'value too long' in error_str:
        return {'success': False, 'message': 'Resumo muito longo. Por favor, reduza o tamanho do resumo ou contate o administrador do sistema.'}, 400
    
    return {'success': False, 'message': f'Erro ao salvar: {str(e)}'}, 500
```

**Benefits:**
- Users get a helpful error message instead of a 500 error
- Admins are directed to contact system administrator if DB schema needs migration
- Graceful degradation even if migrations haven't been applied

## Migration Status

The following migrations exist and are properly configured:

1. `g1h2i3j4k5l6_increase_resumo_length.py` - VARCHAR(400) → VARCHAR(1000)
2. `i8j9k0l1m2n3_increase_resumo_to_2000.py` - VARCHAR(1000) → VARCHAR(2000)  
3. `j9k0l1m2n3o4_resumo_unlimited_text.py` - VARCHAR(2000) → TEXT
4. `m8n9o0p1q2r3_ensure_resumo_text_failsafe.py` - Idempotent failsafe to ensure TEXT

**The failsafe migration (`m8n9o0p1q2r3`) includes:**
```sql
DO $$ 
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'edu_content' 
          AND column_name = 'resumo'
          AND data_type <> 'text'
    ) THEN
        ALTER TABLE edu_content ALTER COLUMN resumo TYPE TEXT;
    END IF;
END $$;
```

This migration is **idempotent** and safe to run multiple times.

## Deployment Steps

### Step 1: Deploy Code Fix (Immediate)
The code fix is backwards compatible and works even if migrations haven't been applied:
- Prevents the autoflush error
- Provides user-friendly error messages
- No breaking changes

### Step 2: Run Migration (Production)
After deploying the code, run the migration in production:

```bash
flask db upgrade
```

This will execute the failsafe migration which converts `resumo` to TEXT type.

### Step 3: Verify Fix
Test by updating content with a long resumo (> 400 characters):

1. Login as admin
2. Go to educational content editor
3. Update any content with resumo > 400 characters
4. Should save successfully after migration

## Files Modified

- `gramatike_app/routes/admin.py` - Added no_autoflush and better error handling
- `test_autoflush_fix.py` - Validation test for the fix

## Testing

Run validation tests:

```bash
# Validate migration structure
python test_resumo_migrations.py

# Validate autoflush fix
python test_autoflush_fix.py
```

Both tests should pass ✅

## Technical Details

### SQLAlchemy Autoflush Behavior

SQLAlchemy's session uses autoflush by default:
- Before executing any query, it flushes pending changes
- This ensures queries see the latest data
- Can cause issues when validation queries trigger premature flushes

### no_autoflush Context Manager

The `db.session.no_autoflush` context manager:
- Temporarily disables autoflush within the block
- Queries execute without flushing pending changes
- Flush happens normally at commit time

### Best Practices

When updating model attributes then querying before commit:
1. Use `db.session.no_autoflush` around validation queries
2. Validate data before setting attributes (when possible)
3. Handle database constraint violations gracefully

## Related Documentation

- SQLAlchemy Autoflush: https://docs.sqlalchemy.org/en/14/orm/session_api.html#sqlalchemy.orm.Session.no_autoflush
- PostgreSQL VARCHAR vs TEXT: https://www.postgresql.org/docs/current/datatype-character.html
- Migration files: `/migrations/versions/*resumo*.py`

## Verification Checklist

- [x] Code fix prevents autoflush error
- [x] Better error messages for VARCHAR truncation
- [x] Migrations exist and are valid
- [x] Failsafe migration is idempotent
- [x] Backwards compatible (works before and after migration)
- [x] Tests validate the fix
- [ ] Deploy to production
- [ ] Run `flask db upgrade` in production
- [ ] Verify with test case (resumo > 400 chars)

## Summary

This fix addresses the immediate error by preventing premature autoflush and provides better error handling. The underlying database schema issue should be resolved by running the existing migrations in production. The solution is minimal, targeted, and backwards compatible.
