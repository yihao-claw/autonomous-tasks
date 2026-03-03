"""
生成一个演示的Python项目，用于文档自动生成测试
大小：约1500行代码，包含多个模块、类、函数
"""
import os

PROJECT_NAME = "datautils"
PROJECT_PATH = "/home/node/.openclaw/workspace/code-to-doc-exp/datautils_project"

# 创建项目结构
os.makedirs(f"{PROJECT_PATH}/datautils", exist_ok=True)

# ============ datautils/__init__.py ============
init_content = '''"""
DataUtils - A comprehensive data processing and utility library.

This library provides tools for data validation, transformation, and analysis.
Features:
  - Data validation with comprehensive type checking
  - CSV and JSON data handling
  - Time series processing
  - Statistical analysis utilities
"""

__version__ = "1.0.0"

from .validators import validate_email, validate_phone, validate_url
from .transformers import normalize_text, convert_case
from .data_io import load_csv, save_csv, load_json, save_json
from .stats import calculate_mean, calculate_std, calculate_percentile

__all__ = [
    "validate_email",
    "validate_phone", 
    "validate_url",
    "normalize_text",
    "convert_case",
    "load_csv",
    "save_csv",
    "load_json",
    "save_json",
    "calculate_mean",
    "calculate_std",
    "calculate_percentile",
]
'''

with open(f"{PROJECT_PATH}/datautils/__init__.py", "w") as f:
    f.write(init_content)

# ============ datautils/validators.py ============
validators_content = '''"""
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
'''

with open(f"{PROJECT_PATH}/datautils/validators.py", "w") as f:
    f.write(validators_content)

# ============ datautils/transformers.py ============
transformers_content = '''"""
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
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
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
        return re.sub(r'[^a-zA-Z0-9\\s]', '', text)
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
    text = re.sub(r'\\s+', separator, text)
    return text.strip(separator)
'''

with open(f"{PROJECT_PATH}/datautils/transformers.py", "w") as f:
    f.write(transformers_content)

# ============ datautils/data_io.py ============
data_io_content = '''"""
File I/O utilities for CSV and JSON data handling.

Provides functions to load and save data in various formats.
"""

import csv
import json
from typing import List, Dict, Any, Optional
from pathlib import Path


def load_csv(filepath: str, delimiter: str = ",", skip_header: bool = False) -> List[Dict[str, str]]:
    """
    Load data from a CSV file and return as a list of dictionaries.
    
    Args:
        filepath: Path to the CSV file
        delimiter: Field delimiter character. Defaults to ","
        skip_header: Skip the first row. Defaults to False
        
    Returns:
        List of dictionaries where keys are column names
        
    Raises:
        FileNotFoundError: If file does not exist
        csv.Error: If CSV parsing fails
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        for i, row in enumerate(reader):
            if i == 0 and skip_header:
                continue
            data.append(row)
    
    return data


def save_csv(data: List[Dict[str, Any]], filepath: str, delimiter: str = ",") -> None:
    """
    Save a list of dictionaries to a CSV file.
    
    Args:
        data: List of dictionaries to save
        filepath: Output file path
        delimiter: Field delimiter character. Defaults to ","
        
    Raises:
        ValueError: If data is empty or has inconsistent keys
    """
    if not data:
        raise ValueError("Cannot save empty data")
    
    keys = list(data[0].keys())
    
    # Verify all rows have same keys
    for row in data:
        if set(row.keys()) != set(keys):
            raise ValueError("Inconsistent keys across rows")
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys, delimiter=delimiter)
        writer.writeheader()
        writer.writerows(data)


def load_json(filepath: str) -> Any:
    """
    Load JSON data from a file.
    
    Args:
        filepath: Path to the JSON file
        
    Returns:
        Parsed JSON data (dict, list, or primitive)
        
    Raises:
        FileNotFoundError: If file does not exist
        json.JSONDecodeError: If JSON is invalid
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(data: Any, filepath: str, indent: int = 2, sort_keys: bool = False) -> None:
    """
    Save data to a JSON file.
    
    Args:
        data: Data to save (must be JSON serializable)
        filepath: Output file path
        indent: JSON indentation level. Defaults to 2
        sort_keys: Sort object keys in output. Defaults to False
        
    Raises:
        TypeError: If data is not JSON serializable
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, sort_keys=sort_keys)
'''

with open(f"{PROJECT_PATH}/datautils/data_io.py", "w") as f:
    f.write(data_io_content)

# ============ datautils/stats.py ============
stats_content = '''"""
Statistical analysis utilities.

Functions for calculating mean, standard deviation, percentiles, and more.
"""

from typing import List, Tuple, Optional
import math


def calculate_mean(values: List[float]) -> float:
    """
    Calculate the arithmetic mean (average) of a list of numbers.
    
    Args:
        values: List of numeric values
        
    Returns:
        The arithmetic mean
        
    Raises:
        ValueError: If list is empty
        TypeError: If values contain non-numeric types
    """
    if not values:
        raise ValueError("Cannot calculate mean of empty list")
    
    return sum(values) / len(values)


def calculate_std(values: List[float], population: bool = False) -> float:
    """
    Calculate the standard deviation of a list of numbers.
    
    Args:
        values: List of numeric values
        population: If True, calculate population std dev; if False (default), calculate sample
        
    Returns:
        The standard deviation
        
    Raises:
        ValueError: If list is empty or has only one element (for sample std dev)
    """
    if not values:
        raise ValueError("Cannot calculate std dev of empty list")
    
    mean = calculate_mean(values)
    n = len(values)
    
    # For sample standard deviation, use n-1; for population, use n
    divisor = n if population else max(1, n - 1)
    
    variance = sum((x - mean) ** 2 for x in values) / divisor
    return math.sqrt(variance)


def calculate_percentile(values: List[float], percentile: int) -> float:
    """
    Calculate the specified percentile of a list of numbers.
    
    Args:
        values: List of numeric values
        percentile: Percentile to calculate (0-100)
        
    Returns:
        The value at the specified percentile
        
    Raises:
        ValueError: If percentile is not between 0 and 100, or list is empty
    """
    if not values:
        raise ValueError("Cannot calculate percentile of empty list")
    
    if not 0 <= percentile <= 100:
        raise ValueError("Percentile must be between 0 and 100")
    
    sorted_vals = sorted(values)
    idx = (percentile / 100) * (len(sorted_vals) - 1)
    
    lower_idx = int(idx)
    upper_idx = min(lower_idx + 1, len(sorted_vals) - 1)
    
    if lower_idx == upper_idx:
        return sorted_vals[lower_idx]
    
    # Linear interpolation
    weight = idx - lower_idx
    return sorted_vals[lower_idx] * (1 - weight) + sorted_vals[upper_idx] * weight


def calculate_median(values: List[float]) -> float:
    """
    Calculate the median (50th percentile) of a list of numbers.
    
    Args:
        values: List of numeric values
        
    Returns:
        The median value
    """
    return calculate_percentile(values, 50)


def calculate_min_max(values: List[float]) -> Tuple[float, float]:
    """
    Calculate both minimum and maximum values in a single pass.
    
    Args:
        values: List of numeric values
        
    Returns:
        Tuple of (min_value, max_value)
        
    Raises:
        ValueError: If list is empty
    """
    if not values:
        raise ValueError("Cannot calculate min/max of empty list")
    
    return min(values), max(values)


def calculate_quartiles(values: List[float]) -> Tuple[float, float, float]:
    """
    Calculate the first, second (median), and third quartiles.
    
    Args:
        values: List of numeric values
        
    Returns:
        Tuple of (Q1, Q2/median, Q3)
    """
    return (
        calculate_percentile(values, 25),
        calculate_percentile(values, 50),
        calculate_percentile(values, 75),
    )
'''

with open(f"{PROJECT_PATH}/datautils/stats.py", "w") as f:
    f.write(stats_content)

# ============ README.md ============
readme_content = '''# DataUtils

A comprehensive data processing and utility library.

## Features

- **Data Validation**: Email, phone, and URL validation with country-specific support
- **Text Transformation**: Case conversion, normalization, and slugification
- **File I/O**: CSV and JSON loading/saving utilities
- **Statistical Analysis**: Mean, standard deviation, percentiles, and quartiles

## Installation

```bash
pip install datautils
```

## Quick Start

```python
from datautils import validate_email, load_csv, calculate_mean

# Validate email
is_valid, msg = validate_email("user@example.com")

# Load CSV file
data = load_csv("data.csv")

# Calculate statistics
numbers = [1, 2, 3, 4, 5]
avg = calculate_mean(numbers)
```

## Documentation

See the docstrings in each module for detailed function documentation.
'''

with open(f"{PROJECT_PATH}/README.md", "w") as f:
    f.write(readme_content)

print(f"✓ Sample project created at: {PROJECT_PATH}")
