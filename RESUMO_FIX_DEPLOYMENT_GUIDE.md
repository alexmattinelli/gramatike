# Resumo VARCHAR to TEXT Migration - Deployment Guide

## 🚨 Issue Summary

**Error in Production:**
```
ERROR:gramatike_app:Erro ao atualizar conteúdo 2: 
(psycopg2.errors.StringDataRightTruncation) value too long for type character varying(400)

Route: POST /admin/edu/content/2/update
```

**Root Cause:** The `edu_content.resumo` column is VARCHAR(400) in production, but the application model expects TEXT (unlimited). When admins try to save educational content with summaries longer than 400 characters, PostgreSQL rejects the data.

**Impact:** Admins cannot save or update educational content with detailed summaries.

## ✅ Solution

Apply database migrations to convert the `resumo` column from VARCHAR(400) to TEXT (unlimited).

## 📋 Migration Files

The following migrations fix the resumo column progressively:

1. **g1h2i3j4k5l6_increase_resumo_length.py**
   - Changes: VARCHAR(400) → VARCHAR(1000)
   - Method: Direct SQL `ALTER TABLE`

2. **i8j9k0l1m2n3_increase_resumo_to_2000.py**
   - Changes: VARCHAR(1000) → VARCHAR(2000)
   - Method: Direct SQL `ALTER TABLE`

3. **j9k0l1m2n3o4_resumo_unlimited_text.py**
   - Changes: VARCHAR(2000) → TEXT
   - Method: Direct SQL `ALTER TABLE`

4. **m8n9o0p1q2r3_ensure_resumo_text_failsafe.py**
   - Changes: Any VARCHAR → TEXT (idempotent)
   - Method: PostgreSQL `DO $$` block with conditional logic

5. **n9o0p1q2r3s4_final_resumo_text_conversion.py** ⭐ NEW
   - Changes: Any VARCHAR → TEXT (idempotent, database-agnostic)
   - Method: SQLAlchemy batch_alter_table
   - Works on: PostgreSQL, SQLite, MySQL

## 🔧 Pre-Deployment Checklist

### 1. Validate Migrations Locally

```bash
# From repository root
python3 test_resumo_migrations.py
```

Expected output:
```
✅ ALL TESTS PASSED
Ready for deployment! Run: flask db upgrade
```

### 2. Backup Production Database

**CRITICAL:** Always backup before schema changes!

```bash
# For PostgreSQL (adjust connection string)
pg_dump $DATABASE_URL > backup_resumo_fix_$(date +%Y%m%d_%H%M%S).sql

# Verify backup was created
ls -lh backup_resumo_fix_*.sql
```

### 3. Check Current Migration State

Connect to production database and check:

```sql
-- Check current migration version
SELECT version_num FROM alembic_version;

-- Check current resumo column type
SELECT column_name, data_type, character_maximum_length 
FROM information_schema.columns 
WHERE table_name = 'edu_content' AND column_name = 'resumo';
```

Expected results before migration:
- `data_type`: `character varying`
- `character_maximum_length`: `400` (or `1000`, `2000`)

## 🚀 Deployment Steps

### Option A: Deploy via Vercel/Railway (Recommended)

1. **Push code to main branch** (after PR approval)
   ```bash
   git checkout main
   git pull origin main
   git merge copilot/fix-content-update-error
   git push origin main
   ```

2. **Run migrations via deployment platform**

   For Vercel:
   ```bash
   # SSH into Vercel deployment or use Vercel CLI
   vercel env pull .env.production
   export $(cat .env.production | xargs)
   flask db upgrade
   ```

   For Railway:
   ```bash
   railway run flask db upgrade
   ```

3. **Verify migration completed**
   ```bash
   # Check migration version
   railway run flask db current
   
   # Or connect to database directly
   railway connect
   ```

### Option B: Deploy via Local Connection to Production DB

⚠️ **Use this only if you have direct database access**

1. **Set production DATABASE_URL**
   ```bash
   export DATABASE_URL="postgresql://user:password@host:port/database"
   ```

2. **Verify connection**
   ```bash
   psql $DATABASE_URL -c "SELECT version();"
   ```

3. **Run migrations**
   ```bash
   FLASK_APP=run.py flask db upgrade
   ```

4. **Expected output:**
   ```
   INFO  [alembic.runtime.migration] Running upgrade ... -> n9o0p1q2r3s4, Final resumo TEXT conversion
   ```

## 🧪 Post-Deployment Verification

### 1. Check Database Schema

```sql
-- Should show TEXT (unlimited)
SELECT column_name, data_type, character_maximum_length 
FROM information_schema.columns 
WHERE table_name = 'edu_content' AND column_name = 'resumo';
```

Expected result:
- `data_type`: `text`
- `character_maximum_length`: `NULL` (unlimited)

### 2. Test in Admin Panel

1. Login as admin: `/login`
2. Go to Admin Dashboard: `/admin`
3. Navigate to Educational Content section
4. Try to edit content with long resumo (> 400 chars)
5. Save and verify no error occurs

### 3. Test with Sample Data

```python
from gramatike_app import create_app, db
from gramatike_app.models import EduContent

app = create_app()
with app.app_context():
    # Create test content with long resumo
    content = EduContent(
        tipo='artigo',
        titulo='Test Article',
        resumo='A' * 1000,  # 1000 characters - would fail with VARCHAR(400)
        corpo='Test body content'
    )
    db.session.add(content)
    db.session.commit()
    print(f"✅ Successfully saved content with {len(content.resumo)} character resumo")
    
    # Clean up
    db.session.delete(content)
    db.session.commit()
```

## 🔄 Rollback Plan (If Needed)

If something goes wrong:

### 1. Restore Database Backup

```bash
# Stop application first!
psql $DATABASE_URL < backup_resumo_fix_YYYYMMDD_HHMMSS.sql
```

### 2. Or Downgrade Migration

```bash
# Downgrade to previous version
FLASK_APP=run.py flask db downgrade m8n9o0p1q2r3

# Or downgrade all resumo migrations
FLASK_APP=run.py flask db downgrade f6a7b8c9d0e1
```

⚠️ **Warning:** Downgrading will change resumo back to VARCHAR(2000), which may truncate long summaries!

## 📊 Migration Details

### Why Multiple Migrations?

1. **Progressive approach:** Safer to increase size gradually
2. **Backward compatibility:** Can roll back to intermediate states
3. **Multiple failsafes:** Ensures TEXT conversion even if earlier steps fail

### Why the New Migration?

The new migration `n9o0p1q2r3s4` offers:

✅ **Database-agnostic:** Works on PostgreSQL, SQLite, MySQL
✅ **Idempotent:** Safe to run multiple times
✅ **Smart checking:** Inspects current type before converting
✅ **Batch operations:** Uses SQLAlchemy's safest approach

Previous migrations used PostgreSQL-specific syntax, which works fine for production but causes issues in local SQLite development.

## 🛠️ Troubleshooting

### Error: "Target database is not up to date"

**Solution:** You need to apply earlier migrations first:
```bash
FLASK_APP=run.py flask db upgrade
```

### Error: "Circular dependency detected"

**Issue:** Earlier migrations have issues in fresh database creation.
**Solution:** This doesn't affect production upgrades, only fresh installs. For production, just run `flask db upgrade`.

### Error: "Column resumo does not exist"

**Issue:** Migration chain is incomplete.
**Solution:** Check which migrations have been applied:
```sql
SELECT * FROM alembic_version;
```

### Error: "Data would be truncated"

**Issue:** Trying to downgrade with existing long resumo values.
**Solution:** Don't downgrade, or manually truncate data first (not recommended).

## 📝 Summary

- **Issue:** VARCHAR(400) truncation error on resumo field
- **Fix:** Apply migrations to convert resumo to TEXT
- **Result:** Unlimited summary length for educational content
- **Safe:** Idempotent, database-agnostic, with multiple failsafes
- **Tested:** Validation script confirms all migrations are correct

## 🎯 Next Steps After Deployment

1. ✅ Verify no errors in production logs
2. ✅ Test admin panel functionality
3. ✅ Monitor database performance (TEXT type is efficient in PostgreSQL)
4. ✅ Update admin documentation about unlimited resumo length
5. ✅ Consider adding UI hint about recommended resumo length (UX best practice)

---

**Deployment Status:** Ready for production
**Risk Level:** Low (idempotent, failsafe migrations)
**Estimated Downtime:** None (online migration)
**Rollback Available:** Yes (with caveats about data truncation)
