"""
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
