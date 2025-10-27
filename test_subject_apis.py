#!/usr/bin/env python
"""
Script para probar las APIs de materias
"""
import os
import sys
import django
import requests
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')
django.setup()

def test_subject_apis():
    """Probar las APIs CRUD de materias"""
    
    print("=== PROBANDO APIs DE MATERIAS ===")
    
    base_url = "http://localhost:8000"
    
    # 1. Probar listado de materias
    print("\n1. Probando listado de materias...")
    try:
        response = requests.get(f"{base_url}/academic-system/api/subjects/", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'No definido')}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ Respuesta JSON válida")
                print(f"Estado: {data.get('status', 'N/A')}")
                print(f"Número de materias: {data.get('count', 0)}")
                
                # Mostrar algunas materias de ejemplo
                subjects = data.get('data', [])
                if subjects:
                    print("\nPrimeras 5 materias:")
                    for i, subject in enumerate(subjects[:5], 1):
                        print(f"  {i}. {subject['name']} ({subject['code']}) - {subject['area_display']} - {subject['hours_per_week']}h")
                
            except json.JSONDecodeError:
                print("❌ La respuesta no es JSON válido")
                print("Primeros 200 caracteres:", response.text[:200])
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print("Contenido:", response.text[:200])
            
    except requests.exceptions.Timeout:
        print("❌ Timeout - el servidor no responde")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 2. Probar creación de materia
    print("\n2. Probando creación de materia...")
    try:
        test_subject = {
            "name": "Materia de Prueba",
            "code": "TEST",
            "area": "informatica",
            "hours_per_week": 2,
            "description": "Materia creada para pruebas"
        }
        
        response = requests.post(
            f"{base_url}/academic-system/api/subjects/create/",
            json=test_subject,
            timeout=5,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ Creación exitosa")
                print(f"Respuesta: {data}")
                return data.get('data', {}).get('id')  # Retornar ID para prueba de eliminación
            except json.JSONDecodeError:
                print("❌ Respuesta no es JSON válido")
                print("Contenido:", response.text[:200])
        else:
            print(f"❌ Error en creación: {response.status_code}")
            print("Contenido:", response.text[:200])
            
    except Exception as e:
        print(f"❌ Error en creación: {e}")
    
    return None

    # 3. Probar eliminación (si se creó la materia)
    # Esta parte se implementará si la creación fue exitosa

def test_direct_database():
    """Probar acceso directo a la base de datos"""
    print("\n3. Probando acceso directo a la base de datos...")
    
    try:
        from academics_extended.models import Subject
        
        subjects = Subject.objects.all()
        print(f"Total materias en DB: {subjects.count()}")
        
        # Mostrar materias por área
        areas = {}
        for subject in subjects:
            area = subject.get_area_display()
            if area not in areas:
                areas[area] = 0
            areas[area] += 1
        
        print("\nMaterias por área:")
        for area, count in sorted(areas.items()):
            print(f"  - {area}: {count} materias")
        
        # Mostrar algunas materias
        print(f"\nPrimeras 5 materias:")
        for i, subject in enumerate(subjects[:5], 1):
            print(f"  {i}. {subject.name} ({subject.code}) - {subject.get_area_display()}")
            
    except Exception as e:
        print(f"❌ Error en acceso directo: {e}")

if __name__ == '__main__':
    test_subject_apis()
    test_direct_database()