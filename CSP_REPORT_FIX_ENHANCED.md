# CSP Report Endpoint Enhancement

## Problem

Production logs showed empty CSP reports being logged, creating noise without providing useful violation information:

```
WARNING:gramatike_app:CSP report: {}
```

This was occurring despite a previous fix (PR #67) that attempted to filter empty reports using `if payload:` check.

## Root Cause Analysis

The issue had multiple facets:

### 1. Content-Type Handling
Browsers send CSP reports with `Content-Type: application/csp-report`, which Flask's `request.get_json(silent=True)` doesn't recognize by default. This caused:
- `request.get_json(silent=True)` to return `None` instead of parsing the JSON
- The fallback `or {}` would create an empty dict
- The empty dict check would correctly filter it out

However, the code wasn't robust against all scenarios.

### 2. Empty Nested Objects
CSP reports can have the structure `{"csp-report": {}}` where the outer dict is truthy but contains no actual violation data. The previous check `if payload:` would evaluate to `True` for this case, causing it to be logged.

### 3. Logging Level
Parse errors were being logged at WARNING level, creating noise even when gracefully handled.

## Solution

### Enhanced Endpoint Logic

```python
@bp.route('/api/csp-report', methods=['POST'])
def api_csp_report():
    try:
        # Use force=True to handle application/csp-report content-type
        payload = request.get_json(force=True, silent=True)
        
        # Only log non-empty, meaningful reports
        if payload and payload != {} and _is_meaningful_csp_report(payload):
            current_app.logger.warning(f"CSP report: {payload}")
    except Exception as _e:
        # Log parse failures at debug level to avoid noise
        current_app.logger.debug(f"CSP report parse failed: {_e}")
    return ('', 204)

def _is_meaningful_csp_report(payload):
    """Check if CSP report contains actual violation data"""
    if not isinstance(payload, dict):
        return False
    
    # Check if there's a csp-report key with actual data
    if 'csp-report' in payload:
        csp_data = payload.get('csp-report')
        return isinstance(csp_data, dict) and bool(csp_data)
    
    # If no csp-report key, check if payload has meaningful data
    return len(payload) > 0
```

### Key Improvements

1. **Force JSON Parsing**: Using `force=True` ensures JSON is parsed regardless of Content-Type header
2. **Explicit Empty Check**: Added `payload != {}` to catch edge cases
3. **Meaningful Report Validation**: New `_is_meaningful_csp_report()` function checks for:
   - Properly structured CSP reports with non-empty data
   - Empty nested objects like `{"csp-report": {}}`
4. **Debug Logging**: Parse errors logged at DEBUG level instead of WARNING

## Testing

### Test Coverage

1. **Empty JSON Object**: `{}` → Not logged ✅
2. **Empty CSP Report**: `{"csp-report": {}}` → Not logged ✅
3. **Valid CSP Report**: `{"csp-report": {"violated-directive": "..."}}` → Logged ✅
4. **Invalid JSON**: Gracefully handled, no crash ✅
5. **application/csp-report Content-Type**: Properly parsed and validated ✅

### Running Tests

```bash
python tests/test_csp_report.py
```

Expected output:
```
✅ Empty CSP reports are not logged (reduces noise)
✅ Non-empty CSP reports are logged correctly
✅ Invalid JSON is handled gracefully (no crash)
✅ CSP reports with application/csp-report content-type handled correctly
```

## Impact

### Before
- ❌ Empty reports logged as WARNING
- ❌ Parse errors logged as WARNING (noise)
- ❌ `application/csp-report` content-type might not be parsed correctly
- ❌ Empty nested objects `{"csp-report": {}}` would be logged

### After
- ✅ Only meaningful CSP violations logged
- ✅ Parse errors at DEBUG level (no noise in production)
- ✅ All content-types handled correctly with `force=True`
- ✅ Empty nested objects properly filtered
- ✅ Clean, actionable logs

## Deployment

No configuration changes or database migrations required. This is a code-only fix that:
- ✅ Works on both local development and Vercel production
- ✅ Backwards compatible (same endpoint behavior)
- ✅ Returns 204 status as before
- ✅ No breaking changes

## Future Considerations

Potential enhancements (not in scope for this fix):
- Store meaningful CSP violations in database for analysis
- Add rate limiting to prevent report abuse
- Create admin dashboard for CSP violation monitoring
- Implement aggregation and alerting for repeated violations

## References

- Flask Request.get_json(): https://flask.palletsprojects.com/en/3.0.x/api/#flask.Request.get_json
- CSP Reporting: https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP#reporting_violations
- Content-Type: application/csp-report: https://www.w3.org/TR/CSP2/#violation-reports
