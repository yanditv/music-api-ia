#!/usr/bin/env python3
"""
Script de inicio rápido para la API Bark
Uso: python start.py
"""

import sys
import os

# Añadir el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import start

if __name__ == "__main__":
    print("🎵 Bark Text-to-Speech API con Música 🎵")
    print("=" * 50)
    start()
