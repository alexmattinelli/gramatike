# Fix: Article Publication and Resumo Length Issues

## Issues Fixed

### 1. Articles Not Appearing After Publication
**Problem**: When users published articles, they did not appear in the articles listing page.

**Root Cause**: The `/artigos` route had an overly restrictive filter that only showed articles where:
- The author_id was NULL, OR
- The author was marked as admin (is_admin=True), OR  
- The author was marked as superadmin (is_superadmin=True)

This meant that if a regular user (non-admin) created an article, it would never appear on the page.

**Solution**: Removed the admin-only filter from the artigos route. Now ALL articles of type 'artigo' are displayed, regardless of who created them.

**Files Changed**:
- `gramatike_app/routes/__init__.py` (lines 1713-1742): Removed the `admin_filter` logic

### 2. Resumo (Summary) Field Too Small
**Problem**: Users could not enter long article summaries because the field was limited to 400 characters.

**Root Cause**: The `resumo` field in the `EduContent` model was defined as `String(400)`, limiting it to 400 characters.

**Solution**: 
1. Updated the model to increase `resumo` from `String(400)` to `String(1000)`
2. Created a database migration to alter the column in the database

**Files Changed**:
- `gramatike_app/models.py` (line 68): Changed resumo from String(400) to String(1000)
- `migrations/versions/g1h2i3j4k5l6_increase_resumo_length.py`: New migration file

## Testing

### Model Verification
```
✓ Resumo field type: VARCHAR(1000)
✓ Resumo field nullable: True
✓ Resumo field length: 1000
```

### Route Verification
```
✓ Artigos route found
✓ Admin filter removed from artigos route
✓ Basic artigo filter still present
```

### Migration Verification
```
✓ Migration module loaded successfully
✓ Revision: g1h2i3j4k5l6
✓ Down revision: f6a7b8c9d0e1
✓ Migration has upgrade() and downgrade() functions
```

## Deployment Instructions

1. **Apply the database migration**:
   ```bash
   flask db upgrade
   ```
   
2. **Restart the application** to load the updated code

3. **Verify**: 
   - Existing articles should now appear on the /artigos page
   - Users should be able to enter summaries up to 1000 characters

## Impact

- **Articles visibility**: All articles will now be visible, not just those created by admins
- **Resumo length**: Users can now enter summaries up to 1000 characters (increased from 400)
- **Backwards compatible**: Existing articles with resumo < 400 chars will continue to work
- **No data loss**: The migration safely expands the field without truncating existing data

## Notes

- The template textarea for resumo has no maxlength attribute, so it already supported user input > 400 chars (it was just being truncated at the database level)
- This same change benefits ALL content types (artigos, apostilas, podcasts, etc.) since they all use the EduContent model
