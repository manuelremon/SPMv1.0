"""Backend v2.0 - API Routes"""

from routes.auth import bp as auth_bp
from routes.health import bp as health_bp
from routes.solicitudes import bp as solicitudes_bp
from routes.planner import planner_bp

__all__ = ["auth_bp", "health_bp", "solicitudes_bp", "planner_bp"]
