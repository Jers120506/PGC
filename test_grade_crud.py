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

from django.test import Client
from django.contrib.auth.models import User
from academics_extended.models import Grade

def test_grade_crud():
    """Probar CRUD de grados usando Django test client"""
    
    print("=== PROBANDO CRUD DE GRADOS CON DJANGO CLIENT ===")
    
    # Crear cliente de test
    client = Client()
    
    try:
        # 1. Probar listado de grados
        print("1. Probando listado de grados...")
        response = client.get('/academic-system/api/grades/')
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Grados encontrados: {len(data.get('data', []))}")
                print(f"Respuesta: {json.dumps(data, indent=2)}")
            except:
                print("No es JSON válido")
                print(f"Contenido: {response.content.decode()[:200]}")
        
        # 2. Probar creación de grado
        print("\n2. Probando creación de grado...")
        new_grade_data = {
            'name': 'TEST Grado',
            'level': 'primaria',
            'order': 99
        }
        
        response = client.post('/academic-system/api/grades/create/', 
                             data=json.dumps(new_grade_data),
                             content_type='application/json')
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Respuesta: {json.dumps(data, indent=2)}")
                
                if data.get('status') == 'success':
                    grade_id = data.get('data', {}).get('id')
                    print(f"Grado creado con ID: {grade_id}")
                    
                    # 3. Probar eliminación
                    if grade_id:
                        print(f"\n3. Probando eliminación del grado {grade_id}...")
                        response = client.post(f'/academic-system/api/grades/{grade_id}/delete/')
                        print(f"Status: {response.status_code}")
                        
                        if response.status_code == 200:
                            data = response.json()
                            print(f"Respuesta: {json.dumps(data, indent=2)}")
                        
            except Exception as e:
                print(f"Error procesando respuesta: {e}")
                print(f"Contenido: {response.content.decode()[:200]}")
        
    except Exception as e:
        print(f"Error en la prueba: {e}")
    
    print("\n=== VERIFICACIÓN DIRECTA DE LA BASE DE DATOS ===")
    grades = Grade.objects.all()
    print(f"Total de grados en DB: {grades.count()}")
    
    for grade in grades[:3]:
        print(f"  - {grade.id}: {grade.name} ({grade.level})")

if __name__ == "__main__":
    test_grade_crud()