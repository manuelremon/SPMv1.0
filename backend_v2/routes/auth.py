"""
Authentication routes
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict

import bcrypt
import jwt
from flask import Blueprint, jsonify, request, g
from jwt import InvalidTokenError

from core.config import settings

bp = Blueprint("auth", __name__)

# Demo user (replace with DB in production)
DEMO_USER = {
    "id": "1",
    "username": "admin",
    "password_hash": bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode(),
    "email": "admin@spm.local",
    "nombre": "Administrador",
    "rol": "admin",
}


def generate_tokens(user_id: str) -> dict:
    """Generate access and refresh tokens"""
    now = datetime.utcnow()

    access_payload = {
        "user_id": user_id,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(seconds=settings.JWT_ACCESS_TOKEN_EXPIRES),
    }
    refresh_payload = {
        "user_id": user_id,
        "type": "refresh",
        "iat": now,
        "exp": now + timedelta(seconds=settings.JWT_REFRESH_TOKEN_EXPIRES),
    }

    access_token = jwt.encode(access_payload, settings.JWT_SECRET_KEY, algorithm="HS256")
    refresh_token = jwt.encode(refresh_payload, settings.JWT_SECRET_KEY, algorithm="HS256")

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


def _get_token_from_request(cookie_name: str) -> str | None:
    """Get token from Authorization header or cookie"""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header.split(" ", 1)[1].strip()
    return request.cookies.get(cookie_name)


def _decode_token(expected_type: str, cookie_name: str) -> Dict[str, Any] | tuple:
    token = _get_token_from_request(cookie_name)
    if not token:
        return (
            jsonify(
                {
                    "ok": False,
                    "error": {"code": "unauthorized", "message": "Missing token"},
                }
            ),
            401,
        )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        if payload.get("type") != expected_type:
            raise InvalidTokenError("Invalid token type")
        return payload
    except InvalidTokenError:
        return (
            jsonify(
                {
                    "ok": False,
                    "error": {"code": "unauthorized", "message": "Invalid token"},
                }
            ),
            401,
        )


def _safe_json():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None
    return data


@bp.route("/login", methods=["POST"])
def login():
    """Login endpoint"""
    data = _safe_json()
    if data is None:
        return (
            jsonify(
                {
                    "ok": False,
                    "error": {
                        "code": "validation_error",
                        "message": "Invalid JSON payload",
                    },
                }
            ),
            400,
        )

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return (
            jsonify(
                {
                    "ok": False,
                    "error": {
                        "code": "validation_error",
                        "message": "Username and password are required",
                    },
                }
            ),
            400,
        )

    # Verify credentials (demo only)
    if username != DEMO_USER["username"]:
        return (
            jsonify(
                {
                    "ok": False,
                    "error": {
                        "code": "invalid_credentials",
                        "message": "Invalid username or password",
                    },
                }
            ),
            401,
        )

    if not bcrypt.checkpw(password.encode(), DEMO_USER["password_hash"].encode()):
        return (
            jsonify(
                {
                    "ok": False,
                    "error": {
                        "code": "invalid_credentials",
                        "message": "Invalid username or password",
                    },
                }
            ),
            401,
        )

    tokens = generate_tokens(DEMO_USER["id"])

    response = jsonify(
        {
            "ok": True,
            "message": "Login successful",
            "user": {
                "id": DEMO_USER["id"],
                "username": DEMO_USER["username"],
                "email": DEMO_USER["email"],
                "nombre": DEMO_USER["nombre"],
                "rol": DEMO_USER["rol"],
            },
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
        }
    )

    response.set_cookie(
        "spm_token",
        tokens["access_token"],
        httponly=True,
        secure=settings.JWT_COOKIE_SECURE,
        samesite=settings.JWT_COOKIE_SAMESITE,
        max_age=settings.JWT_ACCESS_TOKEN_EXPIRES,
    )
    response.set_cookie(
        "spm_token_refresh",
        tokens["refresh_token"],
        httponly=True,
        secure=settings.JWT_COOKIE_SECURE,
        samesite=settings.JWT_COOKIE_SAMESITE,
        max_age=settings.JWT_REFRESH_TOKEN_EXPIRES,
    )

    return response, 200


@bp.route("/me", methods=["GET"])
def get_me():
    """Get current user"""
    payload = _decode_token(expected_type="access", cookie_name="spm_token")
    if isinstance(payload, tuple):
        return payload

    return (
        jsonify(
            {
                "ok": True,
                "user": {
                    "id": payload.get("user_id"),
                    "username": DEMO_USER["username"],
                    "email": DEMO_USER["email"],
                    "nombre": DEMO_USER["nombre"],
                    "rol": DEMO_USER["rol"],
                },
            }
        ),
        200,
    )


@bp.route("/refresh", methods=["POST"])
def refresh():
    """Refresh access token"""
    payload = _decode_token(expected_type="refresh", cookie_name="spm_token_refresh")
    if isinstance(payload, tuple):
        return payload

    tokens = generate_tokens(payload["user_id"])

    response = jsonify(
        {
            "ok": True,
            "message": "Token refreshed",
            "access_token": tokens["access_token"],
        }
    )

    response.set_cookie(
        "spm_token",
        tokens["access_token"],
        httponly=True,
        secure=settings.JWT_COOKIE_SECURE,
        samesite=settings.JWT_COOKIE_SAMESITE,
        max_age=settings.JWT_ACCESS_TOKEN_EXPIRES,
    )

    return response, 200


@bp.route("/logout", methods=["POST"])
def logout():
    """Logout"""
    response = jsonify({"ok": True, "message": "Logged out successfully"})

    response.set_cookie("spm_token", "", max_age=0)
    response.set_cookie("spm_token_refresh", "", max_age=0)
    response.set_cookie("spm_csrf", "", max_age=0)

    return response, 200


@bp.route("/register", methods=["POST"])
def register():
    """Registration stub (demo only)"""
    return (
        jsonify(
            {
                "ok": False,
                "error": {
                    "code": "not_implemented",
                    "message": "Registration endpoint not available in demo",
                },
            }
        ),
        501,
    )


@bp.route("/csrf", methods=["GET"])
def get_csrf_token():
    """Return CSRF token for clients"""
    token = getattr(g, "csrf_token", None)
    if not token:
        return (
            jsonify(
                {
                    "ok": False,
                    "error": {
                        "code": "csrf_error",
                        "message": "Unable to generate CSRF token",
                    },
                }
            ),
            500,
        )

    return jsonify({"ok": True, "csrf_token": token}), 200
