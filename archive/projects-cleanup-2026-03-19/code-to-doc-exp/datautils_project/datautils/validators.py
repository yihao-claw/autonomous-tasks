"""
Data validation module for email, phone, and URL validation.

This module provides comprehensive validation functions for common data types.
"""

import re
from typing import Tuple


def validate_email(email: str) -> Tuple[bool, str]:
    """
    Validate if a string is a valid email address.
    
    Args:
        email: The email string to validate
        
    Returns:
        A tuple of (is_valid, error_message)
        
    Examples:
        >>> validate_email("user@example.com")
        (True, "")
        >>> validate_email("invalid-email")
        (False, "Invalid email format")
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return True, ""
    return False, "Invalid email format"


def validate_phone(phone: str, country_code: str = "US") -> Tuple[bool, str]:
    """
    Validate if a string is a valid phone number.
    
    Supports multiple country formats:
    - US: (XXX) XXX-XXXX or XXX-XXX-XXXX
    - UK: +44 XXXX XXXXXX
    - CN: +86 1X XXXX XXXX
    
    Args:
        phone: The phone number string to validate
        country_code: Country code (US, UK, CN). Defaults to "US"
        
    Returns:
        A tuple of (is_valid, error_message)
        
    Raises:
        ValueError: If country_code is not supported
    """
    patterns = {
        "US": r'^(\d{3}[-.]?\d{3}[-.]?\d{4})$',
        "UK": r'^\+44\s?\d{4}\s?\d{6}$',
        "CN": r'^\+86\s?1[0-9]\s?\d{4}\s?\d{4}$',
    }
    
    if country_code not in patterns:
        raise ValueError(f"Unsupported country code: {country_code}")
    
    if re.match(patterns[country_code], phone):
        return True, ""
    return False, f"Invalid {country_code} phone format"


def validate_url(url: str, require_https: bool = False) -> Tuple[bool, str]:
    """
    Validate if a string is a valid URL.
    
    Args:
        url: The URL string to validate
        require_https: If True, only accept HTTPS URLs. Defaults to False
        
    Returns:
        A tuple of (is_valid, error_message)
    """
    if require_https:
        pattern = r'^https://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$'
    else:
        pattern = r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$'
    
    if re.match(pattern, url):
        return True, ""
    return False, "Invalid URL format"


def validate_range(value: float, min_val: float, max_val: float) -> bool:
    """
    Validate if a numeric value is within a specified range.
    
    Args:
        value: The numeric value to validate
        min_val: Minimum acceptable value (inclusive)
        max_val: Maximum acceptable value (inclusive)
        
    Returns:
        True if value is within range, False otherwise
    """
    return min_val <= value <= max_val
