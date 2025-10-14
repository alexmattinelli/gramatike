"""
Utility functions for flexible text comparison.
Used for validating answers in dynamics, especially "Quem sou eu?" type.
"""
import unicodedata
import re


def normalize_text(text: str) -> str:
    """
    Normalize text for comparison by:
    - Converting to lowercase
    - Removing accents/diacritics
    - Removing extra whitespace
    - Keeping only alphanumeric characters and spaces
    """
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower().strip()
    
    # Remove accents/diacritics
    text = ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )
    
    # Remove non-alphanumeric except spaces
    text = re.sub(r'[^a-z0-9\s]', '', text)
    
    # Normalize whitespace
    text = ' '.join(text.split())
    
    return text


def generate_gender_variants(text: str) -> list:
    """
    Generate gender variants for a given text.
    Examples:
    - "não-binário" -> ["nao binario", "nao binaria", "nao binarie"]
    - "feminino" -> ["feminino", "feminina"]
    """
    variants = set()
    normalized = normalize_text(text)
    variants.add(normalized)
    
    # Common gender endings in Portuguese
    # If ends with 'o', add 'a' and 'e' variants
    if normalized.endswith('o'):
        variants.add(normalized[:-1] + 'a')
        variants.add(normalized[:-1] + 'e')
    # If ends with 'a', add 'o' and 'e' variants
    elif normalized.endswith('a'):
        variants.add(normalized[:-1] + 'o')
        variants.add(normalized[:-1] + 'e')
    # If ends with 'e', add 'o' and 'a' variants
    elif normalized.endswith('e'):
        variants.add(normalized[:-1] + 'o')
        variants.add(normalized[:-1] + 'a')
    
    return list(variants)


def is_answer_correct(user_answer: str, correct_answer: str, alternatives: list = None) -> bool:
    """
    Check if user's answer matches the correct answer or any alternative.
    
    Args:
        user_answer: The answer provided by the user
        correct_answer: The main correct answer
        alternatives: List of alternative correct answers (optional)
    
    Returns:
        True if the answer is correct (matches main answer or any alternative)
    """
    if not user_answer or not correct_answer:
        return False
    
    # Normalize the user's answer
    normalized_user = normalize_text(user_answer)
    
    # Generate all valid answers (main + alternatives)
    all_valid = set()
    
    # Add main answer and its gender variants
    all_valid.update(generate_gender_variants(correct_answer))
    
    # Add alternatives and their gender variants
    if alternatives:
        for alt in alternatives:
            if alt:
                all_valid.update(generate_gender_variants(alt))
    
    # Check if user's answer matches any valid answer
    return normalized_user in all_valid
