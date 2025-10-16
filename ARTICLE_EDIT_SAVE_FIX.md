# Fix: Article Edit Save Failure

## 🐛 Problem Reported

User reported: "Falha ao salvar: Editar Artigo" (Failure to save: Edit Article)

The user was trying to edit an article with the following data:
- **Título**: "Sobre gênero neutro em português brasileiro e os limites do sistema linguístico"
- **Autore**: "Luiz Carlos Schwindt"  
- **Resumo**: 1090 characters / 1125 bytes (UTF-8)
- **URL**: "https://doi.org/10.25189/rabralin.v19i1.1709"
- **Tópico**: "Gênero Gramatical Neutro"

The save was failing with a generic "Falha ao salvar" error message.

## 🔍 Root Causes Identified

### 1. No Error Details Shown to User
The frontend JavaScript only showed a generic "Falha ao salvar" message when the server returned an error. The actual error from the backend was not displayed, making it impossible to diagnose the issue.

### 2. No Error Handling in Backend
The `update_edu_content` route had no try/except block around `db.session.commit()`. If any database error occurred (constraint violation, data too long, etc.), it would raise an unhandled exception, returning HTTP 500 without details.

### 3. Author Field Update Logic Bug
The logic for updating the `autor` field had a subtle bug:
```python
autor = request.form.get('autor','').strip() or None
if autor is not None:
    if autor:
        extra['author'] = autor
    else:
        extra.pop('author', None)
```

If the user wanted to CLEAR the author (submit empty field), it would become `None`, skip the if block, and leave the old author in place.

### 4. No Topic Validation
The code didn't validate if the selected `topic_id` exists before trying to save. If a user selected a deleted or invalid topic, the foreign key constraint would fail with no user-friendly message.

### 5. Potential Database Migration Issue
The `resumo` field was migrated from VARCHAR(400) → VARCHAR(1000) → VARCHAR(2000) → TEXT. However:
- PostgreSQL VARCHAR is measured in BYTES, not characters
- The resumo has 1090 characters but 1125 bytes (UTF-8)
- If the migration to TEXT hasn't been applied in production, and resumo is still VARCHAR(1000), the save would fail due to data truncation

## ✅ Fixes Applied

### 1. Enhanced Error Reporting (Backend)
Added comprehensive error handling in `update_edu_content`:
```python
try:
    db.session.commit()
    return {'success': True, 'message': 'Conteúdo atualizado.'}, 200
except Exception as e:
    db.session.rollback()
    current_app.logger.error(f'Erro ao atualizar conteúdo {content_id}: {str(e)}')
    return {'success': False, 'message': f'Erro ao salvar: {str(e)}'}, 500
```

### 2. Enhanced Error Display (Frontend)
Updated the JavaScript to show the actual error message:
```javascript
if(res.ok){ 
    dlg.close(); 
    location.reload(); 
} else { 
    const data = await res.json();
    alert(data.message || 'Falha ao salvar'); 
}
```

### 3. Fixed Author Field Logic
Simplified the author update logic:
```python
autor = request.form.get('autor','').strip()
if autor:
    extra['author'] = autor
else:
    extra.pop('author', None)
```
Now it correctly handles both setting and clearing the author field.

### 4. Added Topic Validation
Added validation to check if topic exists before saving:
```python
if topic_id:
    try:
        topic_id = int(topic_id)
        from gramatike_app.models import EduTopic
        if not EduTopic.query.get(topic_id):
            return {'success': False, 'message': 'Tópico selecionado não existe.'}, 400
        c.topic_id = topic_id
    except (ValueError, TypeError):
        return {'success': False, 'message': 'ID de tópico inválido.'}, 400
else:
    c.topic_id = None
```

## 🧪 Testing

Created and ran a test script that successfully saves an article with the exact data from the problem statement:

```
✅ SUCCESS: Article updated successfully!
✅ All assertions passed!

Saved data:
  Título: Sobre gênero neutro em português brasileiro e os limites do sistema linguístico
  Autor: Luiz Carlos Schwindt
  Resumo: Neste texto, proponho uma abordagem de neutralização de gênero em português brasileiro na perspectiv...
  URL: https://doi.org/10.25189/rabralin.v19i1.1709
  Topic: Gênero Gramatical Neutro
```

The test confirms that:
- The data can be saved successfully
- All fields are stored correctly
- The resumo (1090 characters / 1125 bytes) is handled properly

## 📋 Action Required

### For Production Deployment

1. **Run database migrations**: Ensure the latest migrations are applied, especially:
   - `j9k0l1m2n3o4_resumo_unlimited_text.py` - Changes resumo to TEXT (unlimited)
   - `m8n9o0p1q2r3_ensure_resumo_text_failsafe.py` - Failsafe migration for PostgreSQL

2. **Verify resumo column type** in production database:
   ```sql
   SELECT column_name, data_type, character_maximum_length 
   FROM information_schema.columns 
   WHERE table_name = 'edu_content' AND column_name = 'resumo';
   ```
   Expected result: `data_type = 'text'` (no character_maximum_length limit)

3. **Monitor error logs**: With the new error handling, any save failures will now:
   - Log the error server-side
   - Display the actual error message to the user
   - Help identify if it's a migration issue, constraint violation, or other problem

## 📝 Files Modified

1. **gramatike_app/routes/admin.py**
   - Added error handling for db.session.commit()
   - Fixed author field update logic
   - Added topic_id validation
   - Enhanced error messages

2. **gramatike_app/templates/artigos.html**
   - Updated error handling to display actual error messages
   - Improved error UX

## 🎯 Expected Outcome

After deploying these changes:

1. **If migrations are applied**: Article edits will save successfully, even with long resumos (1000+ characters)

2. **If migrations are NOT applied**: User will see a specific error message like:
   - "Erro ao salvar: value too long for type character varying(1000)"
   - This clearly indicates the migration issue

3. **For other errors**: User will see the actual error (invalid topic, constraint violation, etc.) instead of a generic message

## 🔗 Related Documentation

- `ARTIGOS_SAVE_FIX.md` - Previous CSRF token fix for articles
- `FIX_PODCAST_RESUMO_SAVE.md` - Similar fix for podcasts
- Database migrations in `migrations/versions/*resumo*.py`
