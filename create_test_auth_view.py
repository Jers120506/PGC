#!/usr/bin/env python
"""
Script para crear una vista de prueba de autenticación
"""

import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')
django.setup()

from django.http import HttpResponse
from django.urls import path
from django.conf.urls import include

def test_auth_view(request):
    """Vista para probar autenticación"""
    html_path = os.path.join(os.path.dirname(__file__), 'test_auth.html')
    
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    return HttpResponse(html_content, content_type='text/html')

print("✅ Vista de prueba creada")
print("📍 Accede a: http://127.0.0.1:8000/test-auth/")
print("🔗 O sirve el archivo test_auth.html directamente en el navegador")