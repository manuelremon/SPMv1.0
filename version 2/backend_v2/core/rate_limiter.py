from typing import Optional, Callable, Tuple
import time
from functools import wraps
from flask import request

try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
except Exception:
    Limiter = None


_BUCKETS = {}


def _parse_rate(rate: str) -> Tuple[int, int]:
    # simple parser: '5/minute', '10/second'
    if '/' not in rate:
        return (1, 60)
    parts = rate.split('/')
    try:
        n = int(parts[0])
    except Exception:
        n = 1
    unit = parts[1]
    if unit.startswith('second'):
        sec = 1
    elif unit.startswith('minute'):
        sec = 60
    elif unit.startswith('hour'):
        sec = 3600
    elif unit.startswith('day'):
        sec = 86400
    else:
        sec = 60
    return (n, sec)


def in_memory_limit(rate: str):
    n, sec = _parse_rate(rate)

    def decorator(fn: Callable):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            key = request.remote_addr or 'global'
            bucket_key = (key, request.endpoint)
            now = int(time.time())
            entry = _BUCKETS.get(bucket_key)
            if not entry:
                entry = {'count': 1, 'reset': now + sec}
                _BUCKETS[bucket_key] = entry
            else:
                if now > entry['reset']:
                    entry['count'] = 1
                    entry['reset'] = now + sec
                else:
                    entry['count'] += 1
            if entry['count'] > n:
                from flask import jsonify

                return jsonify({'error': 'too many requests'}), 429
            return fn(*args, **kwargs)

        return wrapper

    return decorator


class RateLimiter:
    def __init__(self, app=None, key_func=None, default_limits=None, storage_uri: Optional[str] = None):
        self.enabled = Limiter is not None
        if self.enabled:
            self.limiter = Limiter(key_func=key_func, app=app, default_limits=default_limits)
        else:
            self.limiter = None

    def init_app(self, app, **kwargs):
        if self.enabled:
            self.limiter.init_app(app)

    def limit(self, rate: str):
        if self.enabled and self.limiter is not None:
            return self.limiter.limit(rate)
        return in_memory_limit(rate)


def reset_buckets():
    global _BUCKETS
    _BUCKETS = {}
