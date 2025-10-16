# Quick Deploy Guide: Fix Resumo Truncation Error

## 🚨 Emergency Fix for Production

**Error**: `StringDataRightTruncation: value too long for type character varying(400)`

**Cause**: Database column `edu_content.resumo` is VARCHAR(400), but users are entering longer text.

**Fix**: Apply database migrations to change resumo to TEXT (unlimited).

## ⚡ Quick Steps

### 1. Backup Database (CRITICAL!)
```bash
# Production backup
pg_dump $DATABASE_URL > resumo_fix_backup_$(date +%Y%m%d_%H%M%S).sql
```

### 2. Apply Migrations
```bash
# Production environment
flask db upgrade
```

Expected migrations to apply:
- `g1h2i3j4k5l6`: VARCHAR(400) → VARCHAR(1000)
- `i8j9k0l1m2n3`: VARCHAR(1000) → VARCHAR(2000)
- `j9k0l1m2n3o4`: VARCHAR(2000) → TEXT ✅

### 3. Verify
```bash
# Check migration status
flask db current
# Should show: j9k0l1m2n3o4 (head)

# Verify column type
psql $DATABASE_URL -c "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'edu_content' AND column_name = 'resumo';"
# Should show: resumo | text
```

### 4. Test
1. Login as admin
2. Edit any educational content
3. Enter resumo with 500+ characters
4. Save → Should work! ✅

## 📊 What Changed

| Component | Before | After |
|-----------|--------|-------|
| Database Column | `resumo VARCHAR(400)` | `resumo TEXT` |
| Max Length | 400 chars | Unlimited |
| Validation | None (crashes at DB) | None (unlimited) |

## ⏱️ Deployment Time

- **Migration Time**: < 1 second (metadata change)
- **Downtime**: None required
- **Risk**: Very low (data-preserving change)

## 🔍 Verification Checklist

- [ ] Backup created
- [ ] Migrations applied successfully
- [ ] Current migration is `j9k0l1m2n3o4`
- [ ] Column type is TEXT
- [ ] Test save with 500+ character resumo works
- [ ] No errors in logs

## 🆘 Rollback (If Needed)

```bash
# Rollback to VARCHAR(2000) (will truncate >2000 char data!)
flask db downgrade j9k0l1m2n3o4

# Rollback further if needed
flask db downgrade i8j9k0l1m2n3
flask db downgrade g1h2i3j4k5l6
```

⚠️ **Warning**: Rollback will truncate any resumo > 2000 characters!

## 📝 Technical Details

See [FIX_RESUMO_VARCHAR_TRUNCATION.md](FIX_RESUMO_VARCHAR_TRUNCATION.md) for full technical documentation.

## ✅ Success Criteria

After deployment:
- ✅ Admin can save resumo with any length
- ✅ No `StringDataRightTruncation` errors
- ✅ Existing data intact
- ✅ Application functions normally

---

**Deployment Priority**: 🔴 High (blocking admin workflow)  
**Estimated Time**: 5 minutes  
**Risk Level**: 🟢 Low
