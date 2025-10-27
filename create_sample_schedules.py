#!/usr/bin/env python3
"""
Script para crear horarios de ejemplo en el sistema
"""

import requests
import json
import random

# Configuración
BASE_URL = "http://127.0.0.1:8000/academic-system/api"

def get_resources():
    """Obtener recursos disponibles"""
    response = requests.get(f"{BASE_URL}/schedules/resources/")
    data = response.json()
    
    if data.get('status') == 'success':
        return data.get('data', {})
    return None

def create_sample_schedules():
    """Crear horarios de ejemplo"""
    print("🏫 Creando horarios de ejemplo...")
    
    resources = get_resources()
    if not resources:
        print("❌ No se pudieron obtener recursos")
        return
    
    courses = resources.get('courses', [])
    subjects = resources.get('subjects', [])
    teachers = resources.get('teachers', [])
    classrooms = resources.get('classrooms', [])
    time_slots = resources.get('time_slots', [])
    
    # Filtrar solo franjas horarias académicas (excluir descanso)
    academic_slots = [slot for slot in time_slots if 'Descanso' not in slot['name']]
    
    print(f"📊 Recursos disponibles:")
    print(f"  • Cursos: {len(courses)}")
    print(f"  • Materias: {len(subjects)}")
    print(f"  • Profesores: {len(teachers)}")
    print(f"  • Salones: {len(classrooms)}")
    print(f"  • Franjas académicas: {len(academic_slots)}")
    
    # Crear algunos horarios específicos para diferentes cursos
    schedules_to_create = [
        # 1° Primaria - A
        {
            'course_name': '1° Primaria - A',
            'schedules': [
                {'subject': 'Matemáticas', 'day': 1, 'slot': '1ra Hora'},  # Lunes
                {'subject': 'Español', 'day': 1, 'slot': '2da Hora'},     # Lunes
                {'subject': 'Ciencias Naturales', 'day': 2, 'slot': '1ra Hora'},  # Martes
                {'subject': 'Educación Física', 'day': 3, 'slot': '1ra Hora'},    # Miércoles
                {'subject': 'Arte', 'day': 4, 'slot': '1ra Hora'},                # Jueves
            ]
        },
        # 2° Primaria - A
        {
            'course_name': '2° Primaria - A',
            'schedules': [
                {'subject': 'Matemáticas', 'day': 1, 'slot': '3ra Hora'},  # Lunes
                {'subject': 'Español', 'day': 2, 'slot': '2da Hora'},     # Martes
                {'subject': 'Historia', 'day': 3, 'slot': '2da Hora'},    # Miércoles
                {'subject': 'Música', 'day': 4, 'slot': '2da Hora'},      # Jueves
            ]
        },
        # 6° Bachillerato - A
        {
            'course_name': '6° Bachillerato - A',
            'schedules': [
                {'subject': 'Matemáticas', 'day': 1, 'slot': '4ta Hora'},  # Lunes
                {'subject': 'Física', 'day': 2, 'slot': '3ra Hora'},      # Martes
                {'subject': 'Química', 'day': 3, 'slot': '3ra Hora'},     # Miércoles
                {'subject': 'Literatura', 'day': 4, 'slot': '3ra Hora'},  # Jueves
                {'subject': 'Inglés', 'day': 5, 'slot': '1ra Hora'},      # Viernes
            ]
        }
    ]
    
    created_count = 0
    
    for course_data in schedules_to_create:
        # Buscar el curso
        course = next((c for c in courses if course_data['course_name'] in c['name']), None)
        if not course:
            print(f"⚠️  Curso no encontrado: {course_data['course_name']}")
            continue
        
        print(f"\n📚 Creando horarios para: {course['name']}")
        
        for schedule_info in course_data['schedules']:
            # Buscar materia
            subject = next((s for s in subjects if schedule_info['subject'] in s['name']), None)
            if not subject:
                print(f"  ⚠️  Materia no encontrada: {schedule_info['subject']}")
                continue
            
            # Buscar franja horaria
            time_slot = next((t for t in academic_slots if schedule_info['slot'] in t['name']), None)
            if not time_slot:
                print(f"  ⚠️  Franja horaria no encontrada: {schedule_info['slot']}")
                continue
            
            # Seleccionar profesor y salón aleatorio
            teacher = random.choice(teachers)
            classroom = random.choice(classrooms)
            
            # Crear horario
            schedule_data = {
                'course_id': course['id'],
                'subject_id': subject['id'],
                'teacher_id': teacher['id'],
                'classroom_id': classroom['id'],
                'time_slot_id': time_slot['id'],
                'weekday': schedule_info['day'],
                'notes': f'Horario de ejemplo - {course["name"]}'
            }
            
            try:
                response = requests.post(
                    f"{BASE_URL}/schedules/create/",
                    json=schedule_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                result = response.json()
                
                if result.get('status') == 'success':
                    day_names = {1: 'Lunes', 2: 'Martes', 3: 'Miércoles', 4: 'Jueves', 5: 'Viernes'}
                    print(f"  ✅ {day_names[schedule_info['day']]} {time_slot['name']}: {subject['name']} (Prof: {teacher['name'][:20]}...)")
                    created_count += 1
                else:
                    print(f"  ❌ Error: {result.get('message', 'Error desconocido')}")
                    
            except Exception as e:
                print(f"  ❌ Error de conexión: {e}")
    
    print(f"\n🎉 Creación completada!")
    print(f"✅ Total de horarios creados: {created_count}")

def show_current_schedules():
    """Mostrar horarios actuales"""
    print("\n📅 Horarios actuales en el sistema:")
    
    try:
        response = requests.get(f"{BASE_URL}/schedules/")
        data = response.json()
        
        if data.get('status') == 'success':
            schedules = data.get('data', [])
            print(f"Total: {len(schedules)} horarios")
            
            if schedules:
                print("\nDetalle de horarios:")
                for schedule in schedules:
                    print(f"  • {schedule['weekday_name']} {schedule['time_slot']['name']}: "
                          f"{schedule['course']['name']} - {schedule['subject']['name']} "
                          f"(Prof: {schedule['teacher']['name']}, Salón: {schedule['classroom']['name']})")
            else:
                print("No hay horarios registrados")
        else:
            print(f"❌ Error: {data.get('message')}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    print("🚀 Configurando Sistema de Horarios con Datos de Ejemplo")
    print("=" * 70)
    
    create_sample_schedules()
    show_current_schedules()
    
    print("\n" + "=" * 70)
    print("✨ Sistema de horarios configurado exitosamente!")
    print("💡 Puede ver los horarios en:")
    print("   - Lista: GET /academic-system/api/schedules/")
    print("   - Matriz: GET /academic-system/api/schedules/matrix/")