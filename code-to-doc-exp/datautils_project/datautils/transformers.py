"""
Text transformation and normalization utilities.

Provides functions for case conversion, text normalization, and cleanup.
"""

import re
import unicodedata
from typing import List, Optional


def normalize_text(text: str, lowercase: bool = True, remove_accents: bool = True) -> str:
    """
    Normalize text by removing extra whitespace and optionally converting to lowercase.
    
    Args:
        text: Input text to normalize
        lowercase: Convert to lowercase. Defaults to True
        remove_accents: Remove accent marks. Defaults to True
        
    Returns:
        Normalized text string
        
    Examples:
        >>> normalize_text("  Hello   WORLD  ")
        "hello world"
    """
    # Remove extra whitespace
    text = " ".join(text.split())
    
    # Remove accents if requested
    if remove_accents:
        text = ''.join(
            c for c in unicodedata.normalize('NFD', text)
            if unicodedata.category(c) != 'Mn'
        )
    
    # Convert to lowercase if requested
    if lowercase:
        text = text.lower()
    
    return text


def convert_case(text: str, case_type: str) -> str:
    """
    Convert text to specified case format.
    
    Supported formats:
    - "upper": ALL UPPERCASE
    - "lower": all lowercase
    - "title": Title Case
    - "snake": snake_case
    - "camel": camelCase
    
    Args:
        text: Input text to convert
        case_type: Target case format (upper, lower, title, snake, camel)
        
    Returns:
        Text converted to specified case
        
    Raises:
        ValueError: If case_type is not supported
    """
    if case_type == "upper":
        return text.upper()
    elif case_type == "lower":
        return text.lower()
    elif case_type == "title":
        return text.title()
    elif case_type == "snake":
        s1 = re.sub('(.)([A-Z][a-z]+)', r'_', text)
        return re.sub('([a-z0-9])([A-Z])', r'_', s1).lower()
    elif case_type == "camel":
        words = text.split('_')
        return words[0].lower() + ''.join(w.title() for w in words[1:])
    else:
        raise ValueError(f"Unsupported case type: {case_type}")


def remove_special_chars(text: str, keep_alphanumeric: bool = True) -> str:
    """
    Remove special characters from text.
    
    Args:
        text: Input text
        keep_alphanumeric: Keep alphanumeric characters. Defaults to True
        
    Returns:
        Text with special characters removed
    """
    if keep_alphanumeric:
        return re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return re.sub(r'[^a-zA-Z0-9]', '', text)


def slugify(text: str, separator: str = "-") -> str:
    """
    Convert text to a URL-friendly slug.
    
    Args:
        text: Input text
        separator: Character to use as word separator. Defaults to "-"
        
    Returns:
        Slugified text
    """
    text = normalize_text(text, lowercase=True)
    text = remove_special_chars(text)
    text = re.sub(r'\s+', separator, text)
    return text.strip(separator)
