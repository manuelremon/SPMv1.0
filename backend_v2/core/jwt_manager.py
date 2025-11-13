"""
Backend v2.0 - JWT Manager
Emite y verifica tokens JWT con HS256, cookies HttpOnly
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from flask import Response, make_response

from core.config import settings


class JWTManager:
    """Gestor de tokens JWT para autenticación"""
    
    @staticmethod
    def create_access_token(
        payload: dict[str, Any],
        expires_delta: timedelta | None = None
    ) -> str:
        """
        Crea un token JWT firmado.
        
        Args:
            payload: Datos a incluir en el token (user_id, role, etc.)
            expires_delta: Tiempo de expiración custom (default: settings.JWT_ACCESS_TOKEN_TTL)
        
        Returns:
            Token JWT como string
        """
        to_encode = payload.copy()
        
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                seconds=settings.JWT_ACCESS_TOKEN_TTL
            )
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
        })
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> dict[str, Any] | None:
        """
        Verifica y decodifica un token JWT.
        
        Args:
            token: Token JWT a verificar
        
        Returns:
            Payload del token si es válido, None si es inválido/expirado
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            # Token expirado
            return None
        except jwt.InvalidTokenError:
            # Token inválido (firma incorrecta, formato malo, etc.)
            return None
    
    @staticmethod
    def set_token_cookie(response: Response, token: str) -> Response:
        """
        Agrega token JWT como cookie HttpOnly a la respuesta.
        
        Args:
            response: Response de Flask
            token: Token JWT a setear
        
        Returns:
            Response modificada con cookie
        """
        response.set_cookie(
            key=settings.JWT_COOKIE_NAME,
            value=token,
            httponly=settings.JWT_COOKIE_HTTPONLY,
            secure=settings.JWT_COOKIE_SECURE,
            samesite=settings.JWT_COOKIE_SAMESITE,
            max_age=settings.JWT_ACCESS_TOKEN_TTL,
        )
        return response
    
    @staticmethod
    def clear_token_cookie(response: Response) -> Response:
        """
        Elimina cookie de token (para logout).
        
        Args:
            response: Response de Flask
        
        Returns:
            Response con cookie eliminada
        """
        response.set_cookie(
            key=settings.JWT_COOKIE_NAME,
            value="",
            httponly=True,
            secure=settings.JWT_COOKIE_SECURE,
            samesite=settings.JWT_COOKIE_SAMESITE,
            max_age=0,  # Expira inmediatamente
        )
        return response


# Singleton global
jwt_manager = JWTManager()
