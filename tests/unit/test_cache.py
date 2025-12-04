"""
Unit tests for caching layer
Tests cache backends and caching decorators
"""

import pytest
import time
from unittest.mock import Mock, patch
from src.cache import (
    InMemoryCache,
    CacheManager,
    cached,
    invalidate_cache,
    get_cache_manager,
    clear_all_cache
)


class TestInMemoryCache:
    """Tests for InMemoryCache backend"""
    
    def test_set_and_get(self):
        """Test setting and getting values"""
        cache = InMemoryCache()
        
        # Set value
        result = cache.set('test_key', 'test_value', ttl=60)
        assert result is True
        
        # Get value
        value = cache.get('test_key')
        assert value == 'test_value'
    
    def test_get_nonexistent_key(self):
        """Test getting a key that doesn't exist"""
        cache = InMemoryCache()
        value = cache.get('nonexistent')
        assert value is None
    
    def test_ttl_expiration(self):
        """Test that values expire after TTL"""
        cache = InMemoryCache()
        
        # Set with 1 second TTL
        cache.set('test_key', 'test_value', ttl=1)
        
        # Should exist immediately
        assert cache.get('test_key') == 'test_value'
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Should be expired
        assert cache.get('test_key') is None
    
    def test_delete(self):
        """Test deleting a key"""
        cache = InMemoryCache()
        
        cache.set('test_key', 'test_value')
        assert cache.get('test_key') == 'test_value'
        
        result = cache.delete('test_key')
        assert result is True
        assert cache.get('test_key') is None
    
    def test_delete_nonexistent(self):
        """Test deleting a nonexistent key"""
        cache = InMemoryCache()
        result = cache.delete('nonexistent')
        assert result is True  # Should succeed even if key doesn't exist
    
    def test_clear(self):
        """Test clearing all cache entries"""
        cache = InMemoryCache()
        
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')
        cache.set('key3', 'value3')
        
        result = cache.clear()
        assert result is True
        
        assert cache.get('key1') is None
        assert cache.get('key2') is None
        assert cache.get('key3') is None
    
    def test_exists(self):
        """Test checking if key exists"""
        cache = InMemoryCache()
        
        assert cache.exists('test_key') is False
        
        cache.set('test_key', 'test_value')
        assert cache.exists('test_key') is True
        
        cache.delete('test_key')
        assert cache.exists('test_key') is False
    
    def test_cleanup_expired(self):
        """Test cleanup of expired entries"""
        cache = InMemoryCache()
        
        # Set some values with short TTL
        cache.set('key1', 'value1', ttl=1)
        cache.set('key2', 'value2', ttl=10)
        
        # Wait for first to expire
        time.sleep(1.1)
        
        # Cleanup
        cache.cleanup_expired()
        
        # First should be gone, second should remain
        assert cache.get('key1') is None
        assert cache.get('key2') == 'value2'


class TestCacheManager:
    """Tests for CacheManager"""
    
    def test_initialization(self):
        """Test cache manager initialization"""
        cache = CacheManager()
        assert cache.backend is not None
        assert cache.enabled is True
    
    def test_generate_key_simple(self):
        """Test key generation with simple arguments"""
        cache = CacheManager()
        
        key = cache.generate_key('test_func', 'arg1', 'arg2')
        assert key.startswith('test_func:')
        assert len(key) > len('test_func:')
    
    def test_generate_key_with_kwargs(self):
        """Test key generation with keyword arguments"""
        cache = CacheManager()
        
        key1 = cache.generate_key('test_func', name='John', age=30)
        key2 = cache.generate_key('test_func', name='John', age=30)
        key3 = cache.generate_key('test_func', name='Jane', age=30)
        
        # Same arguments should generate same key
        assert key1 == key2
        
        # Different arguments should generate different key
        assert key1 != key3
    
    def test_enable_disable(self):
        """Test enabling and disabling cache"""
        cache = CacheManager()
        
        # Set value while enabled
        cache.set('test_key', 'test_value')
        assert cache.get('test_key') == 'test_value'
        
        # Disable cache
        cache.disable()
        assert cache.enabled is False
        
        # Get should return None when disabled
        assert cache.get('test_key') is None
        
        # Set should fail when disabled
        result = cache.set('new_key', 'new_value')
        assert result is False
        
        # Re-enable
        cache.enable()
        assert cache.enabled is True
        assert cache.get('test_key') == 'test_value'


class TestCachedDecorator:
    """Tests for @cached decorator"""
    
    def test_cached_function(self):
        """Test that function results are cached"""
        call_count = 0
        
        @cached(ttl=60)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # First call should execute function
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count == 1
        
        # Second call should use cache
        result2 = expensive_function(5)
        assert result2 == 10
        assert call_count == 1  # Should not increment
        
        # Different argument should execute function
        result3 = expensive_function(10)
        assert result3 == 20
        assert call_count == 2
    
    def test_cached_with_none_result(self):
        """Test that None results are not cached"""
        call_count = 0
        
        @cached(ttl=60)
        def function_returning_none():
            nonlocal call_count
            call_count += 1
            return None
        
        # First call
        result1 = function_returning_none()
        assert result1 is None
        assert call_count == 1
        
        # Second call should execute again (None not cached)
        result2 = function_returning_none()
        assert result2 is None
        assert call_count == 2
    
    def test_cached_with_custom_prefix(self):
        """Test cached decorator with custom key prefix"""
        @cached(ttl=60, key_prefix='custom_prefix')
        def test_function(x):
            return x * 2
        
        result = test_function(5)
        assert result == 10
        
        # Verify key was generated with custom prefix
        cache = get_cache_manager()
        key = cache.generate_key('custom_prefix', 5)
        assert cache.exists(key)
    
    def test_cached_ttl_expiration(self):
        """Test that cached values expire"""
        call_count = 0
        
        @cached(ttl=1)  # 1 second TTL
        def test_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # First call
        result1 = test_function(5)
        assert result1 == 10
        assert call_count == 1
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Should execute again after expiration
        result2 = test_function(5)
        assert result2 == 10
        assert call_count == 2


class TestCacheInvalidation:
    """Tests for cache invalidation"""
    
    def test_invalidate_cache(self):
        """Test manual cache invalidation"""
        # Clear cache before test
        clear_all_cache()
        
        call_count = 0
        
        @cached(ttl=60)
        def test_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # First call - executes function
        result1 = test_function(5)
        assert result1 == 10
        assert call_count == 1, f"Expected call_count to be 1, but got {call_count}"
        
        # Second call - uses cache
        result2 = test_function(5)
        assert result2 == 10
        assert call_count == 1, f"Expected call_count to be 1 (cached), but got {call_count}"
        
        # Invalidate cache
        invalidate_cache('test_function', 5)
        
        # Third call - executes function again
        result3 = test_function(5)
        assert result3 == 10
        assert call_count == 2, f"Expected call_count to be 2 (after invalidation), but got {call_count}"
    
    def test_clear_all_cache(self):
        """Test clearing all cache entries"""
        @cached(ttl=60)
        def func1(x):
            return x * 2
        
        @cached(ttl=60)
        def func2(x):
            return x * 3
        
        # Call both functions
        func1(5)
        func2(5)
        
        # Clear all cache
        clear_all_cache()
        
        # Verify cache is empty
        cache = get_cache_manager()
        assert not cache.exists(cache.generate_key('func1', 5))
        assert not cache.exists(cache.generate_key('func2', 5))


class TestCacheWithComplexData:
    """Tests for caching complex data structures"""
    
    def test_cache_dict(self):
        """Test caching dictionary data"""
        cache = InMemoryCache()
        
        data = {'name': 'John', 'age': 30, 'city': 'New York'}
        cache.set('user_data', data)
        
        retrieved = cache.get('user_data')
        assert retrieved == data
        assert retrieved['name'] == 'John'
    
    def test_cache_list(self):
        """Test caching list data"""
        cache = InMemoryCache()
        
        data = [1, 2, 3, 4, 5]
        cache.set('numbers', data)
        
        retrieved = cache.get('numbers')
        assert retrieved == data
        assert len(retrieved) == 5
    
    def test_cache_nested_structure(self):
        """Test caching nested data structures"""
        cache = InMemoryCache()
        
        data = {
            'user': {
                'name': 'John',
                'emails': ['john@example.com', 'john.doe@example.com']
            },
            'metadata': {
                'created': '2023-01-01',
                'updated': '2023-06-01'
            }
        }
        
        cache.set('complex_data', data)
        retrieved = cache.get('complex_data')
        
        assert retrieved == data
        assert retrieved['user']['name'] == 'John'
        assert len(retrieved['user']['emails']) == 2


class TestCacheManagerSingleton:
    """Tests for cache manager singleton behavior"""
    
    def test_get_cache_manager_singleton(self):
        """Test that get_cache_manager returns same instance"""
        cache1 = get_cache_manager()
        cache2 = get_cache_manager()
        
        assert cache1 is cache2
    
    @patch.dict('os.environ', {'CACHE_TYPE': 'memory'})
    def test_cache_manager_with_env_config(self):
        """Test cache manager respects environment configuration"""
        # Reset global cache manager
        import src.cache
        src.cache._cache_manager = None
        
        cache = get_cache_manager()
        assert cache is not None
        assert isinstance(cache.backend, InMemoryCache)


class TestCachePerformance:
    """Tests for cache performance characteristics"""
    
    def test_cache_improves_performance(self):
        """Test that caching improves performance"""
        call_times = []
        
        @cached(ttl=60)
        def slow_function(x):
            import time
            time.sleep(0.1)  # Simulate slow operation
            return x * 2
        
        # First call (uncached)
        start = time.time()
        result1 = slow_function(5)
        first_call_time = time.time() - start
        call_times.append(first_call_time)
        
        # Second call (cached)
        start = time.time()
        result2 = slow_function(5)
        second_call_time = time.time() - start
        call_times.append(second_call_time)
        
        # Cached call should be significantly faster
        assert result1 == result2
        assert second_call_time < first_call_time
        assert second_call_time < 0.01  # Should be nearly instant