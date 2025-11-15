"""
Backend v2.0 - Rate Limiting
Soporta Redis (producción) e in-memory cache (desarrollo).
Implementa token bucket algorithm para rate limiting flexible.
"""
from __future__ import annotations

import time
from typing import Optional
from functools import wraps
from collections import defaultdict

from flask import request, jsonify

from core.config import settings


class InMemoryRateLimiter:
    """
    Rate limiter en memoria para desarrollo/testing.
    Usa estructura: {identifier: {timestamp: count}}
    """
    
    def __init__(self, limit_per_minute: int = 60):
        self.limit_per_minute = limit_per_minute
        self.limit_per_second = limit_per_minute / 60
        self.requests: dict[str, list[float]] = defaultdict(list)
    
    def is_allowed(self, identifier: str) -> bool:
        """
        Verifica si el identificador puede hacer una request.
        
        Usa sliding window de 60 segundos.
        
        Args:
            identifier: IP o user_id
        
        Returns:
            True si está dentro del límite, False si excedió
        """
        now = time.time()
        window_start = now - 60
        
        # Limpiar requests antiguas
        self.requests[identifier] = [
            ts for ts in self.requests[identifier]
            if ts > window_start
        ]
        
        # Verificar si está dentro del límite
        if len(self.requests[identifier]) >= self.limit_per_minute:
            return False
        
        # Registrar request
        self.requests[identifier].append(now)
        return True
    
    def get_remaining(self, identifier: str) -> int:
        """
        Obtiene el número de requests restantes para este minuto.
        
        Args:
            identifier: IP o user_id
        
        Returns:
            Número de requests disponibles
        """
        now = time.time()
        window_start = now - 60
        
        count = sum(1 for ts in self.requests[identifier] if ts > window_start)
        return max(0, self.limit_per_minute - count)


class RedisRateLimiter:
    """
    Rate limiter con Redis para producción.
    Usa INCR y EXPIRE para contadores distribuidos.
    """
    
    def __init__(self, redis_client, limit_per_minute: int = 60):
        self.redis = redis_client
        self.limit_per_minute = limit_per_minute
    
    def is_allowed(self, identifier: str) -> bool:
        """
        Verifica si el identificador puede hacer una request.
        
        Args:
            identifier: IP o user_id
        
        Returns:
            True si está dentro del límite, False si excedió
        """
        key = f"rate_limit:{identifier}"
        
        # Pipeline para atomicidad
        pipe = self.redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, 60)  # Reset cada 60 segundos
        results = pipe.execute()
        
        count = results[0]
        return count <= self.limit_per_minute
    
    def get_remaining(self, identifier: str) -> int:
        """
        Obtiene el número de requests restantes.
        
        Args:
            identifier: IP o user_id
        
        Returns:
            Número de requests disponibles
        """
        key = f"rate_limit:{identifier}"
        count = int(self.redis.get(key) or 0)
        return max(0, self.limit_per_minute - count)


def create_rate_limiter(redis_client=None) -> InMemoryRateLimiter | RedisRateLimiter:
    """
    Factory para crear el rate limiter apropiado según entorno.
    
    Args:
        redis_client: Cliente de Redis (requerido en producción)
    
    Returns:
        InMemoryRateLimiter en dev/test, RedisRateLimiter en producción
    """
    if settings.ENV == "production" and redis_client:
        return RedisRateLimiter(
            redis_client,
            limit_per_minute=settings.RATE_LIMIT_PER_MINUTE
        )
    
    # Default: in-memory para desarrollo
    return InMemoryRateLimiter(
        limit_per_minute=settings.RATE_LIMIT_PER_MINUTE
    )


# Singleton global (actualizar en app factory si usas Redis)
rate_limiter: InMemoryRateLimiter | RedisRateLimiter = create_rate_limiter()


def require_rate_limit(f):
    """
    Decorator para endpoints con rate limiting.
    
    Usa IP del cliente como identificador.
    Responde con 429 si se excede el límite.
    
    Uso:
        @app.post('/api/auth/login')
        @require_rate_limit
        def login():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not settings.RATE_LIMIT_ENABLED:
            return f(*args, **kwargs)
        
        # Obtener IP del cliente (considerar X-Forwarded-For para proxies)
        identifier = (
            request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
            or request.remote_addr
            or "unknown"
        )
        
        if not rate_limiter.is_allowed(identifier):
            remaining = 0
            return jsonify({
                "ok": False,
                "error": {
                    "code": "rate_limit_exceeded",
                    "message": f"Rate limit exceeded. Max {settings.RATE_LIMIT_PER_MINUTE} requests per minute.",
                    "retry_after": 60
                }
            }), 429
        
        return f(*args, **kwargs)
    
    return decorated_function

