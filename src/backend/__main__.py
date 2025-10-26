"""Punto de entrada para ejecutar la aplicación Flask como módulo."""
import os
from .app import app

if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "5000"))
    print(f"🚀 Servidor SPM iniciando en http://{host}:{port}")
    print(f"📍 API base: http://{host}:{port}/api")
    print(f"🔗 Frontend: http://{host}:{port}/")
    app.run(host=host, port=port, debug=False, use_reloader=False, threaded=True)
