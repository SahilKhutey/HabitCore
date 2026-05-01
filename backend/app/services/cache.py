import functools

def cached(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Simple passthrough for now, can be extended with Redis/in-memory cache
        return func(*args, **kwargs)
    return wrapper
