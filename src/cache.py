"""
Caching layer for PCO API Wrapper
Supports Redis and in-memory caching with TTL
"""

import json
import time
import hashlib
from typing import Any, Optional, Callable
from functools import wraps
import os
from abc import ABC, abstractmethod


class CacheBackend(ABC):
    """Abstract base class for cache backends"""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set value in cache with TTL in seconds"""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """Clear all cache entries"""
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        pass


class InMemoryCache(CacheBackend):
    """In-memory cache implementation with TTL support"""
    
    def __init__(self):
        self._cache = {}
        self._expiry = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        if key not in self._cache:
            return None
        
        # Check if expired
        if key in self._expiry and time.time() > self._expiry[key]:
            self.delete(key)
            return None
        
        return self._cache[key]
    
    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set value in cache with TTL"""
        try:
            self._cache[key] = value
            self._expiry[key] = time.time() + ttl
            return True
        except Exception:
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            if key in self._cache:
                del self._cache[key]
            if key in self._expiry:
                del self._expiry[key]
            return True
        except Exception:
            return False
    
    def clear(self) -> bool:
        """Clear all cache entries"""
        try:
            self._cache.clear()
            self._expiry.clear()
            return True
        except Exception:
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists and is not expired"""
        return self.get(key) is not None
    
    def cleanup_expired(self):
        """Remove expired entries"""
        current_time = time.time()
        expired_keys = [
            key for key, expiry in self._expiry.items()
            if current_time > expiry
        ]
        for key in expired_keys:
            self.delete(key)


class RedisCache(CacheBackend):
    """Redis cache implementation"""
    
    def __init__(self, host: str = 'localhost', port: int = 6379, 
                 db: int = 0, password: Optional[str] = None):
        try:
            import redis
            self.redis = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=True
            )
            # Test connection
            self.redis.ping()
        except ImportError:
            raise ImportError("redis package is required for RedisCache. Install with: pip install redis")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Redis: {e}")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache"""
        try:
            value = self.redis.get(key)
            if value is None:
                return None
            return json.loads(value)
        except Exception:
            return None
    
    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set value in Redis cache with TTL"""
        try:
            serialized = json.dumps(value)
            return self.redis.setex(key, ttl, serialized)
        except Exception:
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from Redis cache"""
        try:
            return bool(self.redis.delete(key))
        except Exception:
            return False
    
    def clear(self) -> bool:
        """Clear all cache entries"""
        try:
            self.redis.flushdb()
            return True
        except Exception:
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in Redis"""
        try:
            return bool(self.redis.exists(key))
        except Exception:
            return False


class CacheManager:
    """Manages caching operations with configurable backend"""
    
    def __init__(self, backend: Optional[CacheBackend] = None):
        """
        Initialize cache manager with specified backend.
        
        Args:
            backend: Cache backend to use. If None, uses InMemoryCache.
        """
        self.backend = backend or InMemoryCache()
        self.enabled = True
    
    def generate_key(self, prefix: str, *args, **kwargs) -> str:
        """
        Generate a cache key from function arguments.
        
        Args:
            prefix: Key prefix (usually function name)
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            str: Generated cache key
        """
        # Create a string representation of arguments
        key_parts = [prefix]
        
        # Add positional arguments
        for arg in args:
            if isinstance(arg, (str, int, float, bool)):
                key_parts.append(str(arg))
            else:
                # For complex objects, use their string representation
                key_parts.append(str(arg))
        
        # Add keyword arguments (sorted for consistency)
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}={v}")
        
        # Create hash of the key parts
        key_string = ":".join(key_parts)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        
        return f"{prefix}:{key_hash}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.enabled:
            return None
        return self.backend.get(key)
    
    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set value in cache"""
        if not self.enabled:
            return False
        return self.backend.set(key, value, ttl)
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        return self.backend.delete(key)
    
    def clear(self) -> bool:
        """Clear all cache entries"""
        return self.backend.clear()
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self.enabled:
            return False
        return self.backend.exists(key)
    
    def enable(self):
        """Enable caching"""
        self.enabled = True
    
    def disable(self):
        """Disable caching"""
        self.enabled = False


# Global cache manager instance
_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """
    Get or create the global cache manager instance.
    
    Returns:
        CacheManager: Global cache manager
    """
    global _cache_manager
    
    if _cache_manager is None:
        # Check environment for cache configuration
        cache_type = os.getenv('CACHE_TYPE', 'memory').lower()
        
        if cache_type == 'redis':
            try:
                backend = RedisCache(
                    host=os.getenv('REDIS_HOST', 'localhost'),
                    port=int(os.getenv('REDIS_PORT', '6379')),
                    db=int(os.getenv('REDIS_DB', '0')),
                    password=os.getenv('REDIS_PASSWORD')
                )
                print("Using Redis cache backend")
            except Exception as e:
                print(f"Failed to initialize Redis cache: {e}")
                print("Falling back to in-memory cache")
                backend = InMemoryCache()
        else:
            backend = InMemoryCache()
            print("Using in-memory cache backend")
        
        _cache_manager = CacheManager(backend)
    
    return _cache_manager


def cached(ttl: int = 300, key_prefix: Optional[str] = None):
    """
    Decorator to cache function results.
    
    Args:
        ttl: Time to live in seconds (default: 300 = 5 minutes)
        key_prefix: Custom key prefix (default: function name)
        
    Example:
        @cached(ttl=600)
        def get_person(person_id):
            return expensive_api_call(person_id)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_cache_manager()
            
            # Generate cache key
            prefix = key_prefix or func.__name__
            cache_key = cache.generate_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Call function and cache result
            result = func(*args, **kwargs)
            
            # Only cache non-None results
            if result is not None:
                cache.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


def invalidate_cache(key_prefix: str, *args, **kwargs):
    """
    Invalidate cache for specific function call.
    
    Args:
        key_prefix: Function name or custom prefix
        *args: Positional arguments used in original call
        **kwargs: Keyword arguments used in original call
    """
    cache = get_cache_manager()
    cache_key = cache.generate_key(key_prefix, *args, **kwargs)
    cache.delete(cache_key)


def clear_all_cache():
    """Clear all cached data"""
    cache = get_cache_manager()
    cache.clear()