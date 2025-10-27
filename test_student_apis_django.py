#!/usr/bin/env python3
"""
Script para probar las correcciones del sistema de estudiantes
usando el shell de Django directamente
"""

import json
from academics_extended.models import Student, Course
from django.test.client import Client
from django.contrib.auth.models import User
from django.middleware.csrf import get_token
from django.http import HttpRequest

def test_apis():
    """Probar todas las APIs con el cliente de Django"""
    
    print("🔧 INICIANDO PRUEBAS DE APIS DE ESTUDIANTES")
    print("=" * 60)
    
    # Crear cliente de prueba
    client = Client()
    
    # 1. Probar listado de estudiantes
    print("\n=== PROBANDO LISTADO DE ESTUDIANTES ===")
    
    response = client.get('/academic-system/api/students/')
    print(f"📊 Status Code: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            if data.get('status') == 'success':
                students = data.get('data', [])
                print(f"✅ Listado exitoso: {len(students)} estudiantes encontrados")
                
                for i, student in enumerate(students[:3]):
                    print(f"   {i+1}. {student.get('first_name')} {student.get('last_name')} - {student.get('student_id')}")
                    
                listado_ok = True
            else:
                print(f"❌ Error en respuesta: {data.get('message')}")
                listado_ok = False
        except Exception as e:
            print(f"❌ Error al parsear respuesta: {str(e)}")
            listado_ok = False
    else:
        print(f"❌ Error HTTP: {response.status_code}")
        listado_ok = False
    
    # 2. Probar actualización de estudiante
    print("\n=== PROBANDO ACTUALIZACIÓN DE ESTUDIANTE ===")
    
    # Buscar un estudiante existente
    student = Student.objects.first()
    if student:
        student_id = student.id
        print(f"📝 Estudiante a editar: {student.user.get_full_name()} (ID: {student_id})")
        
        # Datos de prueba
        update_data = {
            'first_name': f"{student.user.first_name}_EDITADO",
            'last_name': f"{student.user.last_name}_EDITADO",
            'student_id': f"{student.student_id}_EDIT",
            'address': "Dirección actualizada de prueba",
            'guardian_name': "Acudiente actualizado",
            'guardian_phone': "555-0199"
        }
        
        # Probar método PUT
        response = client.put(
            f'/academic-system/api/students/{student_id}/',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('status') == 'success':
                    print("✅ Actualización exitosa")
                    
                    # Verificar cambios
                    student.refresh_from_db()
                    student.user.refresh_from_db()
                    print(f"✅ Nombre actualizado: {student.user.get_full_name()}")
                    print(f"✅ Student ID actualizado: {student.student_id}")
                    
                    actualizacion_ok = True
                else:
                    print(f"❌ Error en respuesta: {data.get('message')}")
                    actualizacion_ok = False
            except Exception as e:
                print(f"❌ Error al parsear respuesta: {str(e)}")
                print(f"📄 Response content: {response.content}")
                actualizacion_ok = False
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"📄 Response content: {response.content}")
            actualizacion_ok = False
    else:
        print("❌ No hay estudiantes para probar")
        actualizacion_ok = False
    
    # 3. Probar inscripción de estudiante
    print("\n=== PROBANDO INSCRIPCIÓN DE ESTUDIANTE ===")
    
    # Buscar estudiante y curso
    student = Student.objects.filter(course__isnull=True).first()
    if not student:
        student = Student.objects.first()
        
    course = Course.objects.filter(available_spots__gt=0).first()
    
    if student and course:
        print(f"📝 Estudiante: {student.user.get_full_name()} (ID: {student.id})")
        print(f"📚 Curso: {course} (ID: {course.id})")
        
        enrollment_data = {
            'student_id': student.id,
            'course_id': course.id,
            'notes': 'Inscripción de prueba'
        }
        
        response = client.post(
            '/academic-system/api/enrollments/enroll/',
            data=json.dumps(enrollment_data),
            content_type='application/json'
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('status') == 'success':
                    print("✅ Inscripción exitosa")
                    
                    # Verificar inscripción
                    student.refresh_from_db()
                    if student.course:
                        print(f"✅ Estudiante inscrito en: {student.course}")
                        inscripcion_ok = True
                    else:
                        print("❌ Inscripción no se reflejó en la base de datos")
                        inscripcion_ok = False
                else:
                    print(f"❌ Error en respuesta: {data.get('message')}")
                    inscripcion_ok = False
            except Exception as e:
                print(f"❌ Error al parsear respuesta: {str(e)}")
                print(f"📄 Response content: {response.content}")
                inscripcion_ok = False
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"📄 Response content: {response.content}")
            inscripcion_ok = False
    else:
        print("❌ No hay estudiantes o cursos disponibles para probar")
        inscripcion_ok = False
    
    # Resumen de resultados
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS:")
    print("=" * 60)
    
    tests = [
        ("Listado de estudiantes", listado_ok),
        ("Actualización de estudiante", actualizacion_ok),
        ("Inscripción de estudiante", inscripcion_ok)
    ]
    
    for test_name, success in tests:
        status = "✅ ÉXITO" if success else "❌ FALLO"
        print(f"{test_name:<30} {status}")
    
    successful_tests = sum(1 for _, success in tests if success)
    total_tests = len(tests)
    
    print(f"\n🎯 RESULTADO FINAL: {successful_tests}/{total_tests} pruebas exitosas")
    
    if successful_tests == total_tests:
        print("🎉 ¡Todas las pruebas pasaron! El sistema está funcionando correctamente.")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisar logs anteriores.")

if __name__ == "__main__":
    test_apis()