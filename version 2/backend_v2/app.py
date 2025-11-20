from flask import Flask, jsonify
from flask_cors import CORS

from .core.config import Settings
from .routes.health import bp as health_bp
from .routes.auth import bp as auth_bp
from .core.init_db import build_db
from .core.rate_limiter import RateLimiter
from .core.security import csrf_protect
from .routes.solicitudes import bp as solicitudes_bp
from .routes.planner import bp as planner_bp


def create_app():
    app = Flask(__name__, static_folder=None)
    app.config['DEBUG'] = Settings.DEBUG
    app.config['SECRET_KEY'] = Settings.SECRET_KEY
    app.config['MAX_CONTENT_LENGTH'] = Settings.MAX_CONTENT_LENGTH

    CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": Settings.FRONTEND_ORIGIN}})

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(solicitudes_bp)
    app.register_blueprint(planner_bp)
    # Init rate limiter (graceful: will no-op if not installed)
    rate_limiter = RateLimiter(app=app, default_limits=["200/day", "50/hour"])
    app.limiter = rate_limiter.limiter

    @app.before_request
    def _csrf_guard():
        ok = csrf_protect()
        if not ok:
            return jsonify({'error': 'CSRF token missing or invalid'}), 403
    # Ensure DB schema exists (dev only)
    try:
        build_db(force=False)
    except Exception:
        pass

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=8000)
