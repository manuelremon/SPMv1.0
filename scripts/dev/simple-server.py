#!/usr/bin/env python3
"""
Servidor HTTP simple para servir archivos HTML desde src/frontend
Útil para testing cuando Vite no coopera
"""

import http.server
import socketserver
import os
from pathlib import Path

PORT = 8080
FRONTEND_DIR = Path(__file__).parent / 'src' / 'frontend'

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND_DIR), **kwargs)
    
    def do_GET(self):
        # Si la ruta es una página conocida, sirve el HTML
        if self.path.startswith('/') and not '.' in self.path.split('/')[-1]:
            # Es una ruta limpia (sin extensión)
            html_file = FRONTEND_DIR / f"{self.path.lstrip('/')}.html"
            if html_file.exists():
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.end_headers()
                with open(html_file, 'rb') as f:
                    self.wfile.write(f.read())
                return
        
        # Si no, usa el comportamiento por defecto
        super().do_GET()

if __name__ == '__main__':
    os.chdir(FRONTEND_DIR)
    
    handler = MyHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"\n{'='*60}")
        print(f"Servidor HTTP en puerto {PORT}".center(60))
        print(f"{'='*60}")
        print(f"\nSirviendo desde: {FRONTEND_DIR}")
        print(f"URL: http://localhost:{PORT}/")
        print(f"\nRutas disponibles:")
        for html_file in sorted(FRONTEND_DIR.glob('*.html')):
            route = html_file.stem
            print(f"  http://localhost:{PORT}/{route}")
        print(f"\nPresiona Ctrl+C para detener\n")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\nServidor detenido")
