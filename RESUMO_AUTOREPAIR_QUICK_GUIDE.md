# Quick Deploy Guide - Resumo Auto-Repair Fix

## 🚨 The Problem
```
ERROR: value too long for type character varying(400)
Route: /admin/edu/content/2/update
```

## ✅ The Solution
**Auto-repair on app startup** - converts `resumo` from VARCHAR(400) to TEXT automatically.

## 🚀 Deployment (3 Steps)

### Step 1: Deploy to Vercel
```bash
git push origin main
# Or merge this PR
```

### Step 2: Check Logs
In Vercel dashboard, check logs for:
```
Auto-reparo: convertido edu_content.resumo de VARCHAR para TEXT (PostgreSQL)
```

### Step 3: Verify Fix
1. Go to `/admin/edu/content/2/update`
2. Paste a long resumo (500+ characters):
   ```
   Neste texto, proponho uma abordagem de neutralização de gênero em português brasileiro na perspectiva do sistema linguístico. Para isso, parto de considerações sobre variação e mudança linguística, que me orientam nas questões sobre mudanças relativas à categoria de gênero gramatical na língua. São avaliados, nessa perspectiva, quatro tipos de empregos correntes de gênero inclusivo: uso de feminino marcado no caso de substantivos comuns de dois gêneros (ex. a presidenta); emprego de formas femininas e masculinas...
   ```
3. Click "Salvar"
4. ✅ Should save successfully!

## 📊 What Happens

### First Deploy (Production Database has VARCHAR(400))
```
[App Startup] → Auto-repair detects VARCHAR(400)
              → Executes: ALTER TABLE edu_content ALTER COLUMN resumo TYPE TEXT
              → Logs: "Auto-reparo: convertido edu_content.resumo de VARCHAR para TEXT"
              → ✅ Fixed!
```

### Subsequent Deploys (Already TEXT)
```
[App Startup] → Auto-repair detects TEXT
              → Logs: "resumo já é TEXT - nenhuma ação necessária"
              → ✅ No action needed (idempotent)
```

## 🔍 Troubleshooting

### If Error Persists

1. **Check Vercel Logs**:
   - Look for auto-repair messages
   - Check for any errors in auto-repair

2. **Verify Database Connection**:
   ```bash
   # In Vercel logs, check for:
   "Auto-reparo: convertido edu_content.resumo de VARCHAR para TEXT (PostgreSQL)"
   ```

3. **Manual Fix (Last Resort)**:
   ```bash
   # Connect to production database
   psql $DATABASE_URL
   
   # Check current type
   \d edu_content
   
   # If still VARCHAR, manually convert
   ALTER TABLE edu_content ALTER COLUMN resumo TYPE TEXT;
   ```

### Common Issues

**Issue**: Auto-repair not running
- **Cause**: Database connection failed on startup
- **Fix**: Check DATABASE_URL in Vercel environment variables

**Issue**: Still getting truncation error
- **Cause**: Auto-repair failed silently
- **Fix**: Check Vercel logs for "Falha auto-reparo edu_content.resumo"

**Issue**: Column already TEXT but error persists
- **Cause**: Different issue (not VARCHAR truncation)
- **Fix**: Check error message - may be another validation

## ✅ Success Indicators

You'll know it worked when:
- ✅ Vercel logs show "convertido edu_content.resumo de VARCHAR para TEXT"
- ✅ Can save resumos with 500+ characters
- ✅ Content updates work without errors
- ✅ No more StringDataRightTruncation errors

## 📝 Technical Details

**Auto-Repair Code Location**: `gramatike_app/__init__.py` (line ~220)

**How It Works**:
1. Runs on every app initialization
2. Inspects `edu_content.resumo` column type
3. If VARCHAR: converts to TEXT
4. If TEXT: skips (idempotent)
5. Logs result

**Database Support**:
- ✅ PostgreSQL: `ALTER TABLE ... ALTER COLUMN ... TYPE TEXT`
- ✅ SQLite: No conversion needed (already unlimited)
- ✅ Safe: Wrapped in try-except, won't break app startup

## 🔗 Full Documentation

See [RESUMO_AUTOREPAIR_FIX.md](RESUMO_AUTOREPAIR_FIX.md) for complete details.
