#!/usr/bin/env python3
"""
Script para probar las APIs de estudiantes y verificar las correcciones realizadas
"""

import os
import sys
import django
import requests
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')
sys.path.append('.')
django.setup()

from academics_extended.models import Student, Course, User
from django.contrib.auth.models import User

BASE_URL = 'http://127.0.0.1:8000'

def get_csrf_token():
    """Obtener token CSRF desde Django"""
    from django.middleware.csrf import get_token
    from django.http import HttpRequest
    request = HttpRequest()
    return get_token(request)

def test_student_update():
    """Probar actualización de estudiante via API PUT"""
    print("\n=== PROBANDO ACTUALIZACIÓN DE ESTUDIANTE ===")
    
    # Buscar un estudiante existente
    try:
        student = Student.objects.first()
        if not student:
            print("❌ No hay estudiantes para probar")
            return False
            
        student_id = student.id
        print(f"📝 Estudiante a editar: {student.user.get_full_name()} (ID: {student_id})")
        
        # Datos de prueba para actualizar
        update_data = {
            'first_name': f"{student.user.first_name}_EDITADO",
            'last_name': f"{student.user.last_name}_EDITADO",
            'student_id': f"{student.student_id}_EDIT",
            'address': "Dirección actualizada de prueba",
            'guardian_name': "Acudiente actualizado",
            'guardian_phone': "555-0199"
        }
        
        # Hacer petición PUT
        url = f"{BASE_URL}/academic-system/api/students/{student_id}/"
        headers = {
            'Content-Type': 'application/json',
            'X-CSRFToken': get_csrf_token()
        }
        
        response = requests.put(url, 
                              headers=headers, 
                              data=json.dumps(update_data))
        
        print(f"🌐 URL: {url}")
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                print("✅ Actualización exitosa")
                
                # Verificar cambios en la base de datos
                student.refresh_from_db()
                student.user.refresh_from_db()
                print(f"✅ Nombre actualizado: {student.user.get_full_name()}")
                print(f"✅ Student ID actualizado: {student.student_id}")
                
                return True
            else:
                print(f"❌ Error en respuesta: {result.get('message')}")
                return False
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error en test_student_update: {str(e)}")
        return False

def test_student_enrollment():
    """Probar inscripción de estudiante via API"""
    print("\n=== PROBANDO INSCRIPCIÓN DE ESTUDIANTE ===")
    
    try:
        # Buscar estudiante sin curso asignado
        student = Student.objects.filter(course__isnull=True).first()
        if not student:
            # Si no hay estudiantes sin curso, usar cualquier estudiante
            student = Student.objects.first()
            
        if not student:
            print("❌ No hay estudiantes para probar inscripción")
            return False
            
        # Buscar un curso disponible
        course = Course.objects.filter(available_spots__gt=0).first()
        if not course:
            print("❌ No hay cursos disponibles para inscripción")
            return False
            
        print(f"📝 Estudiante: {student.user.get_full_name()} (ID: {student.id})")
        print(f"📚 Curso: {course} (ID: {course.id})")
        print(f"👥 Cupos disponibles: {course.available_spots}")
        
        # Datos para inscripción
        enrollment_data = {
            'student_id': student.id,
            'course_id': course.id,
            'notes': 'Inscripción de prueba via API'
        }
        
        # Hacer petición POST
        url = f"{BASE_URL}/academic-system/api/enrollments/enroll/"
        headers = {
            'Content-Type': 'application/json',
            'X-CSRFToken': get_csrf_token()
        }
        
        response = requests.post(url, 
                               headers=headers, 
                               data=json.dumps(enrollment_data))
        
        print(f"🌐 URL: {url}")
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                print("✅ Inscripción exitosa")
                
                # Verificar inscripción en la base de datos
                student.refresh_from_db()
                if student.course:
                    print(f"✅ Estudiante inscrito en: {student.course}")
                    return True
                else:
                    print("❌ Inscripción no se reflejó en la base de datos")
                    return False
            else:
                print(f"❌ Error en respuesta: {result.get('message')}")
                return False
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error en test_student_enrollment: {str(e)}")
        return False

def test_students_list():
    """Probar listado de estudiantes via API"""
    print("\n=== PROBANDO LISTADO DE ESTUDIANTES ===")
    
    try:
        url = f"{BASE_URL}/academic-system/api/students/"
        response = requests.get(url)
        
        print(f"🌐 URL: {url}")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                students = result.get('data', [])
                print(f"✅ Listado exitoso: {len(students)} estudiantes encontrados")
                
                # Mostrar algunos estudiantes
                for i, student in enumerate(students[:3]):
                    print(f"   {i+1}. {student.get('first_name')} {student.get('last_name')} - {student.get('student_id')}")
                
                return True
            else:
                print(f"❌ Error en respuesta: {result.get('message')}")
                return False
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error en test_students_list: {str(e)}")
        return False

def main():
    """Función principal para ejecutar todas las pruebas"""
    print("🔧 INICIANDO PRUEBAS DE APIS DE ESTUDIANTES")
    print("=" * 60)
    
    results = []
    
    # Probar listado
    results.append(("Listado de estudiantes", test_students_list()))
    
    # Probar actualización
    results.append(("Actualización de estudiante", test_student_update()))
    
    # Probar inscripción
    results.append(("Inscripción de estudiante", test_student_enrollment()))
    
    # Resumen de resultados
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS:")
    print("=" * 60)
    
    for test_name, success in results:
        status = "✅ ÉXITO" if success else "❌ FALLO"
        print(f"{test_name:<30} {status}")
    
    successful_tests = sum(1 for _, success in results if success)
    total_tests = len(results)
    
    print(f"\n🎯 RESULTADO FINAL: {successful_tests}/{total_tests} pruebas exitosas")
    
    if successful_tests == total_tests:
        print("🎉 ¡Todas las pruebas pasaron! El sistema está funcionando correctamente.")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisar logs anteriores.")

if __name__ == "__main__":
    main()