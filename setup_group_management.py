#!/usr/bin/env python
"""
Script para crear datos básicos de grados, cursos y año académico
para el sistema de gestión de grupos
"""
import os
import sys
import django
from datetime import date

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')
django.setup()

from academics_extended.models import AcademicYear, Grade, Course
from django.contrib.auth.models import User

def create_academic_structure():
    """Crear estructura académica básica"""
    print("🎓 Creando estructura académica básica...")
    
    # 1. Crear año académico si no existe
    current_year, created = AcademicYear.objects.get_or_create(
        name="2025",
        defaults={
            'start_date': date(2025, 1, 1),
            'end_date': date(2025, 12, 31),
            'is_current': True
        }
    )
    
    if created:
        print(f"✅ Año académico creado: {current_year.name}")
    else:
        # Asegurar que sea el año actual
        current_year.is_current = True
        current_year.save()
        print(f"✅ Año académico actualizado: {current_year.name}")
    
    # 2. Crear grados escolares
    grades_data = [
        # Primaria
        {'name': '1° Primaria', 'level': 'primaria', 'order': 1},
        {'name': '2° Primaria', 'level': 'primaria', 'order': 2},
        {'name': '3° Primaria', 'level': 'primaria', 'order': 3},
        {'name': '4° Primaria', 'level': 'primaria', 'order': 4},
        {'name': '5° Primaria', 'level': 'primaria', 'order': 5},
        
        # Bachillerato
        {'name': '6° Bachillerato', 'level': 'bachillerato', 'order': 6},
        {'name': '7° Bachillerato', 'level': 'bachillerato', 'order': 7},
        {'name': '8° Bachillerato', 'level': 'bachillerato', 'order': 8},
        {'name': '9° Bachillerato', 'level': 'bachillerato', 'order': 9},
        {'name': '10° Bachillerato', 'level': 'bachillerato', 'order': 10},
        {'name': '11° Bachillerato', 'level': 'bachillerato', 'order': 11},
    ]
    
    created_grades = []
    for grade_data in grades_data:
        grade, created = Grade.objects.get_or_create(
            name=grade_data['name'],
            defaults={
                'level': grade_data['level'],
                'order': grade_data['order']
            }
        )
        created_grades.append(grade)
        if created:
            print(f"✅ Grado creado: {grade.name}")
    
    # 3. Crear cursos (secciones) para cada grado
    sections = ['A', 'B']  # Solo secciones A y B disponibles
    created_courses = []
    
    for grade in created_grades:
        for section in sections:
            course, created = Course.objects.get_or_create(
                grade=grade,
                section=section,
                academic_year=current_year,
                defaults={
                    'max_students': 35
                }
            )
            created_courses.append(course)
            if created:
                print(f"✅ Curso creado: {course.grade.name} - Sección {course.section}")
    
    # 4. Estadísticas finales
    print(f"\n📊 Estructura académica completada:")
    print(f"   • Año académico: {current_year.name}")
    print(f"   • Grados creados: {len(created_grades)}")
    print(f"   • Cursos creados: {len(created_courses)}")
    print(f"   • Profesores registrados: {User.objects.filter(profile__role='teacher').count()}")
    
    return current_year, created_grades, created_courses

def assign_sample_teachers():
    """Asignar algunos profesores como directores de grupo de muestra"""
    print("\n👨‍🏫 Asignando profesores como directores de grupo...")
    
    # Obtener algunos cursos sin director
    courses_without_teacher = Course.objects.filter(homeroom_teacher__isnull=True)[:5]
    
    # Obtener profesores disponibles
    available_teachers = User.objects.filter(
        profile__role='teacher',
        is_active=True
    )[:5]
    
    assignments = 0
    for course, teacher in zip(courses_without_teacher, available_teachers):
        course.homeroom_teacher = teacher
        course.save()
        assignments += 1
        print(f"✅ {teacher.get_full_name()} asignado como director de {course.grade.name} {course.section}")
    
    print(f"\n📋 Asignaciones completadas: {assignments}")

if __name__ == '__main__':
    try:
        print("🚀 Iniciando configuración de gestión de grupos...")
        
        # Crear estructura académica
        current_year, grades, courses = create_academic_structure()
        
        # Asignar profesores de muestra
        assign_sample_teachers()
        
        print(f"\n🎉 ¡Configuración completada exitosamente!")
        print(f"   Ahora puedes ir a: http://127.0.0.1:8000/administration/admin/groups/")
        
    except Exception as e:
        print(f"❌ Error durante la configuración: {e}")
        import traceback
        traceback.print_exc()