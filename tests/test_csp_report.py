#!/usr/bin/env python
"""
Unit test to verify CSP report endpoint only logs non-empty reports.
This prevents log spam from browser extensions and empty CSP violations.
"""

import sys
import os
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_csp_report_empty_payload():
    """Test that empty CSP reports don't generate log entries"""
    from api.index import app
    import logging
    from io import StringIO
    
    # Capture logs
    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setLevel(logging.WARNING)
    app.logger.addHandler(handler)
    
    with app.test_client() as client:
        # Test 1: Send empty JSON object
        resp = client.post('/api/csp-report', 
            data=json.dumps({}),
            content_type='application/json')
        assert resp.status_code == 204, f"Expected 204, got {resp.status_code}"
        
        # Test 2: Send CSP report with empty data
        log_stream.truncate(0)
        log_stream.seek(0)
        resp = client.post('/api/csp-report',
            data=json.dumps({'csp-report': {}}),
            content_type='application/json')
        assert resp.status_code == 204, f"Expected 204, got {resp.status_code}"
        
        # Test 3: Send with application/csp-report content-type
        log_stream.truncate(0)
        log_stream.seek(0)
        resp = client.post('/api/csp-report',
            data=json.dumps({}),
            content_type='application/csp-report')
        assert resp.status_code == 204, f"Expected 204, got {resp.status_code}"
        
        # Check that no CSP report was logged (empty payloads should be ignored)
        log_output = log_stream.getvalue()
        assert 'CSP report:' not in log_output, "Empty CSP reports should not be logged"
    
    app.logger.removeHandler(handler)
    print("✅ Empty CSP reports are not logged (reduces noise)")


def test_csp_report_non_empty_payload():
    """Test that non-empty CSP reports are logged"""
    from api.index import app
    import logging
    from io import StringIO
    
    # Capture logs
    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setLevel(logging.WARNING)
    app.logger.addHandler(handler)
    
    with app.test_client() as client:
        # Send actual CSP violation
        payload = {
            'csp-report': {
                'violated-directive': 'img-src',
                'blocked-uri': 'https://example.com/image.png'
            }
        }
        resp = client.post('/api/csp-report', 
            data=json.dumps(payload),
            content_type='application/json')
        
        assert resp.status_code == 204, f"Expected 204, got {resp.status_code}"
        
        # Check that the CSP report was logged
        log_output = log_stream.getvalue()
        assert 'CSP report:' in log_output, "Non-empty CSP reports should be logged"
        assert 'violated-directive' in log_output, "CSP report details should be in log"
    
    app.logger.removeHandler(handler)
    print("✅ Non-empty CSP reports are logged correctly")


def test_csp_report_invalid_json():
    """Test that invalid JSON is handled gracefully"""
    from api.index import app
    
    with app.test_client() as client:
        # Send invalid JSON
        resp = client.post('/api/csp-report', 
            data='not-valid-json',
            content_type='application/json')
        
        assert resp.status_code == 204, f"Expected 204 even with invalid JSON, got {resp.status_code}"
    
    print("✅ Invalid JSON is handled gracefully (no crash)")


def test_csp_report_with_csp_content_type():
    """Test CSP reports with application/csp-report content-type"""
    from api.index import app
    import logging
    from io import StringIO
    
    # Capture logs
    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setLevel(logging.WARNING)
    app.logger.addHandler(handler)
    
    with app.test_client() as client:
        # Test 1: Empty report with application/csp-report
        log_stream.truncate(0)
        log_stream.seek(0)
        resp = client.post('/api/csp-report',
            data=json.dumps({}),
            content_type='application/csp-report')
        assert resp.status_code == 204
        log_output = log_stream.getvalue()
        assert 'CSP report:' not in log_output, "Empty reports should not be logged"
        
        # Test 2: Valid report with application/csp-report
        log_stream.truncate(0)
        log_stream.seek(0)
        payload = {
            'csp-report': {
                'violated-directive': 'script-src',
                'blocked-uri': 'https://evil.com/script.js'
            }
        }
        resp = client.post('/api/csp-report',
            data=json.dumps(payload),
            content_type='application/csp-report')
        assert resp.status_code == 204
        log_output = log_stream.getvalue()
        assert 'CSP report:' in log_output, "Valid reports should be logged"
        assert 'script-src' in log_output, "Report details should be in log"
    
    app.logger.removeHandler(handler)
    print("✅ CSP reports with application/csp-report content-type handled correctly")


def main():
    print("=" * 70)
    print("UNIT TESTS - CSP REPORT FIX")
    print("=" * 70)
    print()
    
    tests = [
        test_csp_report_empty_payload,
        test_csp_report_non_empty_payload,
        test_csp_report_invalid_json,
        test_csp_report_with_csp_content_type,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            print(f"Running: {test.__name__}...")
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
        print()
    
    print("=" * 70)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 70)
    
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
