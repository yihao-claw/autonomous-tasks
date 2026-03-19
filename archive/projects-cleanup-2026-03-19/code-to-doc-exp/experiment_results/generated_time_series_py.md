# Module `time_series`


## Classes

## class `TimeSeries`

Represents a time series data with timestamps and values.

### Methods

### `add_point(self, timestamp: datetime, value: float) -> None`

Add a new data point to the time series.

Args:
    timestamp: Timestamp for the data point
    value: Numeric value

**Parameters:**

- `self`
- `timestamp` (datetime)
- `value` (float)

**Returns:**

- None


## Functions

### `moving_average(values: List[float], window: int) -> List[float]`

Calculate the moving average of a series.

Args:
    values: List of numeric values
    window: Window size for the moving average
    
Returns:
    List of moving average values
    
Raises:
    ValueError: If window is larger than the series

**Parameters:**

- `values` (List[float])
- `window` (int)

**Returns:**

- List[float]


### `exponential_smoothing(values: List[float], alpha: float = 0.3) -> List[float]`

Apply exponential smoothing to a time series.

The formula is: S_t = alpha * X_t + (1 - alpha) * S_(t-1)

Args:
    values: List of numeric values
    alpha: Smoothing factor (0 to 1). Higher = more responsive to changes
    
Returns:
    List of smoothed values
    
Raises:
    ValueError: If alpha is not between 0 and 1

**Parameters:**

- `values` (List[float])
- `alpha` (float) = 0.3

**Returns:**

- List[float]


### `calculate_trend(values: List[float]) -> str`

Determine the overall trend of a time series.

Args:
    values: List of numeric values
    
Returns:
    "uptrend", "downtrend", or "stable"

**Parameters:**

- `values` (List[float])

**Returns:**

- str


### `detect_anomalies(values: List[float], threshold: float = 2.0) -> List[int]`

Detect anomalies using standard deviation method.

Points more than threshold * std away from mean are considered anomalies.

Args:
    values: List of numeric values
    threshold: Standard deviation multiplier. Defaults to 2.0
    
Returns:
    List of indices where anomalies are detected

**Parameters:**

- `values` (List[float])
- `threshold` (float) = 2.0

**Returns:**

- List[int]


### `interpolate_missing(values: List[Optional[float]]) -> List[float]`

Fill missing values (None) using linear interpolation.

Args:
    values: List with some None values
    
Returns:
    List with missing values filled

**Parameters:**

- `values` (List[Optional[float]])

**Returns:**

- List[float]


### `resample(values: List[float], timestamps: List[datetime], period: str = '1h') -> Tuple[(List[datetime], List[float])]`

Resample time series to a new frequency.

Args:
    values: Original values
    timestamps: Original timestamps
    period: Target period ("1h", "1d", "1w", "1m")
    
Returns:
    Tuple of (new_timestamps, new_values)

**Parameters:**

- `values` (List[float])
- `timestamps` (List[datetime])
- `period` (str) = '1h'

**Returns:**

- Tuple[(List[datetime], List[float])]

