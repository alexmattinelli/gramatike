# Quick Deployment Reference: Resumo TEXT Fix

## 🚀 One-Command Deployment

```bash
# 1. Backup (MANDATORY)
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Apply migration
flask db upgrade

# 3. Verify
flask db current  # Should show: 72c95270b966
psql $DATABASE_URL -c "\d edu_content" | grep resumo  # Should show: text
```

## ⏱️ Timeline
- Backup: 1 min
- Migration: < 30 sec
- Verification: 1 min
- **Total: ~2.5 minutes**

## ✅ Success Indicators

1. Migration output shows:
   ```
   INFO  [alembic.runtime.migration] Running upgrade n9o0p1q2r3s4 -> 72c95270b966
   ✅ Successfully converted resumo column to TEXT (unlimited length)
   ```

2. Database schema shows:
   ```
   resumo | text
   ```

3. Admin can save content with 500+ character resumo without errors

## 🆘 Emergency Rollback

```bash
# Only if absolutely necessary (WARNING: May truncate data!)
flask db downgrade n9o0p1q2r3s4
```

## 📞 Need Help?

See full documentation: [RESUMO_TEXT_FINAL_FIX.md](RESUMO_TEXT_FINAL_FIX.md)
