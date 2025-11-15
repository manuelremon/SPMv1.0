"""
Backend v2.0 - JWT Manager
Emite, verifica y refresca tokens JWT con HS256, cookies HttpOnly
Soporta access tokens (short-lived) y refresh tokens (long-lived)
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from flask import Response, make_response

from core.config import settings


class JWTManager:
    """Gestor de tokens JWT para autenticación con refresh tokens"""
    
    # Constantes de tipos de token
    TOKEN_TYPE_ACCESS = "access"
    TOKEN_TYPE_REFRESH = "refresh"
    
    @staticmethod
    def create_access_token(
        payload: dict[str, Any],
        expires_delta: timedelta | None = None
    ) -> str:
        """
        Crea un token JWT de acceso (short-lived).
        
        Args:
            payload: Datos a incluir en el token (user_id, role, etc.)
            expires_delta: Tiempo de expiración custom (default: settings.JWT_ACCESS_TOKEN_TTL)
        
        Returns:
            Token JWT como string
        
        Uso:
            token = jwt_manager.create_access_token({
                "sub": user.id,
                "username": user.username,
                "role": user.role
            })
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
            "type": JWTManager.TOKEN_TYPE_ACCESS,
        })
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(
        payload: dict[str, Any],
        expires_delta: timedelta | None = None
    ) -> str:
        """
        Crea un token JWT de refresco (long-lived).
        
        Los refresh tokens tienen mayor tiempo de vida y se usan SOLO
        para obtener nuevos access tokens. Nunca se envían a otros endpoints.
        
        Args:
            payload: Datos a incluir en el token (usualmente solo user_id)
            expires_delta: Tiempo de expiración custom (default: 7 días)
        
        Returns:
            Token JWT como string
        
        Uso:
            refresh_token = jwt_manager.create_refresh_token({
                "sub": user.id
            })
        """
        to_encode = payload.copy()
        
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            # Refresh tokens duran 7 días por defecto
            expire = datetime.now(timezone.utc) + timedelta(days=7)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": JWTManager.TOKEN_TYPE_REFRESH,
        })
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        
        return encoded_jwt
    
    @staticmethod
    def verify_token(
        token: str,
        token_type: str | None = None
    ) -> dict[str, Any] | None:
        """
        Verifica y decodifica un token JWT.
        
        Args:
            token: Token JWT a verificar
            token_type: Tipo de token esperado ("access", "refresh", o None para ignorar)
        
        Returns:
            Payload del token si es válido, None si es inválido/expirado
        
        Uso:
            payload = jwt_manager.verify_token(token)
            if payload and payload["type"] == "access":
                user_id = payload["sub"]
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            
            # Validar tipo de token si se especifica
            if token_type and payload.get("type") != token_type:
                return None
            
            return payload
        except jwt.ExpiredSignatureError:
            # Token expirado
            return None
        except jwt.InvalidTokenError:
            # Token inválido (firma incorrecta, formato malo, etc.)
            return None
    
    @staticmethod
    def set_token_cookie(
        response: Response,
        token: str,
        token_type: str = "access"
    ) -> Response:
        """
        Agrega token JWT como cookie HttpOnly a la respuesta.
        
        Args:
            response: Response de Flask
            token: Token JWT a setear
            token_type: Tipo de cookie ("access" o "refresh")
        
        Returns:
            Response modificada con cookie
        
        Uso:
            response = make_response(jsonify({"ok": True}))
            response = jwt_manager.set_token_cookie(response, token)
            return response
        """
        cookie_name = (
            settings.JWT_COOKIE_NAME if token_type == "access"
            else f"{settings.JWT_COOKIE_NAME}_refresh"
        )
        
        # Access tokens: corta duración
        # Refresh tokens: más larga duración
        max_age = (
            settings.JWT_ACCESS_TOKEN_TTL if token_type == "access"
            else 7 * 24 * 60 * 60  # 7 días
        )
        
        response.set_cookie(
            key=cookie_name,
            value=token,
            httponly=settings.JWT_COOKIE_HTTPONLY,
            secure=settings.JWT_COOKIE_SECURE,
            samesite=settings.JWT_COOKIE_SAMESITE,
            max_age=max_age,
            path="/",  # Disponible en toda la aplicación
        )
        return response
    
    @staticmethod
    def clear_token_cookie(response: Response) -> Response:
        """
        Elimina cookies de token (para logout).
        
        Args:
            response: Response de Flask
        
        Returns:
            Response con cookies eliminadas
        """
        for cookie_name in [
            settings.JWT_COOKIE_NAME,
            f"{settings.JWT_COOKIE_NAME}_refresh"
        ]:
            response.set_cookie(
                key=cookie_name,
                value="",
                httponly=True,
                secure=settings.JWT_COOKIE_SECURE,
                samesite=settings.JWT_COOKIE_SAMESITE,
                max_age=0,  # Expira inmediatamente
                path="/",
            )
        return response


# Singleton global
jwt_manager = JWTManager()

