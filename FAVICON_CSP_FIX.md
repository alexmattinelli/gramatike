# Favicon 404 and CSP Report Fix

## Problem

The production logs showed two issues:

1. **Favicon 404 Errors**: Browsers automatically request `/favicon.ico` and `/favicon.png` from the root path, but the app only served these files from `/static/favicon.ico` and `/static/favicon.png`, resulting in 404 errors.

2. **CSP Report Spam**: The CSP report endpoint logged every single report, including empty payloads `{}`, creating excessive noise in the logs. These empty reports were likely caused by browser extensions or the favicon CSP violations themselves.

### Example Logs

**Favicon 404s:**
```
GET /favicon.png HTTP/1.1" 404 -
GET /favicon.ico HTTP/1.1" 404 -
```

**CSP Report Spam:**
```
WARNING:gramatike_app:CSP report: {}
WARNING:gramatike_app:CSP report: {}
WARNING:gramatike_app:CSP report: {}
...
```

## Root Cause

### Favicon 404s
- Browsers automatically request favicons from the root path (`/favicon.ico`, `/favicon.png`) when a page loads
- Templates correctly referenced favicons using `url_for('static', filename='favicon.ico')` → `/static/favicon.ico`
- However, browsers also make automatic requests to root-level paths, which were not handled
- Flask only had the `/static/<path:filename>` route for serving static files

### CSP Report Spam
- The CSP report endpoint logged every report unconditionally
- Many browsers/extensions send empty CSP reports `{}`
- This created unnecessary log noise without providing useful information

## Solution

### 1. Favicon Routes

Added two new routes to serve favicons from the root path:

```python
# gramatike_app/routes/__init__.py

@bp.route('/favicon.ico')
def favicon_ico():
    """Serve favicon.ico from root path (browsers request this automatically)"""
    return redirect(url_for('static', filename='favicon.ico'))

@bp.route('/favicon.png')
def favicon_png():
    """Serve favicon.png from root path (browsers request this automatically)"""
    return redirect(url_for('static', filename='favicon.png'))
```

**How it works:**
- Browser requests `/favicon.ico` or `/favicon.png`
- Route returns 302 redirect to `/static/favicon.ico` or `/static/favicon.png`
- Flask serves the actual file from the static folder
- Result: 200 OK instead of 404

### 2. CSP Report Logging Fix

Modified the CSP report endpoint to only log non-empty reports:

```python
# gramatike_app/routes/__init__.py

@bp.route('/api/csp-report', methods=['POST'])
def api_csp_report():
    try:
        payload = request.get_json(silent=True) or {}
        # Only log non-empty reports to reduce noise
        if payload:
            current_app.logger.warning(f"CSP report: {payload}")
    except Exception as _e:
        current_app.logger.warning(f"CSP report parse failed: {_e}")
    return ('', 204)
```

**How it works:**
- Empty payloads `{}` are ignored (no log entry)
- Only actual CSP violations with data are logged
- Invalid JSON is handled gracefully (no crash)

## Files Modified

### Code Changes
- `gramatike_app/routes/__init__.py`:
  - Added `/favicon.ico` route (line 2489)
  - Added `/favicon.png` route (line 2494)
  - Modified CSP report logging to skip empty payloads (line 773)

### Tests Added
- `tests/test_static_files.py`:
  - Added `test_favicon_root_routes()` to verify root-level favicon access
  
- `tests/test_csp_report.py` (NEW):
  - `test_csp_report_empty_payload()` - verifies empty reports are not logged
  - `test_csp_report_non_empty_payload()` - verifies real violations are logged
  - `test_csp_report_invalid_json()` - verifies graceful handling of invalid JSON

## Testing

### Manual Testing

```bash
# Test favicon routes
curl -I http://localhost:5000/favicon.ico
# Expected: 302 redirect to /static/favicon.ico

curl -I http://localhost:5000/favicon.png
# Expected: 302 redirect to /static/favicon.png

# Test CSP report
curl -X POST http://localhost:5000/api/csp-report -H "Content-Type: application/json" -d '{}'
# Expected: 204 No Content, no log entry

curl -X POST http://localhost:5000/api/csp-report -H "Content-Type: application/json" -d '{"csp-report":{"violated-directive":"img-src"}}'
# Expected: 204 No Content, log entry created
```

### Unit Tests

```bash
# Run static files tests
python tests/test_static_files.py

# Run CSP report tests
python tests/test_csp_report.py
```

**All tests pass:**
- ✅ 5/5 static file tests pass
- ✅ 3/3 CSP report tests pass

## Impact

### Before
- ❌ 404 errors for `/favicon.ico` and `/favicon.png`
- ❌ Log spam with empty CSP reports
- ❌ Noisy logs without useful information

### After
- ✅ 200 OK for all favicon requests
- ✅ Only meaningful CSP violations are logged
- ✅ Clean, actionable logs
- ✅ No changes to templates or existing behavior
- ✅ Backwards compatible (templates still work with `/static/favicon.*`)

## Deployment

These changes are deployment-ready:
- ✅ No database migrations required
- ✅ No configuration changes needed
- ✅ No breaking changes
- ✅ Works on both local development and Vercel production
- ✅ Minimal, surgical changes following project guidelines

## Technical Details

### Route Registration
The new routes are registered under the main blueprint (`bp`) in `gramatike_app/routes/__init__.py`:
- Endpoint: `main.favicon_ico` → Route: `/favicon.ico`
- Endpoint: `main.favicon_png` → Route: `/favicon.png`

### Why Redirects Instead of Direct Serving?
Using redirects (`302`) instead of directly serving files:
1. **Caching**: Browsers will cache the redirect and subsequent requests go directly to `/static/*`
2. **Consistency**: All static files are served through the same `/static/` path
3. **Simplicity**: No need to duplicate file serving logic
4. **SEO**: Search engines understand 302 redirects for resources

### CSP Report Format
CSP reports follow the standard format:
```json
{
  "csp-report": {
    "document-uri": "https://example.com/page",
    "violated-directive": "img-src 'self'",
    "blocked-uri": "https://malicious.com/image.png",
    ...
  }
}
```

Empty reports `{}` are now ignored to reduce noise.

## Future Improvements

Potential enhancements (not in scope for this fix):
- Add rate limiting to CSP report endpoint to prevent abuse
- Store CSP violations in database for analysis
- Create admin dashboard to view CSP violations
- Add metrics/monitoring for CSP violations

## References

- Flask Static Files: https://flask.palletsprojects.com/en/3.0.x/patterns/favicon/
- CSP Reporting: https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP#reporting_violations
- Issue logs showing favicon 404s and CSP spam
