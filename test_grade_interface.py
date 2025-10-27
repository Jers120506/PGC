#!/usr/bin/env python
"""
Script para probar la funcionalidad de grados desde el navegador
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client

def test_grade_functionality():
    """Probar la funcionalidad de grados con sesión activa"""
    
    print("=== PROBANDO FUNCIONALIDAD DE GRADOS CON SESIÓN ===")
    
    # Crear cliente de prueba
    client = Client()
    
    # Hacer login
    print("1. Haciendo login...")
    user = User.objects.get(username='admin')
    client.force_login(user)
    print(f"✅ Login exitoso como: {user.username}")
    
    # Acceder a la página de configuración
    print("\n2. Accediendo a la página de configuración...")
    response = client.get('/administration/system-config/')
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Página de configuración cargada correctamente")
        print("Contenido incluye 'Gestión de Grados':", 'Gestión de Grados' in response.content.decode())
    else:
        print(f"❌ Error al cargar página: {response.status_code}")
    
    # Probar API de grados con sesión
    print("\n3. Probando API de grados con sesión...")
    response = client.get('/academic-system/api/grades/')
    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.get('Content-Type', 'No definido')}")
    
    if response.status_code == 200:
        try:
            import json
            data = json.loads(response.content.decode())
            print("✅ API responde correctamente con JSON")
            print(f"Número de grados: {data.get('count', 0)}")
            print(f"Estado: {data.get('status', 'desconocido')}")
        except json.JSONDecodeError:
            print("❌ La respuesta no es JSON válido")
    else:
        print(f"❌ Error en API: {response.status_code}")
    
    # Probar creación de grado
    print("\n4. Probando creación de nuevo grado...")
    test_data = {
        'name': '12° Bachillerato',
        'level': 'bachillerato',
        'order': 12
    }
    
    response = client.post('/academic-system/api/grades/create/', test_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        try:
            import json
            data = json.loads(response.content.decode())
            print("✅ Creación exitosa")
            print(f"Respuesta: {data}")
        except json.JSONDecodeError:
            print("❌ La respuesta no es JSON válido")
    else:
        print(f"❌ Error en creación: {response.status_code}")
        print(f"Contenido: {response.content.decode()[:200]}")

if __name__ == '__main__':
    test_grade_functionality()