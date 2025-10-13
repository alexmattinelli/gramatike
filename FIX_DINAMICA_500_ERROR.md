# Fix: 500 Internal Server Error on "Quem sou eu?" Dynamic

## Problem
Users were unable to access the "Quem sou eu?" dynamic at `/dinamicas/11`, receiving an "Erro interno no servidor" (500 Internal Server Error).

## Root Cause
The template `dinamica_view.html` was directly accessing dictionary keys from the `cfg` object without using safe access methods:

```jinja2
{# BEFORE - Unsafe direct access #}
{{ cfg.items|length }}
{{ cfg.questao_tipo }}
{{ cfg.options }}
```

When these keys didn't exist in the config JSON (e.g., due to misconfiguration or empty config), Python would raise a `KeyError`, causing a 500 error.

## Solution
Updated the template to use Jinja2's `.get()` method with default values, following the pattern already used elsewhere in the same template:

```jinja2
{# AFTER - Safe access with defaults #}
{{ cfg.get('items', [])|length }}
{{ cfg.get('questao_tipo', '') }}
{{ cfg.get('options', []) }}
```

## Changes Made

### File: `gramatike_app/templates/dinamica_view.html`

1. **Poll dynamic - User response section (lines 117-118)**
   - Added: `{% set options_list = cfg.get('options', []) %}`
   - Changed: `cfg.options` → `options_list`

2. **Poll dynamic - Results section (lines 125, 128)**
   - Added: `{% set options_list = cfg.get('options', []) %}`
   - Changed: `cfg.options` → `options_list`

3. **Poll dynamic - Form section (lines 157-158)**
   - Added: `{% set options_list = cfg.get('options', []) %}`
   - Changed: `cfg.options` → `options_list`

4. **Quemsoeu dynamic - Instructions section (line 237)**
   - Changed: `cfg.items|length` → `cfg.get('items', [])|length`
   - Changed: `cfg.questao_tipo` → `cfg.get('questao_tipo', '')`

5. **Quemsoeu dynamic - JavaScript section (lines 250-251)**
   - Changed: `cfg.items` → `cfg.get('items', [])`
   - Changed: `cfg.questao_tipo` → `cfg.get('questao_tipo', '')`

## Testing

### Syntax Validation
✅ Template compiles without errors
✅ No Jinja2 syntax errors

### Config Access Patterns
Tested with various config states:
- ✅ Empty config: `{}`
- ✅ Partial config (missing items): `{'questao_tipo': 'gênero', 'moral': 'Test'}`
- ✅ Full config with all keys present
- ✅ Poll with empty config
- ✅ Poll with options

All patterns now return safe defaults (empty list `[]` or empty string `''`) when keys are missing.

## Impact

### Before
- ❌ Dynamic with missing config keys → 500 error
- ❌ Users cannot access the dynamic
- ❌ No fallback or graceful degradation

### After
- ✅ Dynamic with missing config keys → Renders successfully
- ✅ Shows empty values or zero items gracefully
- ✅ No errors, better user experience

## Related Files
- `gramatike_app/templates/dinamica_view.html` - Fixed
- `gramatike_app/templates/dinamica_admin.html` - Already uses safe access
- `gramatike_app/templates/dinamica_edit.html` - Already uses safe access

## Prevention
This fix follows the existing pattern already used in the same template (line 166, 203, 220) where `.get()` is used for safe dictionary access. All future template updates should follow this pattern.

## Deployment
No database migrations or environment variable changes required. The fix is purely template-based and can be deployed immediately.
