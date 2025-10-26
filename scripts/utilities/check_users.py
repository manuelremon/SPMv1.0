#!/usr/bin/env python3
"""Script para ver qué usuarios existen en la BD"""
import sqlite3
import json

DB_PATH = "src/backend/core/data/spm.db"

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=" * 70)
    print("USUARIOS EN LA BASE DE DATOS")
    print("=" * 70)
    
    cursor.execute("SELECT id, username, email FROM usuarios LIMIT 10;")
    rows = cursor.fetchall()
    
    for row in rows:
        print(f"  ID: {row[0]}, Username: {row[1]}, Email: {row[2]}")
    
    conn.close()
    
except Exception as e:
    print(f"ERROR: {e}")
