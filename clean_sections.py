#!/usr/bin/env python
"""
Script para limpiar y ajustar los cursos a solo secciones A y B
"""
import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')
django.setup()

from academics_extended.models import Course

def clean_sections():
    """Eliminar cursos de sección C y mantener solo A y B"""
    print("🧹 Limpiando cursos - manteniendo solo secciones A y B...")
    
    # Eliminar todos los cursos de sección C
    section_c_courses = Course.objects.filter(section='C')
    deleted_count = section_c_courses.count()
    section_c_courses.delete()
    
    print(f"✅ Eliminados {deleted_count} cursos de sección C")
    
    # Mostrar estadísticas actuales
    remaining_courses = Course.objects.all().order_by('grade__order', 'section')
    print(f"📊 Cursos restantes: {remaining_courses.count()}")
    
    # Agrupar por grado
    courses_by_grade = {}
    for course in remaining_courses:
        grade_name = course.grade.name
        if grade_name not in courses_by_grade:
            courses_by_grade[grade_name] = []
        courses_by_grade[grade_name].append(course.section)
    
    print("\n📋 Estructura actual:")
    for grade, sections in courses_by_grade.items():
        print(f"   • {grade}: Secciones {', '.join(sections)}")
    
    return remaining_courses

if __name__ == '__main__':
    try:
        courses = clean_sections()
        print(f"\n🎉 ¡Limpieza completada! Ahora solo hay secciones A y B")
        
    except Exception as e:
        print(f"❌ Error durante la limpieza: {e}")
        import traceback
        traceback.print_exc()