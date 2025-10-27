#!/usr/bin/env python3
"""
Script simple para probar las correcciones del sistema de estudiantes
"""

import json
from academics_extended.models import Student, Course
from django.test.client import Client

def test_apis():
    print("INICIANDO PRUEBAS DE APIS DE ESTUDIANTES")
    print("=" * 60)
    
    client = Client()
    
    # 1. Probar listado de estudiantes
    print("\n=== PROBANDO LISTADO DE ESTUDIANTES ===")
    
    response = client.get('/academic-system/api/students/')
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            if data.get('status') == 'success':
                students = data.get('data', [])
                print(f"EXITO: {len(students)} estudiantes encontrados")
                listado_ok = True
            else:
                print(f"ERROR en respuesta: {data.get('message')}")
                listado_ok = False
        except Exception as e:
            print(f"ERROR al parsear respuesta: {str(e)}")
            listado_ok = False
    else:
        print(f"ERROR HTTP: {response.status_code}")
        listado_ok = False
    
    # 2. Probar actualización de estudiante
    print("\n=== PROBANDO ACTUALIZACION DE ESTUDIANTE ===")
    
    student = Student.objects.first()
    if student:
        student_id = student.id
        print(f"Estudiante a editar: {student.user.get_full_name()} (ID: {student_id})")
        
        update_data = {
            'first_name': f"{student.user.first_name}_EDITADO",
            'last_name': f"{student.user.last_name}_EDITADO",
            'address': "Direccion actualizada de prueba"
        }
        
        response = client.put(
            f'/academic-system/api/students/{student_id}/',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('status') == 'success':
                    print("EXITO: Actualizacion exitosa")
                    student.refresh_from_db()
                    student.user.refresh_from_db()
                    print(f"Nombre actualizado: {student.user.get_full_name()}")
                    actualizacion_ok = True
                else:
                    print(f"ERROR en respuesta: {data.get('message')}")
                    actualizacion_ok = False
            except Exception as e:
                print(f"ERROR al parsear respuesta: {str(e)}")
                print(f"Response content: {response.content}")
                actualizacion_ok = False
        else:
            print(f"ERROR HTTP: {response.status_code}")
            print(f"Response content: {response.content}")
            actualizacion_ok = False
    else:
        print("ERROR: No hay estudiantes para probar")
        actualizacion_ok = False
    
    # 3. Probar inscripción de estudiante
    print("\n=== PROBANDO INSCRIPCION DE ESTUDIANTE ===")
    
    student = Student.objects.filter(course__isnull=True).first()
    if not student:
        student = Student.objects.first()
        
    course = Course.objects.filter(available_spots__gt=0).first()
    
    if student and course:
        print(f"Estudiante: {student.user.get_full_name()} (ID: {student.id})")
        print(f"Curso: {course} (ID: {course.id})")
        
        enrollment_data = {
            'student_id': student.id,
            'course_id': course.id,
            'notes': 'Inscripcion de prueba'
        }
        
        response = client.post(
            '/academic-system/api/enrollments/enroll/',
            data=json.dumps(enrollment_data),
            content_type='application/json'
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('status') == 'success':
                    print("EXITO: Inscripcion exitosa")
                    student.refresh_from_db()
                    if student.course:
                        print(f"Estudiante inscrito en: {student.course}")
                        inscripcion_ok = True
                    else:
                        print("ERROR: Inscripcion no se reflejo en la base de datos")
                        inscripcion_ok = False
                else:
                    print(f"ERROR en respuesta: {data.get('message')}")
                    inscripcion_ok = False
            except Exception as e:
                print(f"ERROR al parsear respuesta: {str(e)}")
                print(f"Response content: {response.content}")
                inscripcion_ok = False
        else:
            print(f"ERROR HTTP: {response.status_code}")
            print(f"Response content: {response.content}")
            inscripcion_ok = False
    else:
        print("ERROR: No hay estudiantes o cursos disponibles para probar")
        inscripcion_ok = False
    
    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE PRUEBAS:")
    print("=" * 60)
    
    tests = [
        ("Listado de estudiantes", listado_ok),
        ("Actualizacion de estudiante", actualizacion_ok),
        ("Inscripcion de estudiante", inscripcion_ok)
    ]
    
    for test_name, success in tests:
        status = "EXITO" if success else "FALLO"
        print(f"{test_name:<30} {status}")
    
    successful_tests = sum(1 for _, success in tests if success)
    total_tests = len(tests)
    
    print(f"\nRESULTADO FINAL: {successful_tests}/{total_tests} pruebas exitosas")
    
    if successful_tests == total_tests:
        print("TODAS LAS PRUEBAS PASARON! El sistema esta funcionando correctamente.")
    else:
        print("ALGUNAS PRUEBAS FALLARON. Revisar logs anteriores.")

if __name__ == "__main__":
    test_apis()