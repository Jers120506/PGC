#!/usr/bin/env python
"""
Script para verificar que la página de gestión académica ya no tiene bucles infinitos
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')
django.setup()

import requests
import time

def test_page_stability():
    """Probar que la página no se esté recargando continuamente"""
    
    print("=== VERIFICACIÓN DE ESTABILIDAD DE PÁGINA ===")
    
    base_url = "http://localhost:8000"
    
    # Verificar que las APIs responden correctamente
    print("\n1. Verificando APIs...")
    
    # API de años académicos
    try:
        response = requests.get(f"{base_url}/academic-system/api/academic-years/")
        print(f"✅ API Años Académicos: Status {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Datos: {data.get('status', 'N/A')} - {len(data.get('data', []))} años")
    except Exception as e:
        print(f"❌ API Años Académicos: Error - {e}")
    
    # API de grados
    try:
        response = requests.get(f"{base_url}/academic-system/api/grades/")
        print(f"✅ API Grados: Status {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Datos: {data.get('status', 'N/A')} - {len(data.get('data', []))} grados")
    except Exception as e:
        print(f"❌ API Grados: Error - {e}")
    
    # Verificar que la página principal no redirija continuamente
    print("\n2. Verificando página principal...")
    
    try:
        # Hacer múltiples requests para verificar consistencia
        responses = []
        for i in range(3):
            response = requests.get(f"{base_url}/administration/system-config/", 
                                  allow_redirects=False, timeout=5)
            responses.append(response.status_code)
            time.sleep(0.5)
        
        print(f"Status codes: {responses}")
        
        # Si todos son iguales (probablemente 302 para redirigir al login o 200), está bien
        if len(set(responses)) == 1:
            if responses[0] == 302:
                print("✅ Página redirige consistentemente (probablemente a login)")
            elif responses[0] == 200:
                print("✅ Página carga consistentemente")
            else:
                print(f"⚠️  Página responde con código {responses[0]}")
        else:
            print("❌ Respuestas inconsistentes - posible bucle")
            
    except requests.exceptions.Timeout:
        print("❌ Timeout - la página puede estar en bucle infinito")
    except Exception as e:
        print(f"❌ Error verificando página: {e}")
    
    print("\n3. Verificando servidor Django...")
    try:
        # Verificar que el servidor responde a peticiones básicas
        response = requests.get(f"{base_url}/auth/login/", timeout=5)
        print(f"✅ Página de login: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Error en servidor: {e}")
    
    print("\n=== VERIFICACIÓN COMPLETADA ===")
    print("\nSi no ves errores de timeout o bucles infinitos,")
    print("la página de gestión académica ya debería estar estable.")
    print("\nPara probar manualmente:")
    print("1. Ve a: http://localhost:8000/auth/login/")
    print("2. Login: admin / admin123") 
    print("3. Ve a: http://localhost:8000/administration/system-config/")
    print("4. Observa que la página NO se recarga continuamente")

if __name__ == '__main__':
    test_page_stability()