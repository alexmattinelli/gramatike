# Preventing D1_TYPE_ERROR in Cloudflare Workers Python

## Overview

When using Cloudflare D1 database with Python in the Pyodide/Workers environment, you may encounter this error:

```
Error: D1_TYPE_ERROR: Type 'undefined' not supported for value 'undefined'
```

This error occurs when JavaScript `undefined` values are passed to D1's `.bind()` method. D1 expects valid types (string, number, boolean, null, etc.) but cannot handle `undefined`.

## Root Cause

In the Pyodide environment (Python running in Cloudflare Workers), there's a Foreign Function Interface (FFI) boundary between Python and JavaScript. When Python `None` values cross this boundary, they can be converted to JavaScript `undefined` instead of JavaScript `null`. D1 cannot handle `undefined` values.

**Important**: Even values that are NOT `None` in Python can become `undefined` when crossing the FFI boundary under certain conditions. This is why we must wrap ALL parameters before passing to `.bind()`.

## Solution: The to_d1_null Pattern

### Step 1: Import the helper function

The `to_d1_null()` function is defined in `gramatike_d1/db.py`:

```python
from js import null as JS_NULL

def to_d1_null(value):
    """Converts Python None and JavaScript undefined to JavaScript null for D1 queries."""
    if value is None:
        return JS_NULL
    # Check string representation for 'undefined' (no need to import undefined)
    if str(value) == 'undefined':
        return JS_NULL
    return value
```

**Key Enhancement**: The function now detects and converts both Python `None` AND JavaScript `undefined` values to `JS_NULL`, providing complete protection against D1_TYPE_ERROR. It uses string checking to detect undefined without needing to import it.

### Step 2: ALWAYS wrap ALL bind parameters

**❌ WRONG** (can cause D1_TYPE_ERROR):
```python
s_usuario_id, s_conteudo = sanitize_params(usuario_id, conteudo)
await db.prepare("""
    INSERT INTO post (usuario_id, conteudo) VALUES (?, ?)
""").bind(s_usuario_id, s_conteudo).run()
```

**✅ CORRECT** (prevents D1_TYPE_ERROR):
```python
s_usuario_id, s_conteudo = sanitize_params(usuario_id, conteudo)

# Call to_d1_null() DIRECTLY in bind() to avoid FFI boundary issues
await db.prepare("""
    INSERT INTO post (usuario_id, conteudo) VALUES (?, ?)
""").bind(to_d1_null(s_usuario_id), to_d1_null(s_conteudo)).run()
```

**Alternative** (also correct):
```python
s_usuario_id, s_conteudo = sanitize_params(usuario_id, conteudo)

# Wrap ALL parameters with to_d1_null()
d1_usuario_id = to_d1_null(s_usuario_id)
d1_conteudo = to_d1_null(s_conteudo)

await db.prepare("""
    INSERT INTO post (usuario_id, conteudo) VALUES (?, ?)
""").bind(d1_usuario_id, d1_conteudo).run()
```

### Step 3: Alternative - Use d1_params()

For functions with many parameters, use `d1_params()` which sanitizes AND converts in one call:

```python
# Sanitize and convert all parameters at once
params = d1_params(usuario_id, conteudo, imagem, created_at)

await db.prepare("""
    INSERT INTO post (usuario_id, conteudo, imagem, created_at)
    VALUES (?, ?, ?, ?)
""").bind(*params).run()
```

## Best Practices

### 1. For INSERT operations
```python
async def create_post(db, usuario_id, conteudo, imagem=None):
    # Sanitize first
    s_usuario_id, s_conteudo, s_imagem = sanitize_params(usuario_id, conteudo, imagem)
    
    # Call to_d1_null() DIRECTLY in bind() to prevent FFI boundary issues
    result = await db.prepare("""
        INSERT INTO post (usuario_id, conteudo, imagem)
        VALUES (?, ?, ?)
        RETURNING id
    """).bind(
        to_d1_null(s_usuario_id),
        to_d1_null(s_conteudo),
        to_d1_null(s_imagem)
    ).first()
    
    return safe_get(result, 'id')
```

### 2. For UPDATE operations
```python
async def update_post(db, post_id, conteudo):
    s_post_id, s_conteudo = sanitize_params(post_id, conteudo)
    
    # Call to_d1_null() directly in bind()
    await db.prepare("""
        UPDATE post SET conteudo = ? WHERE id = ?
    """).bind(to_d1_null(s_conteudo), to_d1_null(s_post_id)).run()
```

### 3. For DELETE operations
```python
async def delete_post(db, post_id):
    s_post_id = sanitize_for_d1(post_id)
    
    # Call to_d1_null() directly in bind()
    await db.prepare("""
        DELETE FROM post WHERE id = ?
    """).bind(to_d1_null(s_post_id)).run()
```

### 4. For SELECT with parameters
```python
async def get_user_posts(db, user_id, limit=10):
    s_user_id = sanitize_for_d1(user_id)
    s_limit = sanitize_for_d1(limit) or 10
    
    # Call to_d1_null() directly in bind()
    result = await db.prepare("""
        SELECT * FROM post WHERE usuario_id = ? LIMIT ?
    """).bind(to_d1_null(s_user_id), to_d1_null(s_limit)).all()
    
    return [safe_dict(row) for row in result.results] if result.results else []
```

### 5. Dynamic SQL with multiple parameters
```python
async def update_user_profile(db, user_id, **kwargs):
    allowed = ['nome', 'bio', 'foto_perfil']
    updates = {k: sanitize_for_d1(v) for k, v in kwargs.items() if k in allowed}
    updates = {k: v for k, v in updates.items() if v is not None}
    
    if not updates:
        return False
    
    set_clause = ', '.join(f"{k} = ?" for k in updates.keys())
    
    # Wrap ALL values including the user_id
    values = [to_d1_null(v) for v in updates.values()]
    values.append(to_d1_null(sanitize_for_d1(user_id)))
    
    await db.prepare(f"""
        UPDATE user SET {set_clause} WHERE id = ?
    """).bind(*values).run()
    
    return True
```

## Common Mistakes to Avoid

### ❌ Mistake 1: Only wrapping optional parameters
```python
# WRONG - only d1_imagem is wrapped
d1_imagem = to_d1_null(s_imagem)
await db.prepare("...").bind(s_usuario_id, s_conteudo, d1_imagem, s_usuario_id).run()
```

### ❌ Mistake 2: Forgetting to wrap repeated parameters
```python
# WRONG - s_usuario_id is used twice but only wrapped once
d1_usuario_id = to_d1_null(s_usuario_id)
await db.prepare("...").bind(d1_usuario_id, s_conteudo, s_usuario_id).run()
```

### ❌ Mistake 3: Not wrapping parameters at all
```python
# WRONG - no to_d1_null() used
s_usuario_id, s_conteudo = sanitize_params(usuario_id, conteudo)
await db.prepare("...").bind(s_usuario_id, s_conteudo).run()
```

### ✅ Correct: Call to_d1_null() directly in bind()
```python
# CORRECT - Recommended approach
s_usuario_id, s_conteudo, s_imagem = sanitize_params(usuario_id, conteudo, imagem)
await db.prepare("...").bind(
    to_d1_null(s_usuario_id),
    to_d1_null(s_conteudo),
    to_d1_null(s_imagem),
    to_d1_null(s_usuario_id)
).run()
```

## Why This Pattern is Necessary

1. **Python None → JavaScript undefined**: When Python `None` crosses the Pyodide FFI boundary, it can become JavaScript `undefined`
2. **Values can become undefined**: Even non-None values can unexpectedly become `undefined` when crossing the FFI boundary
3. **D1 rejects undefined**: D1's `.bind()` method throws `D1_TYPE_ERROR` when it receives `undefined`
4. **JavaScript null works**: D1 accepts JavaScript `null` as a valid SQL NULL value
5. **Enhanced detection**: The `to_d1_null()` function now detects BOTH Python `None` and JavaScript `undefined`, converting both to `JS_NULL`

## Helper Functions Reference

### `to_d1_null(value)`
- Converts Python `None` AND JavaScript `undefined` to JavaScript `null` (in Pyodide environment)
- Checks value identity for `None`
- Checks string representation for `'undefined'` (no need to import undefined)
- Returns the original value if not None/undefined
- Use this for individual parameters

### `sanitize_for_d1(value)`
- Sanitizes a single value to prevent undefined/JsProxy issues
- Converts JavaScript undefined to Python None
- Returns Python-native types (str, int, float, None)

### `sanitize_params(*args)`
- Sanitizes multiple parameters at once
- Returns tuple of sanitized Python values (not converted to JS null)

### `d1_params(*args)`
- **RECOMMENDED**: Sanitizes AND converts to D1-safe values
- Combines `sanitize_for_d1()` + `to_d1_null()`
- Returns tuple ready for `.bind(*params)`

## Testing Your Changes

After updating code to use this pattern:

1. Check logs for sanitization warnings
2. Test with actual `None` values
3. Test with edge cases (empty strings, zeros, etc.)
4. Monitor production for D1_TYPE_ERROR

## Summary

**Golden Rule**: ALWAYS wrap ALL parameters with `to_d1_null()` when passing to `.bind()`

**Best Practice**: Call `to_d1_null()` directly in the `.bind()` call to minimize FFI boundary crossings:
```python
await db.prepare("...").bind(to_d1_null(param1), to_d1_null(param2)).run()
```

Whether a parameter is required or optional, None or not None, wrap it with `to_d1_null()` to ensure it safely crosses the Python-JavaScript FFI boundary.

For quick implementation: Use `d1_params()` to sanitize and convert all parameters in one call.
