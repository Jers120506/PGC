#!/usr/bin/env python3
"""
Script para probar las APIs de gestión de horarios académicos
"""

import requests
import json

# Configuración
BASE_URL = "http://127.0.0.1:8000/academic-system/api"

def test_schedule_resources():
    """Prueba la API de recursos para horarios"""
    print("=== Probando API de Recursos ===")
    
    try:
        response = requests.get(f"{BASE_URL}/schedules/resources/")
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Status: {data.get('status')}")
        
        if data.get('status') == 'success':
            resources = data.get('data', {})
            print(f"✅ Cursos disponibles: {len(resources.get('courses', []))}")
            print(f"✅ Profesores disponibles: {len(resources.get('teachers', []))}")
            print(f"✅ Salones disponibles: {len(resources.get('classrooms', []))}")
            print(f"✅ Materias disponibles: {len(resources.get('subjects', []))}")
            print(f"✅ Franjas horarias: {len(resources.get('time_slots', []))}")
            
            # Mostrar algunos ejemplos
            if resources.get('courses'):
                print(f"Ejemplo de curso: {resources['courses'][0]['name']}")
            if resources.get('teachers'):
                print(f"Ejemplo de profesor: {resources['teachers'][0]['name']}")
            if resources.get('time_slots'):
                print(f"Ejemplo de horario: {resources['time_slots'][0]['name']} ({resources['time_slots'][0]['start_time']}-{resources['time_slots'][0]['end_time']})")
        else:
            print(f"❌ Error: {data.get('message')}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

def test_schedules_list():
    """Prueba la API de listado de horarios"""
    print("\n=== Probando API de Listado de Horarios ===")
    
    try:
        response = requests.get(f"{BASE_URL}/schedules/")
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Status: {data.get('status')}")
        
        if data.get('status') == 'success':
            schedules = data.get('data', [])
            print(f"✅ Horarios encontrados: {len(schedules)}")
            print(f"Total: {data.get('total', 0)}")
            
            if schedules:
                print("Ejemplo de horario:")
                schedule = schedules[0]
                print(f"  - {schedule['weekday_name']} {schedule['time_slot']['name']}")
                print(f"  - Curso: {schedule['course']['name']}")
                print(f"  - Materia: {schedule['subject']['name']}")
                print(f"  - Profesor: {schedule['teacher']['name']}")
                print(f"  - Salón: {schedule['classroom']['name']}")
            else:
                print("No hay horarios creados aún")
        else:
            print(f"❌ Error: {data.get('message')}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

def test_schedule_matrix():
    """Prueba la API de matriz de horarios"""
    print("\n=== Probando API de Matriz de Horarios ===")
    
    try:
        response = requests.get(f"{BASE_URL}/schedules/matrix/")
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Status: {data.get('status')}")
        
        if data.get('status') == 'success':
            matrix_data = data.get('data', {})
            print(f"✅ Año académico: {matrix_data.get('academic_year')}")
            print(f"✅ Total horarios: {matrix_data.get('total_schedules')}")
            print(f"✅ Días de la semana: {len(matrix_data.get('weekdays', []))}")
            print(f"✅ Franjas horarias: {len(matrix_data.get('matrix', []))}")
            
            # Mostrar estructura de la matriz
            matrix = matrix_data.get('matrix', [])
            if matrix:
                print("Estructura de la matriz:")
                for time_slot in matrix[:2]:  # Solo mostrar las primeras 2 franjas
                    slot_info = time_slot['time_slot']
                    print(f"  {slot_info['name']} ({slot_info['start_time']}-{slot_info['end_time']}):")
                    
                    for day_value, day_data in time_slot['days'].items():
                        schedules_count = len(day_data['schedules'])
                        if schedules_count > 0:
                            print(f"    {day_data['weekday_name']}: {schedules_count} horario(s)")
        else:
            print(f"❌ Error: {data.get('message')}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

def test_create_schedule():
    """Prueba la creación de un horario (requiere datos específicos)"""
    print("\n=== Probando Creación de Horario ===")
    
    # Primero obtener recursos disponibles
    try:
        response = requests.get(f"{BASE_URL}/schedules/resources/")
        resources_data = response.json()
        
        if resources_data.get('status') != 'success':
            print("❌ No se pudieron obtener recursos")
            return
            
        resources = resources_data.get('data', {})
        
        # Verificar que tenemos recursos suficientes
        courses = resources.get('courses', [])
        subjects = resources.get('subjects', [])
        teachers = resources.get('teachers', [])
        classrooms = resources.get('classrooms', [])
        time_slots = resources.get('time_slots', [])
        
        if not all([courses, subjects, teachers, classrooms, time_slots]):
            print("❌ No hay suficientes recursos para crear un horario")
            print(f"Cursos: {len(courses)}, Materias: {len(subjects)}, Profesores: {len(teachers)}")
            print(f"Salones: {len(classrooms)}, Horarios: {len(time_slots)}")
            return
        
        # Crear un horario de prueba
        test_schedule = {
            'course_id': courses[0]['id'],
            'subject_id': subjects[0]['id'],
            'teacher_id': teachers[0]['id'],
            'classroom_id': classrooms[0]['id'],
            'time_slot_id': time_slots[0]['id'],
            'weekday': 1,  # Lunes
            'notes': 'Horario de prueba creado automáticamente'
        }
        
        print(f"Intentando crear horario:")
        print(f"  Curso: {courses[0]['name']}")
        print(f"  Materia: {subjects[0]['name']}")
        print(f"  Profesor: {teachers[0]['name']}")
        print(f"  Salón: {classrooms[0]['name']}")
        print(f"  Horario: {time_slots[0]['name']}")
        print(f"  Día: Lunes")
        
        response = requests.post(
            f"{BASE_URL}/schedules/create/",
            json=test_schedule,
            headers={'Content-Type': 'application/json'}
        )
        
        data = response.json()
        print(f"Status Code: {response.status_code}")
        print(f"Response Status: {data.get('status')}")
        
        if data.get('status') == 'success':
            print(f"✅ Horario creado exitosamente!")
            print(f"Mensaje: {data.get('message')}")
            if 'data' in data:
                print(f"ID del horario: {data['data'].get('id')}")
        else:
            print(f"❌ Error al crear horario: {data.get('message')}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de APIs de Gestión de Horarios")
    print("=" * 60)
    
    test_schedule_resources()
    test_schedules_list()
    test_schedule_matrix()
    test_create_schedule()
    
    print("\n" + "=" * 60)
    print("✅ Pruebas completadas")