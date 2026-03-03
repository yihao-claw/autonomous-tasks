"""
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
