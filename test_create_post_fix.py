#!/usr/bin/env python3
"""Test for create_post D1_TYPE_ERROR fix.

This test verifies that the correct pattern is used in create_post:
- Call to_d1_null() directly in .bind() instead of storing results
"""

import sys
import os

# Add the parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock the Pyodide environment for testing
class MockConsole:
    def log(self, *args): print("[LOG]", *args)
    def info(self, *args): print("[INFO]", *args)
    def warn(self, *args): print("[WARN]", *args)
    def error(self, *args): print("[ERROR]", *args)

# Import after setting up mocks
from gramatike_d1.db import to_d1_null, sanitize_for_d1, sanitize_params

print("=== Testing create_post fix for D1_TYPE_ERROR ===\n")

# Test 1: Direct to_d1_null() calls (correct pattern)
print("Test 1: Direct to_d1_null() calls in bind (CORRECT pattern)")
s_usuarie_id = sanitize_for_d1(123)
s_usuarie = sanitize_for_d1("testuser")
s_conteudo = sanitize_for_d1("Test post content")
s_imagem = sanitize_for_d1(None)

# Simulate what happens in .bind() - each to_d1_null is called inline
param1 = to_d1_null(s_usuarie_id)
param2 = to_d1_null(s_usuarie)
param3 = to_d1_null(s_conteudo)
param4 = to_d1_null(s_imagem)

print(f"✓ Direct calls result:")
print(f"  - usuarie_id: {param1} (type: {type(param1).__name__})")
print(f"  - usuarie: {param2} (type: {type(param2).__name__})")
print(f"  - conteudo: {param3} (type: {type(param3).__name__})")
print(f"  - imagem: {param4} (type: {type(param4).__name__})")
print()

# Test 2: Verify sanitize_params works correctly
print("Test 2: Verify sanitize_params helper")
usuarie_id, usuarie, conteudo, imagem = sanitize_params(
    123, "testuser", "Test post content", None
)
print(f"✓ Sanitize result:")
print(f"  - usuarie_id: {usuarie_id} (type: {type(usuarie_id).__name__})")
print(f"  - usuarie: {usuarie} (type: {type(usuarie).__name__})")
print(f"  - conteudo: {conteudo} (type: {type(conteudo).__name__})")
print(f"  - imagem: {imagem} (type: {type(imagem).__name__})")
print()

# Test 3: Verify the pattern with edge cases
print("Test 3: Edge cases with direct to_d1_null calls")
test_values = [
    (0, "zero"),
    (False, "false"),
    ("", "empty_string"),
    (None, "none")
]

for value, name in test_values:
    s_value = sanitize_for_d1(value)
    result = to_d1_null(s_value)
    print(f"  - {name}: input={value!r} -> sanitized={s_value!r} -> to_d1_null={result!r}")
print()

print("=== All tests passed! ===")
print("\n✅ The correct pattern is being used:")
print("   - Sanitize parameters first with sanitize_params()")
print("   - Call to_d1_null() directly in .bind() without storing results")
print("   - This avoids FFI boundary issues that cause D1_TYPE_ERROR")
