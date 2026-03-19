"""
Caching utilities for storing and retrieving cached computation results.

Provides both simple in-memory caching and file-based caching mechanisms.
"""

import time
import pickle
import json
from typing import Any, Callable, Optional, Dict
from pathlib import Path
from functools import wraps


class CacheEntry:
    """Represents a single cache entry with value and metadata."""
    
    def __init__(self, value: Any, ttl: Optional[int] = None):
        """
        Initialize a cache entry.
        
        Args:
            value: The value to cache
            ttl: Time to live in seconds. None means no expiration
        """
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl
    
    def is_expired(self) -> bool:
        """Check if this cache entry has expired."""
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl


class MemoryCache:
    """Simple in-memory cache with TTL support."""
    
    def __init__(self, max_size: int = 1000):
        """
        Initialize memory cache.
        
        Args:
            max_size: Maximum number of entries to store
        """
        self.max_size = max_size
        self._cache: Dict[str, CacheEntry] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found or expired
        """
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        if entry.is_expired():
            del self._cache[key]
            return None
        
        return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Store a value in cache.
        
        Args:
            key: Cache key
            value: Value to store
            ttl: Time to live in seconds
        """
        if len(self._cache) >= self.max_size:
            # Simple eviction: remove oldest entry
            oldest_key = min(self._cache.keys(), 
                           key=lambda k: self._cache[k].created_at)
            del self._cache[oldest_key]
        
        self._cache[key] = CacheEntry(value, ttl)
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
    
    def size(self) -> int:
        """Get current number of cached entries."""
        return len(self._cache)


def cached(ttl: Optional[int] = None):
    """
    Decorator to cache function results.
    
    Args:
        ttl: Time to live in seconds
        
    Returns:
        Decorated function with caching
        
    Examples:
        @cached(ttl=3600)
        def expensive_function(x):
            return x ** 2
    """
    cache = {}
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from arguments
            key = str((args, tuple(sorted(kwargs.items()))))
            
            if key in cache:
                entry = cache[key]
                if not entry.is_expired():
                    return entry.value
                else:
                    del cache[key]
            
            result = func(*args, **kwargs)
            cache[key] = CacheEntry(result, ttl)
            return result
        
        return wrapper
    return decorator


class FileCache:
    """File-based cache for persistent storage."""
    
    def __init__(self, cache_dir: str, format: str = "json"):
        """
        Initialize file cache.
        
        Args:
            cache_dir: Directory to store cache files
            format: Storage format ("json" or "pickle")
        """
        self.cache_dir = Path(cache_dir)
        self.format = format
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_path(self, key: str) -> Path:
        """Get file path for a cache key."""
        ext = "json" if self.format == "json" else "pkl"
        return self.cache_dir / f"{key}.{ext}"
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve a value from file cache."""
        path = self._get_path(key)
        if not path.exists():
            return None
        
        try:
            if self.format == "json":
                with open(path, 'r') as f:
                    return json.load(f)
            else:
                with open(path, 'rb') as f:
                    return pickle.load(f)
        except (json.JSONDecodeError, pickle.PickleError):
            return None
    
    def set(self, key: str, value: Any) -> None:
        """Store a value in file cache."""
        path = self._get_path(key)
        
        try:
            if self.format == "json":
                with open(path, 'w') as f:
                    json.dump(value, f)
            else:
                with open(path, 'wb') as f:
                    pickle.dump(value, f)
        except (TypeError, json.JSONDecodeError):
            pass  # Silently ignore serialization errors
    
    def clear(self) -> None:
        """Clear all cache files."""
        for file in self.cache_dir.glob('*'):
            file.unlink()
