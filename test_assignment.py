#!/usr/bin/env python3
"""
Script para probar la asignación de profesores a cursos
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')
django.setup()

from django.contrib.auth.models import User
from academics_extended.models import Course, AcademicYear

def test_assignment():
    print("=== TESTING TEACHER-COURSE ASSIGNMENT ===")
    
    # Obtener año académico actual
    current_year = AcademicYear.objects.filter(is_current=True).first()
    print(f"Año académico actual: {current_year}")
    
    # Obtener algunos cursos
    courses = Course.objects.filter(academic_year=current_year)[:5]
    print(f"\nCursos disponibles ({courses.count()}):")
    for course in courses:
        print(f"  - ID: {course.id} | {course.grade.name} {course.section} | Director actual: {course.homeroom_teacher}")
    
    # Obtener algunos profesores
    teachers = User.objects.filter(is_active=True, profile__role='teacher')[:5]
    print(f"\nProfesores disponibles ({teachers.count()}):")
    for teacher in teachers:
        current_courses = Course.objects.filter(homeroom_teacher=teacher).count()
        print(f"  - ID: {teacher.id} | {teacher.get_full_name()} | Cursos asignados: {current_courses}")
    
    if courses.exists() and teachers.exists():
        course = courses.first()
        teacher = teachers.first()
        
        print(f"\n=== PRUEBA DE ASIGNACIÓN ===")
        print(f"Asignando profesor {teacher.get_full_name()} (ID: {teacher.id})")
        print(f"Al curso {course.grade.name} {course.section} (ID: {course.id})")
        
        # Hacer la asignación
        course.homeroom_teacher = teacher
        course.save()
        
        print("✅ Asignación exitosa!")
        print(f"Verificación: {course.grade.name} {course.section} -> Director: {course.homeroom_teacher}")
    else:
        print("❌ No hay suficientes cursos o profesores para la prueba")

if __name__ == "__main__":
    test_assignment()