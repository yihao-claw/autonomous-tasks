# Module `cache`


## Classes

## class `CacheEntry`

Represents a single cache entry with value and metadata.

### Methods

### `is_expired(self) -> bool`

Check if this cache entry has expired.

**Parameters:**

- `self`

**Returns:**

- bool


## class `MemoryCache`

Simple in-memory cache with TTL support.

### Methods

### `get(self, key: str) -> Optional[Any]`

Retrieve a value from cache.

Args:
    key: Cache key
    
Returns:
    Cached value or None if not found or expired

**Parameters:**

- `self`
- `key` (str)

**Returns:**

- Optional[Any]

### `set(self, key: str, value: Any, ttl: Optional[int] = None) -> None`

Store a value in cache.

Args:
    key: Cache key
    value: Value to store
    ttl: Time to live in seconds

**Parameters:**

- `self`
- `key` (str)
- `value` (Any)
- `ttl` (Optional[int]) = None

**Returns:**

- None

### `clear(self) -> None`

Clear all cache entries.

**Parameters:**

- `self`

**Returns:**

- None

### `size(self) -> int`

Get current number of cached entries.

**Parameters:**

- `self`

**Returns:**

- int


## class `FileCache`

File-based cache for persistent storage.

### Methods

### `get(self, key: str) -> Optional[Any]`

Retrieve a value from file cache.

**Parameters:**

- `self`
- `key` (str)

**Returns:**

- Optional[Any]

### `set(self, key: str, value: Any) -> None`

Store a value in file cache.

**Parameters:**

- `self`
- `key` (str)
- `value` (Any)

**Returns:**

- None

### `clear(self) -> None`

Clear all cache files.

**Parameters:**

- `self`

**Returns:**

- None


## Functions

### `cached(ttl: Optional[int] = None)`

Decorator to cache function results.

Args:
    ttl: Time to live in seconds
    
Returns:
    Decorated function with caching
    
Examples:
    @cached(ttl=3600)
    def expensive_function(x):
        return x ** 2

**Parameters:**

- `ttl` (Optional[int]) = None


### `decorator(func: Callable) -> Callable`

_No documentation provided._

**Parameters:**

- `func` (Callable)

**Returns:**

- Callable


### `wrapper()`

_No documentation provided._

