#!/usr/bin/env python
"""
Script para limpiar duplicados y mantener estructura limpia
"""
import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')
django.setup()

from academics_extended.models import Course, Grade, AcademicYear

def clean_duplicates():
    """Limpiar cursos duplicados y mantener estructura correcta"""
    print("🧹 Limpiando duplicados y normalizando estructura...")
    
    # Obtener año académico actual
    current_year = AcademicYear.objects.filter(is_current=True).first()
    
    # Eliminar TODOS los cursos existentes para empezar limpio
    all_courses = Course.objects.all()
    deleted_count = all_courses.count()
    all_courses.delete()
    print(f"✅ Eliminados {deleted_count} cursos existentes")
    
    # Obtener todos los grados ordenados
    grades = Grade.objects.all().order_by('order')
    
    # Crear cursos limpios solo con secciones A y B
    sections = ['A', 'B']
    created_courses = []
    
    for grade in grades:
        for section in sections:
            course = Course.objects.create(
                grade=grade,
                section=section,
                academic_year=current_year,
                max_students=35
            )
            created_courses.append(course)
            print(f"✅ Curso creado: {course.grade.name} - Sección {course.section}")
    
    print(f"\n📊 Estructura final:")
    print(f"   • Total de grados: {grades.count()}")
    print(f"   • Total de cursos: {len(created_courses)}")
    print(f"   • Secciones por grado: A, B")
    
    # Mostrar estructura por grado
    print(f"\n📋 Cursos por grado:")
    for grade in grades:
        grade_courses = Course.objects.filter(grade=grade).order_by('section')
        sections_list = [course.section for course in grade_courses]
        print(f"   • {grade.name}: Secciones {', '.join(sections_list)}")
    
    return created_courses

if __name__ == '__main__':
    try:
        courses = clean_duplicates()
        print(f"\n🎉 ¡Estructura limpia completada!")
        print(f"   Total: {len(courses)} cursos (solo secciones A y B)")
        
    except Exception as e:
        print(f"❌ Error durante la limpieza: {e}")
        import traceback
        traceback.print_exc()