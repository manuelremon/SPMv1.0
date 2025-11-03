#!/usr/bin/env python
"""Simple Flask backend launcher for SPM"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # Import and run the app
    from src.backend.app import app
    
    # Get host and port from environment or use defaults
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "5000"))
    
    print(f"\n{'='*60}")
    print(f"🚀 INICIANDO BACKEND SPM")
    print(f"{'='*60}")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"URL: http://{host}:{port}")
    print(f"{'='*60}\n")
    
    # Run Flask development server
    app.run(
        host=host,
        port=port,
        debug=False,
        use_reloader=False,
        threaded=True
    )
