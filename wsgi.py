#!/usr/bin/env python
"""WSGI entry point for Gunicorn"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.backend.app import app

if __name__ == "__main__":
    app.run()
