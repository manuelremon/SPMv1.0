"""
Auth module - Re-exports from services.auth.auth for backward compatibility
"""
from .services.auth.auth import (
    auth_required,
    auth_bp,
    authenticate_request,
    authenticate_user,
    clear_auth_cookie,
    get_current_user,
    get_current_user_id,
    issue_token,
    set_auth_cookie,
    decode_token,
    load_user_by_id,
)

__all__ = [
    "auth_required",
    "auth_bp",
    "authenticate_request",
    "authenticate_user",
    "clear_auth_cookie",
    "get_current_user",
    "get_current_user_id",
    "issue_token",
    "set_auth_cookie",
    "decode_token",
    "load_user_by_id",
]
