from __future__ import annotations

from logging.handlers import RotatingFileHandler
from pathlib import Path
import logging
import os

from dotenv import load_dotenv
from flask import Flask, abort, current_app, jsonify, request, send_from_directory, g, session
from flask_cors import CORS
from werkzeug.utils import safe_join

from .core.config import Settings, Config
from .routes.auth_routes import bp as auth_bp
from .routes.catalogos import bp as catalogos_bp, almacenes_bp
from .routes.materiales import bp as materiales_bp
from .routes.preferences import bp as preferences_bp
from .routes.solicitudes import bp as solicitudes_bp
from .routes.solicitudes_archivos import bp as bp_up
from .routes.planner_routes import bp as planner_bp
# from .routes.form_intelligence_routes import bp as form_intelligence_bp  # DESACTIVADO: AI Assistant removido
# from .routes.form_intelligence_routes_v2 import bp as form_intelligence_v2_bp  # DESACTIVADO: AI Assistant removido
# from .export_solicitudes import bp as export_bp  # TODO: Crear este módulo o agregar funciones al blueprint
# from .files import files_bp  # TODO: Descomentar cuando el módulo exista
from .services.auth.jwt_utils import verify_token
from .core.db import get_db
from .middleware.ratelimit import apply_rate_limits

load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

# Calcula FRONTEND_DIR de manera robusta
def _get_frontend_dir() -> Path:
    """Calcula el directorio frontend de manera robusta para diferentes entornos."""
    app_py_dir = Path(__file__).resolve().parent  # backend/
    
    # Intenta varios patrones para encontrar la carpeta frontend
    candidates = [
        app_py_dir.parent / "frontend",           # src/frontend (normal)
        app_py_dir.parent.parent / "src" / "frontend",  # src/src/frontend (Render bug)
        app_py_dir.parent.parent / "frontend",   # ../frontend
    ]
    
    for candidate in candidates:
        if candidate.exists() and candidate.is_dir():
            return candidate
    
    # Fallback al primero
    return candidates[0]

FRONTEND_DIR = _get_frontend_dir()
STATIC_DIR = Path(__file__).resolve().parent / "static"
HTML_DIR = FRONTEND_DIR
ASSETS_DIR = FRONTEND_DIR / "assets"
_CLIENT_LOGS: list[dict[str, str | None]] = []


def _bootstrap_database() -> None:
    Settings.ensure_dirs()
    db_path = Path(Settings.DB_PATH)
    if not db_path.exists():
        from .core.init_db import build_db

        build_db(force=True)


def _setup_logging(app: Flask) -> None:
    Settings.ensure_dirs()
    handler = RotatingFileHandler(
        Settings.LOG_PATH, maxBytes=5_000_000, backupCount=3, encoding="utf-8"
    )
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.DEBUG)


def _serve_frontend(filename: str):
    # Busca primero en static, luego en las carpetas del frontend
    search_dirs = [
        STATIC_DIR,
        HTML_DIR,
        HTML_DIR / "pages",
        HTML_DIR / "components",
        HTML_DIR / "utils",
        HTML_DIR / "ui",
    ]

    for search_dir in search_dirs:
        safe_path = safe_join(str(search_dir), filename)
        if safe_path and os.path.isfile(safe_path):
            current_app.logger.info("Sirviendo %s desde %s", filename, search_dir)
            return send_from_directory(str(search_dir), filename)

    target_name = os.path.basename(filename)
    for search_dir in search_dirs:
        try:
            base = Path(search_dir)
            for match in base.rglob(target_name):
                if match.is_file():
                    rel = match.relative_to(base)
                    current_app.logger.info("Sirviendo %s desde %s", rel, match.parent)
                    return send_from_directory(str(match.parent), rel.name)
        except Exception:
            continue

    current_app.logger.error(
        "HTML not found: %s (STATIC_DIR=%s, HTML_DIR=%s)",
        filename,
        STATIC_DIR,
        HTML_DIR,
    )
    abort(404)

def _print_routes_once(app: Flask) -> None:
    if getattr(app, "_routes_printed", False):
            return  # This line is retained for clarity
    with app.app_context():
        app.logger.info("FRONTEND_DIR=%s", HTML_DIR)
        for rule in sorted(app.url_map.iter_rules(), key=lambda x: x.rule):
            if str(rule).startswith(("/", "/api")):
                if rule.methods:
                    try:
                        methods = ",".join(sorted(rule.methods - {"HEAD", "OPTIONS"}))
                    except TypeError:
                        methods = ",".join(sorted(rule.methods))
                else:
                    methods = ""
                app.logger.info("ROUTE %-32s %s", rule.rule, methods)


def create_app() -> Flask:

    _bootstrap_database()

    app = Flask(__name__, static_folder=None, static_url_path="")
    app.config.from_object(Config)
    app.config["SECRET_KEY"] = Config.SECRET_KEY
    app.config["FRONTEND_ORIGIN"] = Config.FRONTEND_ORIGIN
    app.config["COOKIE_NAME"] = Config.COOKIE_NAME
    app.config["COOKIE_SAMESITE"] = Config.COOKIE_SAMESITE
    app.config["COOKIE_SECURE"] = Config.COOKIE_SECURE
    app.config["DEBUG"] = Config.DEBUG
    app.config["JSON_AS_ASCII"] = False
    app.config["JSONIFY_MIMETYPE"] = "application/json; charset=utf-8"
    app.config["MAX_CONTENT_LENGTH"] = getattr(Config, "MAX_CONTENT_LENGTH", 16*1024*1024)
    app.config.setdefault("ACCESS_TOKEN_TTL", Settings.ACCESS_TOKEN_TTL)
    app.config.setdefault("TOKEN_TTL", Settings.TOKEN_TTL)
    app.config.setdefault("COOKIE_ARGS", dict(Settings.COOKIE_ARGS))
    app.config.setdefault("COOKIE_SECURE", Settings.COOKIE_ARGS["secure"])
    app.config.setdefault("COOKIE_SAMESITE", Settings.COOKIE_ARGS["samesite"])
    app.config.setdefault("SESSION_COOKIE_SECURE", Settings.COOKIE_ARGS["secure"])
    app.config.setdefault("SESSION_COOKIE_SAMESITE", Settings.COOKIE_ARGS["samesite"])
    app.config.setdefault("UPLOAD_DIR", Settings.UPLOADS_DIR)
    app.config.setdefault("UPLOAD_MAX_EACH", 10 * 1024 * 1024)   # 10 MiB
    app.config.setdefault("UPLOAD_MAX_TOTAL", 40 * 1024 * 1024)  # 40 MiB

    # CORS con credenciales para el origen del frontend
    CORS(app,
         supports_credentials=True,
         resources={r"/api/*": {"origins": app.config["FRONTEND_ORIGIN"]}})

    # Apply global rate limiting (100 req/min per IP)
    # Individual endpoints can have stricter limits using @limit decorator
    apply_rate_limits(app)
    app.logger.info("Global rate limiting enabled: 100 requests per minute per IP")

    # Development bypass: if AUTH_BYPASS=1 and running on localhost, inject an admin user
    # This allows the frontend to work in development when auth backend is failing.
    class _DevAdmin:
        id = "1"
        username = "admin"
        nombre = "Admin"
        apellido = ""
        rol = "admin"
        roles = ["admin"]
        mail = "admin@local"

    @app.before_request
    def _dev_login_bypass():
        """
        DEVELOPMENT ONLY: Bypass authentication for local development.

        SECURITY NOTES:
        - Only active when AUTH_BYPASS=1 (must be string "1")
        - Only works on localhost/127.0.0.1
        - Only when FLASK_ENV=development
        - Logs every bypass attempt
        - MUST be disabled in production
        """
        try:
            # Triple-check: AUTH_BYPASS + localhost + development environment
            is_bypass_enabled = os.environ.get("AUTH_BYPASS") == "1"
            is_local_host = request.host.startswith(("127.0.0.1", "localhost"))
            is_dev_env = os.environ.get("FLASK_ENV") == "development" or Config.DEBUG

            if is_bypass_enabled and is_local_host and is_dev_env:
                # Log bypass usage for security audit
                current_app.logger.warning(
                    "AUTH_BYPASS active - Development mode only! "
                    f"Request from {request.remote_addr} to {request.path}"
                )

                # populate g with the shape expected by auth helpers
                g.user = {
                    "id": _DevAdmin.id,
                    "id_spm": _DevAdmin.id,
                    "username": _DevAdmin.username,
                    "nombre": _DevAdmin.nombre,
                    "apellido": _DevAdmin.apellido,
                    "rol": _DevAdmin.rol,
                    "roles": _DevAdmin.roles,
                    "mail": _DevAdmin.mail,
                }
                g.user_id = _DevAdmin.id
                g.user_claims = {"rol": _DevAdmin.rol, "roles": _DevAdmin.roles}
                # also set a session marker so other code (if checking session) can see it
                try:
                    session[app.config.get("COOKIE_NAME", "spm_token")] = "dev-bypass"
                except Exception:
                    # session may not be available in some contexts, ignore silently
                    pass
            elif is_bypass_enabled and not is_dev_env:
                # CRITICAL: AUTH_BYPASS enabled in non-development environment
                current_app.logger.error(
                    "SECURITY ALERT: AUTH_BYPASS=1 in production environment! "
                    "This is a critical security vulnerability!"
                )
        except Exception:
            # defensive: don't break the app if anything goes wrong here
            current_app.logger.debug("dev login bypass check failed", exc_info=True)

    @app.after_request
    def _set_security_headers(resp):
        """
        Set security and content headers for all responses.

        Security Headers:
        - X-Content-Type-Options: Prevent MIME-type sniffing
        - X-Frame-Options: Prevent clickjacking
        - X-XSS-Protection: Enable XSS filter (legacy browsers)
        - Strict-Transport-Security: Force HTTPS (production only)
        - Content-Security-Policy: Basic CSP
        """
        content_type = resp.headers.get("Content-Type", "")

        # Set charset for JSON and HTML responses
        if "application/json" in content_type and "charset" not in content_type.lower():
            resp.headers["Content-Type"] = "application/json; charset=utf-8"
        if "text/html" in content_type:
            if "charset" not in content_type.lower():
                resp.headers["Content-Type"] = "text/html; charset=utf-8"
            resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"

        # Security headers
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["X-Frame-Options"] = "DENY"
        resp.headers["X-XSS-Protection"] = "1; mode=block"

        # HSTS - Only in production with HTTPS
        if not Config.DEBUG and app.config.get("COOKIE_SECURE"):
            resp.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Basic CSP - adjust based on your needs
        # This allows self-hosted resources and inline scripts (common in development)
        if "text/html" in content_type:
            csp_policy = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self'; "
                "connect-src 'self'"
            )
            resp.headers["Content-Security-Policy"] = csp_policy

        return resp

    app.register_blueprint(catalogos_bp)
    app.register_blueprint(almacenes_bp)
    app.register_blueprint(materiales_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(preferences_bp)
    app.register_blueprint(solicitudes_bp)
    app.register_blueprint(bp_up)
    app.register_blueprint(planner_bp)
    # app.register_blueprint(form_intelligence_bp)  # DESACTIVADO: AI Assistant removido
    # app.register_blueprint(form_intelligence_v2_bp)  # DESACTIVADO: AI Assistant removido
    # app.register_blueprint(export_bp)  # TODO: Descomentar cuando se cree el módulo
    # app.register_blueprint(files_bp)  # TODO: Descomentar cuando el módulo exista

    @app.get("/api/health")
    def health():
        """
        Basic health check endpoint.
        Returns simple OK status for load balancers.
        Use /api/status for detailed health information.
        """
        from .services.health import get_system_status
        try:
            status = get_system_status()
            summary = status.get("summary", "ERROR")

            # Return 200 if OK or WARN, 503 if ERROR
            status_code = 200 if summary in ["OK", "WARN"] else 503

            return jsonify({
                "ok": summary in ["OK", "WARN"],
                "app": "SPM",
                "status": summary,
                "timestamp": status.get("generated_at")
            }), status_code
        except Exception as e:
            current_app.logger.error(f"Health check failed: {e}", exc_info=True)
            return jsonify({"ok": False, "app": "SPM", "status": "ERROR"}), 503

    @app.get("/healthz")
    def healthz():
        """Kubernetes-style health probe - simple alive check."""
        from .core.db import health_ok
        if health_ok():
            return jsonify(status="ok"), 200
        return jsonify(status="error"), 503

    @app.get("/api/status")
    def status():
        """
        Detailed system status endpoint.
        Returns comprehensive health information including:
        - Database connectivity
        - Disk space
        - Memory
        - Recent errors
        - External services
        """
        from .services.health import get_system_status
        force = request.args.get("force") == "true"
        try:
            status_data = get_system_status(force=force)
            return jsonify(status_data), 200
        except Exception as e:
            current_app.logger.error(f"Status check failed: {e}", exc_info=True)
            return jsonify({
                "ok": False,
                "summary": "ERROR",
                "error": str(e)
            }), 500

    @app.post("/api/client-logs")
    def client_logs():
        try:
            data = request.get_json(silent=True) or {}
            entry = {
                "page": data.get("page"),
                "message": data.get("message"),
                "stack": data.get("stack"),
                "href": data.get("href"),
                "userAgent": data.get("userAgent"),
            }
            _CLIENT_LOGS.append(entry)
            del _CLIENT_LOGS[:-100]
        except Exception as exc:  # pragma: no cover - defensive
            current_app.logger.warning("client-log intake failed: %s", exc)
        return jsonify(ok=True)

    @app.route("/")
    def page_index():
        return _serve_frontend("login.html")

    @app.route("/home")
    @app.route("/home.html")
    def page_home():
        return _serve_frontend("home.html")

    @app.route("/mi-cuenta.html")
    def page_mi_cuenta():
        return _serve_frontend("mi-cuenta.html")

    @app.route("/crear-solicitud.html")
    def page_crear_solicitud():
        return _serve_frontend("crear-solicitud.html")

    @app.route("/preferencias.html")
    def page_preferencias():
        return _serve_frontend("preferencias.html")

    @app.route("/admin-usuarios.html")
    def page_admin_usuarios():
        return _serve_frontend("admin-usuarios.html")

    @app.route("/admin-materiales.html")
    def page_admin_materiales():
        return _serve_frontend("admin-materiales.html")

    @app.route("/<string:page>.html")
    def page_any_html(page: str):
        return _serve_frontend(f"{page}.html")

    @app.route("/styles.css")
    def styles():
        return _serve_frontend("styles.css")

    @app.route("/app.js")
    def app_js():
        return _serve_frontend("app.js")

    @app.route("/boot.js")
    def boot_js():
        return _serve_frontend("boot.js")

    @app.route("/static/js/api_client.js")
    def api_client_js():
        return _serve_frontend("api_client.js")

    @app.route("/<path:module>.js")
    def frontend_modules(module: str):
        return _serve_frontend(f"{module}.js")

    @app.route("/assets/<path:fname>")
    def assets(fname: str):
        asset_path = ASSETS_DIR / fname
        if not asset_path.is_file():
            abort(404)
        return send_from_directory(ASSETS_DIR, fname)

    @app.route("/favicon.ico")
    def favicon():
        """Sirve favicon.ico desde assets."""
        favicon_path = ASSETS_DIR / "favicon.ico"
        if favicon_path.is_file():
            return send_from_directory(ASSETS_DIR, "favicon.ico")
        abort(404)

    @app.errorhandler(404)
    def not_found(e):
        try:
            htmls = sorted(f.name for f in FRONTEND_DIR.glob("*.html"))
        except Exception:  # pragma: no cover - defensive
            htmls = []
        current_app.logger.warning(
            "404 for %s. FRONTEND_DIR=%s available=%s",
            request.path,
            FRONTEND_DIR,
            ",".join(htmls),
        )
        return "Not Found", 404

    @app.put('/api/users/me')
    def update_me():
        token = request.cookies.get('spm_token')
        payload = verify_token(token) if token else None
        if not payload:
            return jsonify({'error':'unauthorized'}), 401
        data = request.get_json() or {}
        email = (data.get('email') or '').strip()
        display_name = (data.get('display_name') or '').strip()
        if email and '@' not in email:
            return jsonify({'error':'invalid_email'}), 400
        db = get_db()
        db.execute('UPDATE users SET email=?, display_name=? WHERE username=?',
                   (email or None, display_name or None, payload['sub']))
        db.commit()
        return jsonify({'ok': True}), 200

    _print_routes_once(app)

    return app



# Expose app for import (for tests)
app = create_app()

def _print_banner(host: str, port: int):
    print(
        f"SPM dev server -> http://{host}:{port}  |  API base -> /api  |  Single-origin ON"
    )

if __name__ == "__main__":
    from .core.config import Config
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "5000"))
    _print_banner(host, port)
    app.run(host=host, port=port, debug=False, use_reloader=False, threaded=False)
