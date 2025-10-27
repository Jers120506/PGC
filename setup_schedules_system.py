#!/usr/bin/env python3
"""
Script para crear datos básicos del sistema de horarios:
- Franjas horarias estándar
- Salones básicos
- Algunas asignaciones de profesor-materia
"""

import os
import sys
import django
from datetime import time

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')
sys.path.append('.')
django.setup()

from academics_extended.models import (
    TimeSlot, Classroom, AcademicYear, Subject, Course, 
    TeacherSubjectAssignment, Schedule
)
from authentication.models import User

def create_time_slots():
    """Crear franjas horarias estándar para jornada única"""
    print("📅 CREANDO FRANJAS HORARIAS...")
    
    time_slots_data = [
        ('1ª Hora', time(7, 0), time(7, 50), 1),
        ('2ª Hora', time(7, 50), time(8, 40), 2),
        ('3ª Hora', time(8, 40), time(9, 30), 3),
        ('Descanso', time(9, 30), time(9, 50), 4),
        ('4ª Hora', time(9, 50), time(10, 40), 5),
        ('5ª Hora', time(10, 40), time(11, 30), 6),
        ('6ª Hora', time(11, 30), time(12, 20), 7),
    ]
    
    created_count = 0
    for name, start_time, end_time, order in time_slots_data:
        time_slot, created = TimeSlot.objects.get_or_create(
            name=name,
            defaults={
                'start_time': start_time,
                'end_time': end_time,
                'order': order,
                'is_active': True
            }
        )
        if created:
            print(f"✅ Franja creada: {time_slot}")
            created_count += 1
        else:
            print(f"⚠️  Franja ya existe: {time_slot}")
    
    print(f"📊 Total franjas creadas: {created_count}")
    return created_count

def create_classrooms():
    """Crear salones básicos"""
    print("\n🏫 CREANDO SALONES...")
    
    classrooms_data = [
        # Primaria
        ('Salón 1A', 'SAL-1A', 30, 'Edificio A', '1er Piso'),
        ('Salón 1B', 'SAL-1B', 30, 'Edificio A', '1er Piso'),
        ('Salón 2A', 'SAL-2A', 30, 'Edificio A', '1er Piso'),
        ('Salón 2B', 'SAL-2B', 30, 'Edificio A', '1er Piso'),
        ('Salón 3A', 'SAL-3A', 30, 'Edificio A', '2do Piso'),
        ('Salón 3B', 'SAL-3B', 30, 'Edificio A', '2do Piso'),
        
        # Bachillerato
        ('Salón 4A', 'SAL-4A', 35, 'Edificio B', '1er Piso'),
        ('Salón 4B', 'SAL-4B', 35, 'Edificio B', '1er Piso'),
        ('Salón 5A', 'SAL-5A', 35, 'Edificio B', '2do Piso'),
        ('Salón 5B', 'SAL-5B', 35, 'Edificio B', '2do Piso'),
        
        # Salones especiales
        ('Lab. Ciencias', 'LAB-CIE', 25, 'Edificio C', '1er Piso'),
        ('Lab. Informática', 'LAB-INF', 25, 'Edificio C', '1er Piso'),
        ('Salón de Arte', 'SAL-ART', 20, 'Edificio C', '2do Piso'),
        ('Biblioteca', 'BIBLIO', 40, 'Edificio Principal', '1er Piso'),
        ('Auditorio', 'AUDIT', 100, 'Edificio Principal', '2do Piso'),
    ]
    
    created_count = 0
    for name, code, capacity, building, floor in classrooms_data:
        classroom, created = Classroom.objects.get_or_create(
            code=code,
            defaults={
                'name': name,
                'capacity': capacity,
                'building': building,
                'floor': floor,
                'is_active': True
            }
        )
        if created:
            print(f"✅ Salón creado: {classroom}")
            created_count += 1
        else:
            print(f"⚠️  Salón ya existe: {classroom}")
    
    print(f"📊 Total salones creados: {created_count}")
    return created_count

def create_sample_teacher_assignments():
    """Crear algunas asignaciones de profesores para poder hacer horarios"""
    print("\n👨‍🏫 CREANDO ASIGNACIONES DE PROFESORES...")
    
    current_year = AcademicYear.objects.filter(is_current=True).first()
    if not current_year:
        print("❌ No hay año académico actual configurado")
        return 0
    
    # Obtener algunos profesores
    teachers = User.objects.filter(profile__role='teacher', is_active=True)[:5]
    if not teachers:
        print("❌ No hay profesores disponibles")
        return 0
    
    # Obtener algunas materias
    subjects = Subject.objects.all()[:6]  # Primeras 6 materias
    courses = Course.objects.all()[:6]    # Primeros 6 cursos
    
    if not subjects or not courses:
        print("❌ No hay materias o cursos disponibles")
        return 0
    
    created_count = 0
    
    # Crear asignaciones de ejemplo
    for i, teacher in enumerate(teachers):
        # Cada profesor tendrá 1-2 materias
        teacher_subjects = subjects[i:i+2] if i+2 <= len(subjects) else subjects[i:i+1]
        
        for subject in teacher_subjects:
            # Asignar 2-3 cursos por materia
            assigned_courses = courses[i:i+3] if i+3 <= len(courses) else courses[i:]
            
            assignment, created = TeacherSubjectAssignment.objects.get_or_create(
                teacher=teacher,
                subject=subject,
                academic_year=current_year,
                defaults={
                    'is_main_teacher': i == 0,  # El primer profesor será principal
                }
            )
            
            if created:
                # Asignar cursos
                assignment.courses.set(assigned_courses)
                print(f"✅ Asignación creada: {teacher.get_full_name()} - {subject.name}")
                created_count += 1
            else:
                print(f"⚠️  Asignación ya existe: {teacher.get_full_name()} - {subject.name}")
    
    print(f"📊 Total asignaciones creadas: {created_count}")
    return created_count

def show_system_status():
    """Mostrar estado actual del sistema de horarios"""
    print("\n📊 ESTADO DEL SISTEMA DE HORARIOS")
    print("=" * 50)
    
    print(f"🕐 Franjas Horarias: {TimeSlot.objects.filter(is_active=True).count()}")
    print(f"🏫 Salones: {Classroom.objects.filter(is_active=True).count()}")
    print(f"👨‍🏫 Profesores: {User.objects.filter(profile__role='teacher', is_active=True).count()}")
    print(f"📚 Materias: {Subject.objects.count()}")
    print(f"🎓 Cursos: {Course.objects.filter(is_active=True).count()}")
    print(f"📋 Asignaciones P-M: {TeacherSubjectAssignment.objects.count()}")
    print(f"⏰ Horarios: {Schedule.objects.filter(is_active=True).count()}")
    
    print("\n🕐 Franjas Horarias Disponibles:")
    time_slots = TimeSlot.objects.filter(is_active=True).order_by('order')
    for slot in time_slots:
        print(f"   • {slot}")
    
    print("\n🏫 Salones Disponibles:")
    classrooms = Classroom.objects.filter(is_active=True)[:10]  # Primeros 10
    for classroom in classrooms:
        print(f"   • {classroom} - Capacidad: {classroom.capacity}")
    
    if Schedule.objects.exists():
        print("\n⏰ Horarios Creados:")
        schedules = Schedule.objects.filter(is_active=True)[:10]  # Primeros 10
        for schedule in schedules:
            print(f"   • {schedule}")

def main():
    """Función principal"""
    print("🚀 CONFIGURANDO SISTEMA DE HORARIOS ACADÉMICOS")
    print("=" * 60)
    
    # Crear datos básicos
    time_slots_created = create_time_slots()
    classrooms_created = create_classrooms()
    assignments_created = create_sample_teacher_assignments()
    
    # Mostrar estado
    show_system_status()
    
    print("\n" + "=" * 60)
    print("✅ CONFIGURACIÓN COMPLETADA")
    print(f"📊 Resumen: {time_slots_created} franjas, {classrooms_created} salones, {assignments_created} asignaciones")
    print("\n🎯 Siguiente paso: Crear horarios usando la interfaz web")
    print("   URL: http://127.0.0.1:8000/admin/config/ → Tab 'Horarios'")

if __name__ == "__main__":
    main()