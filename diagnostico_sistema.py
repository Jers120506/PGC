#!/usr/bin/env python3
"""
Script de diagnóstico para verificar el estado del sistema de cursos
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8080"

def test_courses_api():
    """Prueba la API de cursos"""
    print("🔧 Probando API de cursos...")
    
    try:
        response = requests.get(f"{BASE_URL}/academics_extended/api/courses/")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                courses = data.get('courses', [])
                print(f"✅ API de cursos funciona - {len(courses)} cursos encontrados")
                
                if courses:
                    print("📋 Algunos cursos:")
                    for i, course in enumerate(courses[:3]):
                        print(f"   {i+1}. {course['grade_name']} - {course['section']} ({course['academic_year_name']})")
                return True
            else:
                print(f"❌ Error en API: {data.get('message')}")
                return False
        else:
            print(f"❌ Error HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_grades_api():
    """Prueba la API de grados"""
    print("🔧 Probando API de grados...")
    
    try:
        response = requests.get(f"{BASE_URL}/academics_extended/api/grades/")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                grades = data.get('grades', [])
                print(f"✅ API de grados funciona - {len(grades)} grados encontrados")
                return True
            else:
                print(f"❌ Error en API: {data.get('message')}")
                return False
        else:
            print(f"❌ Error HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_subjects_api():
    """Prueba la API de materias"""
    print("🔧 Probando API de materias...")
    
    try:
        response = requests.get(f"{BASE_URL}/academics_extended/api/subjects/")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                subjects = data.get('subjects', [])
                print(f"✅ API de materias funciona - {len(subjects)} materias encontradas")
                return True
            else:
                print(f"❌ Error en API: {data.get('message')}")
                return False
        else:
            print(f"❌ Error HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_academic_years_api():
    """Prueba la API de años académicos"""
    print("🔧 Probando API de años académicos...")
    
    try:
        response = requests.get(f"{BASE_URL}/academics_extended/api/academic-years/")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                years = data.get('academic_years', [])
                print(f"✅ API de años académicos funciona - {len(years)} años encontrados")
                return True
            else:
                print(f"❌ Error en API: {data.get('message')}")
                return False
        else:
            print(f"❌ Error HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

if __name__ == '__main__':
    print("=" * 50)
    print("🏫 DIAGNÓSTICO DEL SISTEMA ACADÉMICO")
    print("=" * 50)
    
    # Verificar servidor
    try:
        response = requests.get(BASE_URL, timeout=5)
        print("✅ Servidor Django disponible")
    except:
        print("❌ Servidor Django no disponible")
        exit(1)
    
    # Probar todas las APIs
    results = {
        'academic_years': test_academic_years_api(),
        'grades': test_grades_api(),
        'subjects': test_subjects_api(),
        'courses': test_courses_api()
    }
    
    print("\n" + "=" * 50)
    print("📊 RESUMEN")
    print("=" * 50)
    
    for api, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} API {api}: {'OK' if status else 'ERROR'}")
    
    total = len(results)
    working = sum(results.values())
    print(f"\n🎯 {working}/{total} APIs funcionando correctamente")
    
    if working == total:
        print("🎉 ¡Todo el sistema está funcionando!")
    else:
        print("⚠️  Hay problemas que requieren atención")