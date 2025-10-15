# Article Form Simplification - Remove "Corpo Principal" Field

## Issue
The admin panel had a "Corpo principal" (main body) textarea field when publishing articles, but this field was not being used or displayed in the article pages. Only the "resumo" (summary) field is used for article content.

## Solution
Removed the unnecessary "corpo principal" textarea from the article publication form in the admin dashboard.

## Changes Applied

### Before
```html
<!-- admin/dashboard.html - Article Publication Form -->
<h3>Publicar Artigo</h3>
<form method="POST" action="{{ url_for('admin.edu_publicar') }}">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() if csrf_token is defined else '' }}" />
    <input type="hidden" name="tipo" value="artigo" />
    <input name="titulo" placeholder="Título" required />
    <input name="autor" placeholder="Autore (opcional)" />
    <select name="topic_id">...</select>
    <input name="url" placeholder="Link (fonte)" />
    <textarea name="resumo" placeholder="Resumo"></textarea>
    <textarea name="corpo" placeholder="Corpo principal"></textarea>  <!-- ❌ REMOVED -->
    <button type="submit">Publicar</button>
</form>
```

### After
```html
<!-- admin/dashboard.html - Article Publication Form -->
<h3>Publicar Artigo</h3>
<form method="POST" action="{{ url_for('admin.edu_publicar') }}">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() if csrf_token is defined else '' }}" />
    <input type="hidden" name="tipo" value="artigo" />
    <input name="titulo" placeholder="Título" required />
    <input name="autor" placeholder="Autore (opcional)" />
    <select name="topic_id">...</select>
    <input name="url" placeholder="Link (fonte)" />
    <textarea name="resumo" placeholder="Resumo"></textarea>  <!-- ✅ Only resumo -->
    <button type="submit">Publicar</button>
</form>
```

## Form Fields (After Simplification)

| Field | Type | Required | Purpose |
|-------|------|----------|---------|
| **Título** | Text input | Yes | Article title |
| **Autore** | Text input | No | Author name (optional) |
| **Tópico** | Dropdown | No | Category/topic selection |
| **Link (fonte)** | Text input | No | Source URL |
| **Resumo** | Textarea | No | Article summary/content |

## Why This Change?

### 1. Eliminates Confusion
- Admins no longer need to decide between "resumo" and "corpo principal"
- Clear single field for article content

### 2. Database Alignment
- The `EduContent.resumo` field supports up to 2000 characters
- No separate "corpo" field exists in the model
- Articles use only `resumo` for content display

### 3. UI Consistency
- `artigos.html` displays only the `resumo` field
- Edit modal has only `resumo` textarea
- Publication form now matches the display/edit behavior

### 4. Cleaner Workflow
- **Before**: Fill "resumo" → Also fill "corpo"? → Confusion
- **After**: Fill "resumo" → Done ✅

## Article Display Behavior

### Resumo Display Logic (Already Implemented)
```python
# In artigos.html template
{% set resumo_limit = 300 %}
{% if c.resumo|length > resumo_limit %}
    <!-- Show truncated with "Ver mais" link -->
    {{ c.resumo[:300] }}... [Ver mais]
{% else %}
    <!-- Show full resumo -->
    {{ c.resumo }}
{% endif %}
```

### Resumo Capacity
- **Database**: VARCHAR(2000) - supports up to 2000 characters
- **Edit Form**: No maxlength restriction on textarea
- **Display**: Truncates at 300 chars with "Ver mais" expansion

## Files Modified
- ✅ `gramatike_app/templates/admin/dashboard.html` (line 732 removed)

## Testing Checklist
- [x] "Corpo principal" field removed from article publication form
- [x] Form still submits successfully with only "resumo"
- [x] Published articles display correctly in artigos.html
- [x] Edit functionality works with resumo field only
- [x] No references to "corpo" in article-related templates

## Related Fixes
This change complements the existing fixes:
1. ✅ CSRF token corrections (PR_SUMMARY_ARTIGOS_FIX.md)
2. ✅ Resumo truncation with "Ver mais" (RESUMO_TRUNCATION_FIX.md)
3. ✅ Resumo length increased to 2000 chars (ARTICLE_PUBLICATION_FIX.md)

## Result
A cleaner, more intuitive article publication form that aligns perfectly with how articles are stored and displayed in the application.
