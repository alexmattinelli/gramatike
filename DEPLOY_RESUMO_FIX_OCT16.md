# URGENT: Deploy Resumo TEXT Migration to Fix Production Error

## 🚨 Current Status

**Production Error**: Active (Oct 16, 2025)
```
ERROR: sqlalchemy.exc.DataError: (psycopg2.errors.StringDataRightTruncation) 
value too long for type character varying(400)
Route: /admin/edu/content/2/update
```

**Impact**: Admins cannot save educational content with resumo (summary) longer than 400 characters.

## 📋 Quick Fix (5 minutes)

### Step 1: Connect to Production Database

```bash
# Export your production database URL
export DATABASE_URL="postgresql://user:password@host:port/database"

# Or for Vercel/Railway, get it from their dashboard
```

### Step 2: Backup Database (CRITICAL!)

```bash
# Create backup before any changes
pg_dump $DATABASE_URL > resumo_fix_backup_$(date +%Y%m%d_%H%M%S).sql

# Verify backup was created
ls -lh resumo_fix_backup_*.sql
```

### Step 3: Apply Migrations

```bash
# From your local machine with DATABASE_URL set
flask db upgrade

# Expected output:
# INFO  [alembic.runtime.migration] Running upgrade f6a7b8c9d0e1 -> g1h2i3j4k5l6, increase resumo length to 1000
# INFO  [alembic.runtime.migration] Running upgrade g1h2i3j4k5l6 -> h7i8j9k0l1m2, add palavra do dia
# INFO  [alembic.runtime.migration] Running upgrade h7i8j9k0l1m2 -> x56rn24y9zwi, add word exclusion
# INFO  [alembic.runtime.migration] Running upgrade x56rn24y9zwi -> z9a8b7c6d5e4, rename quemsoeu to quemsouleu
# INFO  [alembic.runtime.migration] Running upgrade h7i8j9k0l1m2 -> i8j9k0l1m2n3, increase resumo length to 2000
# INFO  [alembic.runtime.migration] Running upgrade i8j9k0l1m2n3, z9a8b7c6d5e4 -> j9k0l1m2n3o4, change resumo to unlimited text
# INFO  [alembic.runtime.migration] Running upgrade j9k0l1m2n3o4 -> m8n9o0p1q2r3, ensure resumo text failsafe
# NOTICE: Successfully converted resumo column to TEXT
```

### Step 4: Verify Fix

```bash
# Check current migration head
flask db current
# Should show: m8n9o0p1q2r3 (head)

# Verify column type changed
psql $DATABASE_URL -c "\d edu_content" | grep resumo
# Should show: resumo | text |
```

### Step 5: Test in Production

1. Login to https://www.gramatike.com.br/admin
2. Navigate to Gramátike Edu
3. Edit content ID 2 (the one that failed)
4. Enter a long resumo (500+ characters)
5. Click "Salvar"
6. ✅ Should save successfully!

## 🔍 What This Fix Does

### Migrations Applied

| Migration | Change | Notes |
|-----------|--------|-------|
| `g1h2i3j4k5l6` | VARCHAR(400) → VARCHAR(1000) | First expansion |
| `h7i8j9k0l1m2` | No resumo change | Adds palavra_do_dia |
| `i8j9k0l1m2n3` | VARCHAR(1000) → VARCHAR(2000) | Second expansion |
| `x56rn24y9zwi` | No resumo change | Word exclusion feature |
| `z9a8b7c6d5e4` | No resumo change | Column rename |
| `j9k0l1m2n3o4` | VARCHAR(2000) → TEXT | **Unlimited text** |
| `m8n9o0p1q2r3` | Failsafe: Ensure TEXT | **Idempotent safety check** |

### Database Schema Change

**Before**:
```sql
resumo | character varying(400)
```

**After**:
```sql
resumo | text  -- UNLIMITED LENGTH
```

## ✅ Safety Guarantees

- ✅ **No Data Loss**: All migrations preserve existing data
- ✅ **Idempotent**: Safe to run multiple times
- ✅ **No Downtime**: Schema change is instant (metadata only)
- ✅ **Reversible**: Downgrade functions included (with truncation warning)
- ✅ **Tested**: Migration chain verified and syntax checked

## 🆘 Troubleshooting

### Issue: "alembic_version table not found"
**Solution**: Initialize migrations first:
```bash
flask db init  # Only if migrations folder doesn't exist
flask db stamp head  # Set current version
```

### Issue: "Multiple heads detected"
**Solution**: The merge migration `j9k0l1m2n3o4` will resolve this automatically.

### Issue: Migration fails at merge step
**Cause**: Production might be on only one branch
**Solution**: Alembic will automatically apply both branches before merging

### Issue: "Column already is TEXT"
**Success!** The failsafe migration detects this and reports:
```
NOTICE: resumo column is already TEXT - no action needed
```

## 📊 Expected Timeline

| Step | Duration | Risk |
|------|----------|------|
| Database Backup | 1 min | None |
| Migration Execution | < 30 sec | Very Low |
| Verification | 1 min | None |
| Testing | 2 min | None |
| **Total** | **~5 min** | **🟢 Low** |

## 🔄 Rollback Plan (If Needed)

⚠️ Only use if migrations cause unexpected issues:

```bash
# Rollback to previous state (truncates resumo > 2000 chars!)
flask db downgrade m8n9o0p1q2r3

# Full rollback to VARCHAR(400) (truncates resumo > 400 chars!)
flask db downgrade f6a7b8c9d0e1
```

**WARNING**: Rollback will truncate any resumo exceeding the target length!

## 📝 Technical Details

### Why This Works

1. **PostgreSQL ALTER TABLE**: Handles VARCHAR → TEXT conversion automatically
2. **Idempotent SQL**: Uses `DO $$ BEGIN ... END $$;` blocks to check state first
3. **Merge Migration**: Properly combines two development branches
4. **Failsafe Layer**: Extra migration ensures TEXT even if earlier steps had issues

### Migration Dependencies

```
                    f6a7b8c9d0e1 (promotion_table)
                          ↓
                    g1h2i3j4k5l6 (VARCHAR 400→1000)
                          ↓
                    h7i8j9k0l1m2 (palavra_do_dia)
                          ↓
           ┌──────────────┴───────────────┐
           ↓                               ↓
    i8j9k0l1m2n3                  x56rn24y9zwi → z9a8b7c6d5e4
 (VARCHAR 1000→2000)               (word_exclusion, rename)
           └──────────────┬───────────────┘
                          ↓
                  j9k0l1m2n3o4 (VARCHAR→TEXT)
                          ↓
                  m8n9o0p1q2r3 (failsafe) ✅
```

## ✨ After Deployment

### Expected Behavior
- ✅ Admins can save resumo of **any length** (500, 1000, 5000+ characters)
- ✅ No more `StringDataRightTruncation` errors
- ✅ Existing content unchanged
- ✅ Form textarea already supports unlimited input (no frontend changes needed)

### Verification Checklist
- [ ] Backup created and verified
- [ ] All migrations applied successfully
- [ ] Current migration is `m8n9o0p1q2r3`
- [ ] Database column type is `text`
- [ ] Test save with 500+ character resumo works
- [ ] No errors in production logs
- [ ] Admin workflow restored

## 📚 Related Documentation

- [FIX_RESUMO_VARCHAR_TRUNCATION.md](FIX_RESUMO_VARCHAR_TRUNCATION.md) - Original analysis
- [DEPLOY_RESUMO_FIX.md](DEPLOY_RESUMO_FIX.md) - Previous deployment guide
- [PR_SUMMARY_RESUMO_TRUNCATION_FIX.md](PR_SUMMARY_RESUMO_TRUNCATION_FIX.md) - PR summary

---

**Priority**: 🔴 **URGENT** (Production blocker)  
**Deployment Risk**: 🟢 **Low**  
**Data Loss Risk**: 🟢 **None**  
**Estimated Time**: ⏱️ **5 minutes**

**Deploy immediately to restore admin functionality.**
