#!/usr/bin/env python
"""
Debug: decodificar token y ver qué data tiene.
"""
import sys
import os
import json
import http.cookies
import jwt

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, '.')

from flask import Flask
from src.backend.services.auth.jwt_utils import verify_access_token

app = Flask(__name__)
app.config['DATABASE'] = 'src/backend/core/data/spm.db'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

from src.backend.routes.auth_routes import bp as auth_bp
app.register_blueprint(auth_bp)

print("=" * 60)
print("DEBUG: DECODIFICAR TOKEN")
print("=" * 60)

with app.app_context():
    client = app.test_client()
    
    # 1. Login
    print("\n1. Login...")
    login_response = client.post(
        '/api/auth/login',
        json={"username": "2", "password": "a1"},
        headers={'Content-Type': 'application/json'}
    )
    print(f"   Status: {login_response.status_code}")
    
    if login_response.status_code == 200:
        # 2. Extraer token
        print("\n2. Extrayendo token...")
        set_cookie_header = login_response.headers.get('Set-Cookie', '')
        cookie = http.cookies.SimpleCookie()
        cookie.load(set_cookie_header)
        token = cookie.get('access_token')
        if token:
            token_value = token.value
            print(f"   ✓ Token: {token_value[:40]}...")
            
            # 3. Decodificar sin verificación (para ver qué data hay)
            print("\n3. Decodificando token (sin verificación)...")
            try:
                decoded = jwt.decode(token_value, options={"verify_signature": False})
                print(f"   Payload: {json.dumps(decoded, indent=2)}")
            except Exception as e:
                print(f"   Error: {e}")
            
            # 4. Intentar verificar con verify_access_token
            print("\n4. Verificando con verify_access_token()...")
            try:
                claims = verify_access_token(token_value)
                print(f"   ✓ Válido: {json.dumps(claims, indent=2)}")
            except Exception as e:
                print(f"   ✗ Error: {e}")
                print(f"   Tipo: {type(e).__name__}")

print("\n✓ Debug completado")
