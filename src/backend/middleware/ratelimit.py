"""
Rate Limiting Middleware

Implements token bucket rate limiting by IP address.
Supports different rate limits for different endpoint types.

Usage:
    from middleware.ratelimit import limit, apply_rate_limits

    @bp.route('/login')
    @limit('login', limit=5, window=60)  # 5 requests per minute
    def login():
        pass

    # Or apply globally in app.py:
    apply_rate_limits(app)
"""

import time
from collections import deque, defaultdict
from functools import wraps
from flask import request, jsonify, current_app, Flask
import logging

logger = logging.getLogger(__name__)

_buckets = defaultdict(deque)  # key -> deque[timestamps]
_CLEANUP_INTERVAL = 300  # Clean old buckets every 5 minutes
_last_cleanup = time.monotonic()

def _now():
    """Get current monotonic time."""
    return time.monotonic()

def _cleanup_old_buckets():
    """Periodically cleanup old buckets to prevent memory leaks."""
    global _last_cleanup
    now = _now()
    if now - _last_cleanup < _CLEANUP_INTERVAL:
        return

    _last_cleanup = now
    # Remove buckets that haven't been used in the last hour
    cutoff = now - 3600
    keys_to_remove = []

    for key, bucket in _buckets.items():
        if bucket and bucket[-1] < cutoff:
            keys_to_remove.append(key)

    for key in keys_to_remove:
        del _buckets[key]

    if keys_to_remove:
        logger.info(f"Cleaned up {len(keys_to_remove)} old rate limit buckets")

def _check(key, limit, window):
    """
    Check if request is within rate limit using token bucket algorithm.

    Args:
        key: Unique key for this bucket (typically endpoint:ip)
        limit: Maximum number of requests allowed
        window: Time window in seconds

    Returns:
        True if request is allowed, False if rate limited
    """
    q = _buckets[key]
    t = _now()

    # Remove expired timestamps from bucket
    cutoff = t - window
    while q and q[0] <= cutoff:
        q.popleft()

    # Check if limit exceeded
    if len(q) >= limit:
        return False

    # Add current timestamp
    q.append(t)

    # Periodic cleanup
    _cleanup_old_buckets()

    return True

def _get_client_ip():
    """
    Extract client IP address from request.
    Handles proxied requests (X-Forwarded-For, X-Real-IP).

    Returns:
        Client IP address as string
    """
    # Check for proxied IP
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        # X-Forwarded-For can contain multiple IPs, take the first
        return forwarded_for.split(',')[0].strip()

    real_ip = request.headers.get('X-Real-IP')
    if real_ip:
        return real_ip.strip()

    # Fallback to direct connection IP
    return request.remote_addr or 'unknown'

def limit(key='rl', limit=30, window=60):
    """
    Rate limiting decorator using token bucket algorithm.

    Args:
        key: Identifier for this rate limit bucket (e.g., 'login', 'api')
        limit: Maximum number of requests allowed
        window: Time window in seconds

    Returns:
        Decorator function

    Example:
        @bp.route('/login')
        @limit('login', limit=5, window=60)  # 5 requests per minute
        def login():
            pass
    """
    def deco(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            ip = _get_client_ip()
            bucket_key = f'{key}:{ip}'

            if not _check(bucket_key, limit, window):
                logger.warning(
                    f"Rate limit exceeded for {key} from IP {ip}. "
                    f"Limit: {limit} requests per {window}s"
                )
                return jsonify({
                    'error': 'rate_limited',
                    'message': f'Rate limit exceeded. Try again in {window} seconds.',
                    'retry_after': window
                }), 429

            return f(*args, **kwargs)
        return wrapper
    return deco

def apply_rate_limits(app: Flask):
    """
    Apply global rate limiting to the Flask app.

    This adds a before_request handler that rate limits ALL API endpoints
    with a generous default limit. Individual endpoints can have stricter
    limits using the @limit decorator.

    Args:
        app: Flask application instance

    Example:
        app = Flask(__name__)
        apply_rate_limits(app)
    """
    @app.before_request
    def _global_rate_limit():
        # Skip rate limiting for non-API routes
        if not request.path.startswith('/api'):
            return None

        # Skip health checks
        if request.path in ['/api/health', '/healthz']:
            return None

        # Global rate limit: 100 requests per minute per IP
        ip = _get_client_ip()
        bucket_key = f'global:{ip}'

        if not _check(bucket_key, limit=100, window=60):
            logger.warning(f"Global rate limit exceeded from IP {ip}")
            return jsonify({
                'error': 'rate_limited',
                'message': 'Too many requests. Please slow down.',
                'retry_after': 60
            }), 429

        return None
