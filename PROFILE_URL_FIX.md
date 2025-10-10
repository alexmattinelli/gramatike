# Profile URL Fix - Complete Documentation

## Problem Summary

The application was experiencing 500 Internal Server Errors on the homepage (`/`) for authenticated users. The error logs showed:

```
werkzeug.routing.exceptions.BuildError: Could not build url for endpoint 'main.perfil' 
with values ['username']. Did you forget to specify values ['user_id']?
```

This error occurred on line 514 of `gramatike_app/templates/index.html`.

## Root Cause

The template was attempting to generate a URL for the user's profile using:

```jinja2
<a href="{{ url_for('main.perfil', username=current_user.username) }}" aria-label="Perfil" title="Perfil">
```

However, the `perfil` route is defined as:

```python
@bp.route('/perfil/<int:user_id>')
@login_required
def perfil(user_id):
    usuario = User.query.get_or_404(user_id)
    return render_template('perfil.html', usuario=usuario)
```

This route expects a `user_id` parameter (integer), not a `username` parameter (string). This mismatch caused Flask's URL building to fail.

## Solution

The application has a separate route for users to view their own profile:

```python
@bp.route('/perfil')
@login_required
def meu_perfil():
    return render_template('meu_perfil.html', usuario=current_user)
```

This route requires no parameters. The fix was to change the template to use this route instead:

```jinja2
<a href="{{ url_for('main.meu_perfil') }}" aria-label="Perfil" title="Perfil">
```

## Changes Made

### File: `gramatike_app/templates/index.html`

**Line 514 - Before:**
```jinja2
<a href="{{ url_for('main.perfil', username=current_user.username) }}" aria-label="Perfil" title="Perfil">
```

**Line 514 - After:**
```jinja2
<a href="{{ url_for('main.meu_perfil') }}" aria-label="Perfil" title="Perfil">
```

This is a **one-line change** that fixes the critical bug.

## Route Architecture

The application has a clear separation for profile viewing:

1. **`/perfil`** (route: `main.meu_perfil`) - Current user's own profile
   - No parameters required
   - Uses `current_user` from Flask-Login
   - Renders `meu_perfil.html`

2. **`/perfil/<int:user_id>`** (route: `main.perfil`) - View another user's profile
   - Requires `user_id` parameter (integer)
   - Queries the database for the user
   - Renders `perfil.html`

## Testing

The fix has been verified with the following tests:

1. ✅ `url_for('main.meu_perfil')` generates `/perfil` (correct)
2. ✅ `url_for('main.perfil', user_id=1)` generates `/perfil/1` (correct)
3. ✅ `url_for('main.perfil', username='test')` raises BuildError (expected)
4. ✅ Template contains the fixed pattern
5. ✅ Template does not contain the broken pattern

## Impact

- **Before:** Users experienced 500 errors when visiting the homepage
- **After:** Users can successfully access the homepage and navigate to their profile

## Related Code Patterns

Other parts of the application correctly handle profile navigation:

### JavaScript (feed.js)
```javascript
if(window.currentUser && uname===window.currentUser){ 
    window.location.href='/perfil'; // Uses meu_perfil route
    return; 
} 
fetch(`/api/usuarios/username/${uname}`)
    .then(r=>r.json())
    .then(u=>{ 
        if(u.id) window.location.href='/perfil/'+u.id;  // Uses perfil route with user_id
    });
```

This pattern correctly:
- Uses `/perfil` for the current user
- Uses `/perfil/<user_id>` for other users (after fetching their ID)

## Prevention

To prevent similar issues in the future:

1. Always verify route parameters match the route definition
2. Use `main.meu_perfil` (no params) for current user's profile
3. Use `main.perfil` with `user_id` for viewing other users' profiles
4. Never use `username` with the `main.perfil` route

## Deployment Notes

- This fix is safe to deploy immediately
- No database migrations required
- No configuration changes needed
- No impact on existing user data
- Backwards compatible with all existing functionality
