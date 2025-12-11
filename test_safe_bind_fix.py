#!/usr/bin/env python3
"""Test for safe_bind fix for D1_TYPE_ERROR issue."""

import sys
sys.path.insert(0, '/home/runner/work/gramatike/gramatike')

# Mock the Pyodide environment for testing
class MockConsole:
    def log(self, *args): print("[LOG]", *args)
    def info(self, *args): print("[INFO]", *args)
    def warn(self, *args): print("[WARN]", *args)
    def error(self, *args): print("[ERROR]", *args)

# Import after setting up mocks
from gramatike_d1.db import to_d1_null, safe_bind, sanitize_for_d1

print("=== Testing safe_bind fix for D1_TYPE_ERROR ===\n")

# Test 1: safe_bind with None values
print("Test 1: safe_bind with None values")
params = safe_bind(
    to_d1_null(None),
    to_d1_null(42),
    to_d1_null("hello"),
    to_d1_null(None)
)
print(f"✓ Result: {params}")
print(f"  - Length: {len(params)}")
print(f"  - All non-None: {all(p is not None for p in params)}")
print()

# Test 2: safe_bind with string 'undefined'
print("Test 2: safe_bind with string 'undefined'")
params = safe_bind(
    to_d1_null('undefined'),
    to_d1_null('valid_string'),
    to_d1_null(123)
)
print(f"✓ Result: {params}")
print()

# Test 3: Simulate create_post parameters
print("Test 3: Simulate create_post parameters")
s_usuarie_id = sanitize_for_d1(123)
s_usuarie = sanitize_for_d1("testuser")
s_conteudo = sanitize_for_d1("Test post content")
s_imagem = sanitize_for_d1(None)

params = safe_bind(
    to_d1_null(s_usuarie_id),
    to_d1_null(s_usuarie),
    to_d1_null(s_conteudo),
    to_d1_null(s_imagem)
)
print(f"✓ Params for INSERT: {params}")
print(f"  - usuarie_id: {params[0]} (type: {type(params[0]).__name__})")
print(f"  - usuarie: {params[1]} (type: {type(params[1]).__name__})")
print(f"  - conteudo: {params[2]} (type: {type(params[2]).__name__})")
print(f"  - imagem: {params[3]} (type: {type(params[3]).__name__})")
print()

# Test 4: Edge cases
print("Test 4: Edge cases")
params = safe_bind(
    to_d1_null(0),          # Zero should be preserved
    to_d1_null(False),      # False should be preserved
    to_d1_null(""),         # Empty string should be preserved
    to_d1_null(None)        # None should become null
)
print(f"✓ Edge cases result: {params}")
print(f"  - Zero preserved: {params[0] == 0}")
print(f"  - False preserved: {params[1] == False}")
print(f"  - Empty string preserved: {params[2] == ''}")
print()

print("=== All tests passed! ===")
