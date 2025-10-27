#!/usr/bin/env python3
"""
Script para probar las APIs de horarios con autenticación
"""

import requests
import json
from datetime import datetime

# Base URL del sistema
BASE_URL = "http://127.0.0.1:8000"
SCHEDULE_API_BASE = f"{BASE_URL}/academic-system/schedules"

def test_with_authentication():
    """Prueba las APIs con una sesión autenticada"""
    print("🔄 PROBANDO APIs CON AUTENTICACIÓN")
    print("=" * 50)
    
    # Crear una sesión
    session = requests.Session()
    
    # Primero obtener la página de login para obtener el CSRF token
    login_page = session.get(f"{BASE_URL}/auth/login/")
    csrf_token = None
    
    if login_page.status_code == 200:
        # Buscar el CSRF token en el contenido
        content = login_page.text
        start = content.find('csrfmiddlewaretoken') 
        if start != -1:
            start = content.find('value="', start) + 7
            end = content.find('"', start)
            csrf_token = content[start:end]
            print(f"✓ CSRF token obtenido: {csrf_token[:20]}...")
    
    # Intentar login con credenciales de prueba
    login_data = {
        'username': 'admin',  # Asumiendo que existe un usuario admin
        'password': 'admin123',  # Contraseña común de prueba
        'csrfmiddlewaretoken': csrf_token
    }
    
    login_response = session.post(f"{BASE_URL}/auth/login/", data=login_data)
    print(f"Login Status: {login_response.status_code}")
    
    if login_response.status_code == 302:  # Redirección después del login exitoso
        print("✓ Login exitoso!")
    else:
        print("⚠ Login falló, probando sin autenticación...")
    
    # Ahora probar las APIs con la sesión
    endpoints = [
        (f"{SCHEDULE_API_BASE}/api/", "Lista de horarios"),
        (f"{SCHEDULE_API_BASE}/resources/", "Recursos del sistema"),
        (f"{SCHEDULE_API_BASE}/matrix/", "Matriz de horarios"),
    ]
    
    for url, description in endpoints:
        print(f"\n{'='*30}")
        print(f"Probando: {description}")
        print(f"URL: {url}")
        
        response = session.get(url)
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            if 'application/json' in content_type:
                print("✓ Respuesta JSON correcta")
                try:
                    data = response.json()
                    print(f"Datos: {list(data.keys()) if isinstance(data, dict) else f'{len(data)} elementos'}")
                except:
                    print("⚠ Error al parsear JSON")
            else:
                print("⚠ Respuesta HTML (no API)")
                print(f"Contenido: {response.text[:100]}...")
        else:
            print(f"✗ Error: {response.status_code}")

def test_direct_api_access():
    """Prueba acceso directo a las APIs"""
    print("\n🔄 PROBANDO ACCESO DIRECTO A APIs")
    print("=" * 50)
    
    # Probar las APIs directamente con headers específicos
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'  # Indica que es una petición AJAX
    }
    
    endpoints = [
        (f"{SCHEDULE_API_BASE}/api/", "Lista de horarios"),
        (f"{SCHEDULE_API_BASE}/resources/", "Recursos del sistema"),
        (f"{SCHEDULE_API_BASE}/matrix/", "Matriz de horarios"),
    ]
    
    for url, description in endpoints:
        print(f"\n{'='*30}")
        print(f"Probando: {description}")
        print(f"URL: {url}")
        
        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            if 'application/json' in content_type:
                print("✓ Respuesta JSON correcta")
            else:
                print("⚠ Respuesta HTML")
                # Verificar si contiene el mensaje "Por implementar"
                if "Por implementar" in response.text:
                    print("❌ La página muestra 'Por implementar'")
                else:
                    print(f"Contenido: {response.text[:200]}...")

if __name__ == "__main__":
    test_with_authentication()
    test_direct_api_access()