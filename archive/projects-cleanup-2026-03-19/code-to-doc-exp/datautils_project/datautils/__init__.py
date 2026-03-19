"""
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
