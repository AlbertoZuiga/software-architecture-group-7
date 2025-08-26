from django.core.cache import cache
from functools import wraps
import hashlib

# Cache time in seconds (5 minutes)
CACHE_TTL = 300


def get_cache_key(model_name, obj_id):
    """Generate a consistent cache key format"""
    return f"{model_name.lower()}:{obj_id}"


def get_from_cache_or_db(model_name, obj_id, query_func):
    """
    Try to get an object from cache, or query the database if not found
    
    Args:
        model_name (str): Model name for cache key
        obj_id: Object ID 
        query_func (callable): Function to execute if cache miss
        
    Returns:
        The cached or database-queried object
    """
    cache_key = get_cache_key(model_name, obj_id)
    cached_obj = cache.get(cache_key)

    if cached_obj is None:
        db_obj = query_func()

        if db_obj is not None:
            cache.set(cache_key, db_obj, CACHE_TTL)

        return db_obj

    return cached_obj


def invalidate_cache(model_name, obj_id):
    """Delete a specific object from cache"""
    cache_key = get_cache_key(model_name, obj_id)
    cache.delete(cache_key)


def cached_method(ttl=CACHE_TTL):
    """
    Decorator for caching method results
    
    Usage:
        @cached_method()
        def get_something(self, key):
            # Expensive operation
            return result
    """
    def decorator(func):
        @wraps(func)
        def wrapped(instance, *args, **kwargs):
            instance_id = getattr(instance, 'id', 'unknown')
            cache_key = f"method:{func.__name__}:{instance.__class__.__name__}:{instance_id}"

            if args or kwargs:
                args_str = str(args)
                kwargs_str = str(sorted(kwargs.items()))
                hash_obj = hashlib.md5((args_str + kwargs_str).encode())
                cache_key += ":" + hash_obj.hexdigest()

            result = cache.get(cache_key)
            if result is None:
                result = func(instance, *args, **kwargs)
                cache.set(cache_key, result, ttl)
            return result
        return wrapped
    return decorator
