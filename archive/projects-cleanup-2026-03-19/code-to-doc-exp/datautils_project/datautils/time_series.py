"""
Time series analysis and manipulation utilities.

Functions for handling temporal data, moving averages, and trend analysis.
"""

from typing import List, Tuple, Optional
from datetime import datetime, timedelta
import statistics


class TimeSeries:
    """Represents a time series data with timestamps and values."""
    
    def __init__(self, timestamps: List[datetime], values: List[float]):
        """
        Initialize a time series.
        
        Args:
            timestamps: List of datetime objects
            values: List of numeric values
            
        Raises:
            ValueError: If timestamps and values have different lengths
        """
        if len(timestamps) != len(values):
            raise ValueError("Timestamps and values must have same length")
        
        self.timestamps = timestamps
        self.values = values
    
    def add_point(self, timestamp: datetime, value: float) -> None:
        """
        Add a new data point to the time series.
        
        Args:
            timestamp: Timestamp for the data point
            value: Numeric value
        """
        self.timestamps.append(timestamp)
        self.values.append(value)
    
    def __len__(self) -> int:
        """Get number of data points in the time series."""
        return len(self.values)
    
    def __getitem__(self, index: int) -> Tuple[datetime, float]:
        """Get a specific data point by index."""
        return self.timestamps[index], self.values[index]


def moving_average(values: List[float], window: int) -> List[float]:
    """
    Calculate the moving average of a series.
    
    Args:
        values: List of numeric values
        window: Window size for the moving average
        
    Returns:
        List of moving average values
        
    Raises:
        ValueError: If window is larger than the series
    """
    if window > len(values):
        raise ValueError("Window size cannot be larger than series length")
    
    result = []
    for i in range(len(values) - window + 1):
        window_values = values[i:i + window]
        result.append(sum(window_values) / window)
    
    return result


def exponential_smoothing(values: List[float], alpha: float = 0.3) -> List[float]:
    """
    Apply exponential smoothing to a time series.
    
    The formula is: S_t = alpha * X_t + (1 - alpha) * S_(t-1)
    
    Args:
        values: List of numeric values
        alpha: Smoothing factor (0 to 1). Higher = more responsive to changes
        
    Returns:
        List of smoothed values
        
    Raises:
        ValueError: If alpha is not between 0 and 1
    """
    if not 0 <= alpha <= 1:
        raise ValueError("Alpha must be between 0 and 1")
    
    if not values:
        return []
    
    result = [values[0]]
    for i in range(1, len(values)):
        smoothed = alpha * values[i] + (1 - alpha) * result[i - 1]
        result.append(smoothed)
    
    return result


def calculate_trend(values: List[float]) -> str:
    """
    Determine the overall trend of a time series.
    
    Args:
        values: List of numeric values
        
    Returns:
        "uptrend", "downtrend", or "stable"
    """
    if len(values) < 2:
        return "stable"
    
    first_half = statistics.mean(values[:len(values)//2])
    second_half = statistics.mean(values[len(values)//2:])
    
    diff = ((second_half - first_half) / first_half) * 100 if first_half != 0 else 0
    
    if diff > 5:
        return "uptrend"
    elif diff < -5:
        return "downtrend"
    else:
        return "stable"


def detect_anomalies(values: List[float], threshold: float = 2.0) -> List[int]:
    """
    Detect anomalies using standard deviation method.
    
    Points more than threshold * std away from mean are considered anomalies.
    
    Args:
        values: List of numeric values
        threshold: Standard deviation multiplier. Defaults to 2.0
        
    Returns:
        List of indices where anomalies are detected
    """
    if len(values) < 2:
        return []
    
    mean = statistics.mean(values)
    stdev = statistics.stdev(values)
    
    anomalies = []
    for i, val in enumerate(values):
        if abs(val - mean) > threshold * stdev:
            anomalies.append(i)
    
    return anomalies


def interpolate_missing(values: List[Optional[float]]) -> List[float]:
    """
    Fill missing values (None) using linear interpolation.
    
    Args:
        values: List with some None values
        
    Returns:
        List with missing values filled
    """
    result = list(values)
    
    # Find all None indices
    none_indices = [i for i, v in enumerate(result) if v is None]
    
    for idx in none_indices:
        # Find nearest non-None values
        left_val, right_val = None, None
        left_idx, right_idx = -1, -1
        
        for i in range(idx - 1, -1, -1):
            if result[i] is not None:
                left_val = result[i]
                left_idx = i
                break
        
        for i in range(idx + 1, len(result)):
            if result[i] is not None:
                right_val = result[i]
                right_idx = i
                break
        
        # Interpolate
        if left_val is not None and right_val is not None:
            ratio = (idx - left_idx) / (right_idx - left_idx)
            result[idx] = left_val + ratio * (right_val - left_val)
        elif left_val is not None:
            result[idx] = left_val
        elif right_val is not None:
            result[idx] = right_val
    
    return result


def resample(values: List[float], timestamps: List[datetime], 
            period: str = "1h") -> Tuple[List[datetime], List[float]]:
    """
    Resample time series to a new frequency.
    
    Args:
        values: Original values
        timestamps: Original timestamps
        period: Target period ("1h", "1d", "1w", "1m")
        
    Returns:
        Tuple of (new_timestamps, new_values)
    """
    # Simple implementation: group by period and average
    period_map = {
        "1h": timedelta(hours=1),
        "1d": timedelta(days=1),
        "1w": timedelta(weeks=1),
        "1m": timedelta(days=30),
    }
    
    if period not in period_map:
        raise ValueError(f"Unknown period: {period}")
    
    delta = period_map[period]
    grouped = {}
    
    for ts, val in zip(timestamps, values):
        # Round timestamp to period
        rounded = ts.replace(hour=0, minute=0, second=0, microsecond=0)
        if period == "1h":
            rounded = ts.replace(minute=0, second=0, microsecond=0)
        
        if rounded not in grouped:
            grouped[rounded] = []
        grouped[rounded].append(val)
    
    new_timestamps = sorted(grouped.keys())
    new_values = [statistics.mean(grouped[ts]) for ts in new_timestamps]
    
    return new_timestamps, new_values
