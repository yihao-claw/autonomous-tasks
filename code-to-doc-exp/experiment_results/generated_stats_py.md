# Module `stats`


## Functions

### `calculate_mean(values: List[float]) -> float`

Calculate the arithmetic mean (average) of a list of numbers.

Args:
    values: List of numeric values
    
Returns:
    The arithmetic mean
    
Raises:
    ValueError: If list is empty
    TypeError: If values contain non-numeric types

**Parameters:**

- `values` (List[float])

**Returns:**

- float


### `calculate_std(values: List[float], population: bool = False) -> float`

Calculate the standard deviation of a list of numbers.

Args:
    values: List of numeric values
    population: If True, calculate population std dev; if False (default), calculate sample
    
Returns:
    The standard deviation
    
Raises:
    ValueError: If list is empty or has only one element (for sample std dev)

**Parameters:**

- `values` (List[float])
- `population` (bool) = False

**Returns:**

- float


### `calculate_percentile(values: List[float], percentile: int) -> float`

Calculate the specified percentile of a list of numbers.

Args:
    values: List of numeric values
    percentile: Percentile to calculate (0-100)
    
Returns:
    The value at the specified percentile
    
Raises:
    ValueError: If percentile is not between 0 and 100, or list is empty

**Parameters:**

- `values` (List[float])
- `percentile` (int)

**Returns:**

- float


### `calculate_median(values: List[float]) -> float`

Calculate the median (50th percentile) of a list of numbers.

Args:
    values: List of numeric values
    
Returns:
    The median value

**Parameters:**

- `values` (List[float])

**Returns:**

- float


### `calculate_min_max(values: List[float]) -> Tuple[(float, float)]`

Calculate both minimum and maximum values in a single pass.

Args:
    values: List of numeric values
    
Returns:
    Tuple of (min_value, max_value)
    
Raises:
    ValueError: If list is empty

**Parameters:**

- `values` (List[float])

**Returns:**

- Tuple[(float, float)]


### `calculate_quartiles(values: List[float]) -> Tuple[(float, float, float)]`

Calculate the first, second (median), and third quartiles.

Args:
    values: List of numeric values
    
Returns:
    Tuple of (Q1, Q2/median, Q3)

**Parameters:**

- `values` (List[float])

**Returns:**

- Tuple[(float, float, float)]

