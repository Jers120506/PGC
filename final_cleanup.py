#!/usr/bin/env python
"""
Script para limpiar grados duplicados y crear estructura final correcta
"""
import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')
django.setup()

from academics_extended.models import Course, Grade, AcademicYear

def final_cleanup():
    """Limpieza final para tener estructura correcta"""
    print("🧹 Limpieza final de grados y cursos...")
    
    # Obtener año académico actual
    current_year = AcademicYear.objects.filter(is_current=True).first()
    
    # Eliminar TODOS los cursos y grados existentes
    Course.objects.all().delete()
    Grade.objects.all().delete()
    print("✅ Eliminados todos los cursos y grados existentes")
    
    # Crear grados limpios y correctos
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
    
    # Crear grados
    created_grades = []
    for grade_data in grades_data:
        grade = Grade.objects.create(
            name=grade_data['name'],
            level=grade_data['level'],
            order=grade_data['order']
        )
        created_grades.append(grade)
        print(f"✅ Grado creado: {grade.name}")
    
    # Crear cursos solo con secciones A y B
    sections = ['A', 'B']
    created_courses = []
    
    for grade in created_grades:
        for section in sections:
            course = Course.objects.create(
                grade=grade,
                section=section,
                academic_year=current_year,
                max_students=35
            )
            created_courses.append(course)
            print(f"✅ Curso creado: {course.grade.name} - Sección {course.section}")
    
    print(f"\n📊 Estructura final correcta:")
    print(f"   • Total de grados: {len(created_grades)}")
    print(f"   • Total de cursos: {len(created_courses)} (solo secciones A y B)")
    
    # Asignar algunos profesores como directores de grupo
    from django.contrib.auth.models import User
    available_teachers = User.objects.filter(
        profile__role='teacher',
        is_active=True
    )[:5]
    
    assignments = 0
    for i, course in enumerate(created_courses[:5]):
        if i < len(available_teachers):
            course.homeroom_teacher = available_teachers[i]
            course.save()
            assignments += 1
            print(f"✅ {available_teachers[i].get_full_name()} asignado como director de {course.grade.name} {course.section}")
    
    print(f"\n📋 Resumen final:")
    print(f"   • Grados: {len(created_grades)} (Primaria: 5, Bachillerato: 6)")
    print(f"   • Cursos: {len(created_courses)} (2 secciones por grado)")
    print(f"   • Directores asignados: {assignments}")
    
    return created_grades, created_courses

if __name__ == '__main__':
    try:
        grades, courses = final_cleanup()
        print(f"\n🎉 ¡Estructura final completada!")
        print(f"   Ahora la página mostrará solo secciones A y B")
        
    except Exception as e:
        print(f"❌ Error durante la limpieza final: {e}")
        import traceback
        traceback.print_exc()