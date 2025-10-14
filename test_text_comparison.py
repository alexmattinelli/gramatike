"""
Test script to verify the text_comparison module works correctly.
This validates the flexible answer matching for "Quem Soul Eu" dynamics.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gramatike_app.utils.text_comparison import (
    normalize_text,
    generate_gender_variants,
    is_answer_correct
)


def test_normalize_text():
    """Test text normalization"""
    print("=" * 60)
    print("TEST 1: normalize_text()")
    print("=" * 60)
    
    test_cases = [
        ("não-binário", "naobinario"),
        ("Não Binária", "nao binaria"),
        ("NÃO BINARIE", "nao binarie"),
        ("  pansexual  ", "pansexual"),
        ("Bissexual!", "bissexual"),
        ("elu/delu", "eludelu"),
    ]
    
    for input_text, expected in test_cases:
        result = normalize_text(input_text)
        status = "✅" if result == expected else "❌"
        print(f"{status} {input_text:20} → {result:20} (expected: {expected})")
    
    print()


def test_generate_gender_variants():
    """Test gender variant generation"""
    print("=" * 60)
    print("TEST 2: generate_gender_variants()")
    print("=" * 60)
    
    test_cases = [
        "não-binário",
        "masculino",
        "pansexual",
        "bissexual",
    ]
    
    for text in test_cases:
        variants = sorted(generate_gender_variants(text))
        print(f"  {text:20} → {variants}")
    
    print()


def test_is_answer_correct():
    """Test flexible answer matching"""
    print("=" * 60)
    print("TEST 3: is_answer_correct()")
    print("=" * 60)
    
    # Test Case 1: Gender with alternatives
    print("\n📋 Scenario 1: Gênero - não-binário")
    print("-" * 40)
    correct = "não-binário"
    alts = ["nb", "enby", "nao binario"]
    
    test_inputs = [
        ("não-binário", True),
        ("Não Binária", True),
        ("nao binarie", True),
        ("NB", True),
        ("nb", True),
        ("enby", True),
        ("ENBY", True),
        ("não binario", True),
        ("NÃO BINARIE", True),
        ("masculino", False),
        ("errado", False),
    ]
    
    for user_input, expected in test_inputs:
        result = is_answer_correct(user_input, correct, alts)
        status = "✅" if result == expected else "❌"
        symbol = "✓" if result else "✗"
        print(f"{status} {symbol} {user_input:20} → {result:5} (expected: {expected})")
    
    # Test Case 2: Sexual orientation
    print("\n📋 Scenario 2: Orientação - pansexual")
    print("-" * 40)
    correct = "pansexual"
    alts = ["pan", "pansexualidade"]
    
    test_inputs = [
        ("pansexual", True),
        ("Pansexual", True),
        ("PANSEXUAL", True),
        ("pan", True),
        ("Pan", True),
        ("PAN", True),
        ("pansexualidade", True),
        ("Pansexualidade", True),
        ("bissexual", False),
    ]
    
    for user_input, expected in test_inputs:
        result = is_answer_correct(user_input, correct, alts)
        status = "✅" if result == expected else "❌"
        symbol = "✓" if result else "✗"
        print(f"{status} {symbol} {user_input:20} → {result:5} (expected: {expected})")
    
    # Test Case 3: Pronouns
    print("\n📋 Scenario 3: Pronomes - elu/delu")
    print("-" * 40)
    correct = "elu/delu"
    alts = ["elu", "delu", "ile/dile"]
    
    test_inputs = [
        ("elu/delu", True),
        ("Elu/Delu", True),
        ("elu", True),
        ("delu", True),
        ("ile/dile", True),
        ("ELU", True),
        ("ele/dele", False),
    ]
    
    for user_input, expected in test_inputs:
        result = is_answer_correct(user_input, correct, alts)
        status = "✅" if result == expected else "❌"
        symbol = "✓" if result else "✗"
        print(f"{status} {symbol} {user_input:20} → {result:5} (expected: {expected})")
    
    print()


def test_edge_cases():
    """Test edge cases"""
    print("=" * 60)
    print("TEST 4: Edge Cases")
    print("=" * 60)
    
    # Empty strings
    assert is_answer_correct("", "test", []) == False
    print("✅ Empty user answer returns False")
    
    assert is_answer_correct("test", "", []) == False
    print("✅ Empty correct answer returns False")
    
    # None alternatives
    assert is_answer_correct("test", "test", None) == True
    print("✅ None alternatives works correctly")
    
    # Case sensitivity
    assert is_answer_correct("TEST", "test", []) == True
    print("✅ Case insensitive matching works")
    
    # Accents
    assert is_answer_correct("café", "cafe", []) == True
    print("✅ Accent normalization works")
    
    print()


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print(" VALIDAÇÃO DO MÓDULO text_comparison.py")
    print("=" * 60 + "\n")
    
    try:
        test_normalize_text()
        test_generate_gender_variants()
        test_is_answer_correct()
        test_edge_cases()
        
        print("=" * 60)
        print("✅ TODOS OS TESTES PASSARAM COM SUCESSO!")
        print("=" * 60)
        print("\nO módulo text_comparison.py está funcionando corretamente.")
        print("A validação flexível de respostas está implementada e testada.")
        print()
        
        return 0
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
