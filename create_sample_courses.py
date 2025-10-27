#!/usr/bin/env python3
"""
Script para crear cursos de ejemplo en el sistema académico

Este script crea cursos para los grados existentes con diferentes secciones
y los asocia con el año académico actual.
"""

import os
import sys
import django

# Configurar el entorno de Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')
django.setup()

from academics_extended.models import AcademicYear, Grade, Course
from django.db import transaction

def crear_cursos_ejemplo():
    """Crea cursos de ejemplo para el sistema académico"""
    
    print("🎯 Iniciando creación de cursos de ejemplo...")
    
    # Verificar año académico actual
    try:
        current_year = AcademicYear.objects.filter(is_current=True).first()
        if not current_year:
            print("❌ No se encontró un año académico actual. Creando año 2024...")
            current_year = AcademicYear.objects.create(
                name="Año Académico 2024",
                start_date="2024-02-01",
                end_date="2024-11-30",
                is_current=True
            )
        print(f"✅ Año académico actual: {current_year.name}")
    except Exception as e:
        print(f"❌ Error al configurar año académico: {str(e)}")
        return
    
    # Obtener todos los grados
    try:
        grades = Grade.objects.all().order_by('order')
        print(f"✅ Encontrados {len(grades)} grados")
        
        if len(grades) == 0:
            print("❌ No hay grados configurados. Ejecute create_sample_grades.py primero")
            return
            
    except Exception as e:
        print(f"❌ Error al obtener grados: {str(e)}")
        return
    
    # Configuración de secciones por nivel
    sections_config = {
        # Primaria (grados 1-5): 2-3 secciones cada uno
        'primaria': ['A', 'B', 'C'],
        # Secundaria básica (grados 6-9): 2 secciones cada uno  
        'secundaria_basica': ['A', 'B'],
        # Secundaria media (grados 10-11): 1-2 secciones cada uno
        'secundaria_media': ['A', 'B']
    }
    
    cursos_creados = 0
    cursos_existentes = 0
    
    try:
        with transaction.atomic():
            for grade in grades:
                # Determinar qué secciones crear según el grado
                if grade.order <= 5:
                    # Primaria: más secciones para grados menores
                    if grade.order <= 3:
                        sections = sections_config['primaria']  # A, B, C
                    else:
                        sections = sections_config['primaria'][:2]  # A, B
                elif grade.order <= 9:
                    # Secundaria básica
                    sections = sections_config['secundaria_basica']  # A, B
                else:
                    # Secundaria media
                    if grade.order == 10:
                        sections = sections_config['secundaria_media']  # A, B
                    else:
                        sections = ['A']  # Solo una sección para grado 11
                
                # Crear cursos para cada sección
                for section in sections:
                    # Verificar si ya existe el curso
                    if Course.objects.filter(
                        grade=grade,
                        section=section,
                        academic_year=current_year
                    ).exists():
                        cursos_existentes += 1
                        print(f"⚠️  Curso {grade.name} - {section} ya existe")
                        continue
                    
                    # Determinar capacidad máxima según el grado
                    if grade.order <= 5:
                        max_students = 25  # Primaria: clases más pequeñas
                    elif grade.order <= 9:
                        max_students = 30  # Secundaria básica
                    else:
                        max_students = 35  # Secundaria media
                    
                    # Crear el curso
                    course = Course.objects.create(
                        grade=grade,
                        section=section,
                        academic_year=current_year,
                        max_students=max_students,
                        is_active=True
                    )
                    
                    cursos_creados += 1
                    print(f"✅ Creado: {course} (Capacidad: {max_students})")
        
        print(f"\n🎉 Proceso completado:")
        print(f"   - Cursos creados: {cursos_creados}")
        print(f"   - Cursos ya existentes: {cursos_existentes}")
        print(f"   - Total de cursos en sistema: {Course.objects.count()}")
        
        # Mostrar resumen por grado
        print(f"\n📊 Resumen por grado:")
        for grade in grades:
            course_count = Course.objects.filter(grade=grade, academic_year=current_year).count()
            courses = Course.objects.filter(grade=grade, academic_year=current_year)
            sections = [c.section for c in courses]
            print(f"   {grade.name}: {course_count} curso(s) - Secciones: {', '.join(sections)}")
        
    except Exception as e:
        print(f"❌ Error al crear cursos: {str(e)}")
        return

def mostrar_estadisticas():
    """Muestra estadísticas del sistema de cursos"""
    print(f"\n📈 Estadísticas del Sistema:")
    print(f"   - Total años académicos: {AcademicYear.objects.count()}")
    print(f"   - Total grados: {Grade.objects.count()}")
    print(f"   - Total cursos: {Course.objects.count()}")
    
    current_year = AcademicYear.objects.filter(is_current=True).first()
    if current_year:
        current_courses = Course.objects.filter(academic_year=current_year)
        print(f"   - Cursos año actual ({current_year.name}): {current_courses.count()}")
        print(f"   - Cursos activos: {current_courses.filter(is_active=True).count()}")
        
        total_capacity = sum(c.max_students for c in current_courses)
        print(f"   - Capacidad total del sistema: {total_capacity} estudiantes")

if __name__ == '__main__':
    print("=" * 60)
    print("🏫 CREADOR DE CURSOS DE EJEMPLO")
    print("=" * 60)
    
    crear_cursos_ejemplo()
    mostrar_estadisticas()
    
    print("\n" + "=" * 60)
    print("✨ ¡Script completado exitosamente!")
    print("   Ahora puede probar la gestión de cursos en la interfaz")
    print("=" * 60)