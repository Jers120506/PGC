#!/usr/bin/env python3
"""
Script para probar las APIs de horarios después de corregir el middleware
"""

import requests
import json
from datetime import datetime

# Base URL del sistema
BASE_URL = "http://127.0.0.1:8000"
SCHEDULE_API_BASE = f"{BASE_URL}/academic-system/schedules"

def test_api_endpoint(url, description):
    """Prueba un endpoint de API específico"""
    print(f"\n{'='*50}")
    print(f"Probando: {description}")
    print(f"URL: {url}")
    print(f"{'='*50}")
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'No especificado')}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✓ Respuesta JSON válida")
                print(f"Claves principales: {list(data.keys()) if isinstance(data, dict) else 'Lista de elementos'}")
                
                if isinstance(data, dict) and 'status' in data:
                    print(f"Status: {data.get('status')}")
                    if data.get('status') == 'success' and 'data' in data:
                        inner_data = data['data']
                        if isinstance(inner_data, dict):
                            for key, value in inner_data.items():
                                if isinstance(value, list):
                                    print(f"  {key}: {len(value)} elementos")
                                else:
                                    print(f"  {key}: {value}")
                        elif isinstance(inner_data, list):
                            print(f"  Elementos en la lista: {len(inner_data)}")
                
                return True
            except json.JSONDecodeError:
                print(f"⚠ Respuesta no es JSON válido")
                print(f"Contenido: {response.text[:200]}...")
                return False
        else:
            print(f"✗ Error HTTP: {response.status_code}")
            print(f"Contenido: {response.text[:200]}...")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"✗ Error de conexión. ¿Está el servidor corriendo?")
        return False
    except Exception as e:
        print(f"✗ Error inesperado: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🔄 PRUEBAS DE APIs DE HORARIOS - POST MIDDLEWARE FIX")
    print(f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Lista de endpoints a probar
    endpoints = [
        (f"{SCHEDULE_API_BASE}/api/", "Lista de horarios"),
        (f"{SCHEDULE_API_BASE}/resources/", "Recursos del sistema"),
        (f"{SCHEDULE_API_BASE}/matrix/", "Matriz de horarios"),
    ]
    
    results = []
    
    for url, description in endpoints:
        success = test_api_endpoint(url, description)
        results.append((description, success))
    
    # Resumen final
    print(f"\n{'='*60}")
    print("📋 RESUMEN DE PRUEBAS")
    print(f"{'='*60}")
    
    successful = sum(1 for _, success in results if success)
    total = len(results)
    
    for description, success in results:
        status = "✓ EXITOSO" if success else "✗ FALLÓ"
        print(f"{description}: {status}")
    
    print(f"\nResultado general: {successful}/{total} pruebas exitosas")
    
    if successful == total:
        print("🎉 ¡Todas las APIs están funcionando correctamente!")
    else:
        print("⚠ Algunas APIs tienen problemas. Revisa los logs arriba.")

if __name__ == "__main__":
    main()