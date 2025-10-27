#!/usr/bin/env python

import os
import sys
import django
import requests
import json

# Configurar Django
sys.path.append('C:\\Users\\jbang\\OneDrive\\Desktop\\gestion de proyectos')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')
django.setup()

def test_grade_apis():
    """Probar las APIs de grados directamente"""
    
    print("=== PROBANDO APIs DE GRADOS ===")
    
    base_url = 'http://localhost:8000/academic-system/api'
    
    try:
        # Probar API de listado
        print("1. Probando listado de grados...")
        response = requests.get(f'{base_url}/grades/', timeout=5)
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Respuesta JSON: {json.dumps(data, indent=2)}")
            except:
                print("No es JSON válido. Primeros 500 caracteres:")
                print(response.text[:500])
        else:
            print(f"Error: {response.status_code}")
            print(response.text[:200])
            
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: {e}")
    
    # Probar directamente con Django
    print("\n2. Probando directamente con Django ORM...")
    from academics_extended.models import Grade
    
    grades = Grade.objects.all()
    print(f"Grados en la base de datos: {grades.count()}")
    
    for grade in grades[:5]:  # Solo los primeros 5
        print(f"  - {grade.id}: {grade.name} ({grade.level}, orden: {grade.order})")

if __name__ == "__main__":
    test_grade_apis()