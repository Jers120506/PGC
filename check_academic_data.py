#!/usr/bin/env python3
"""
Script para verificar y crear datos académicos de muestra
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')
django.setup()

from academics_extended.models import AcademicYear, Grade, Subject, Course
from datetime import date

def check_academic_data():
    print("=== VERIFICACIÓN DE DATOS ACADÉMICOS ===")
    
    # Verificar año académico
    current_year = AcademicYear.objects.filter(is_current=True).first()
    print(f"Año académico actual: {current_year}")
    
    if not current_year:
        print("Creando año académico 2025...")
        current_year = AcademicYear.objects.create(
            name="2025",
            start_date=date(2025, 1, 15),
            end_date=date(2025, 12, 15),
            is_current=True
        )
        print(f"✅ Año académico creado: {current_year}")
    
    # Verificar grados
    grades_count = Grade.objects.count()
    print(f"Grados registrados: {grades_count}")
    
    if grades_count == 0:
        print("Creando grados básicos...")
        # Primaria
        for i in range(1, 6):
            Grade.objects.create(
                name=f"{i}° Primaria",
                level="primaria",
                order=i
            )
        
        # Bachillerato
        for i in range(6, 12):
            Grade.objects.create(
                name=f"{i}° Bachillerato", 
                level="bachillerato",
                order=i
            )
        print("✅ Grados creados")
    
    # Verificar materias
    subjects_count = Subject.objects.count()
    print(f"Materias registradas: {subjects_count}")
    
    if subjects_count == 0:
        print("Creando materias básicas...")
        basic_subjects = [
            "Matemáticas", "Lengua Castellana", "Ciencias Naturales",
            "Ciencias Sociales", "Educación Física", "Educación Artística",
            "Inglés", "Informática", "Ética y Valores"
        ]
        
        for subject_name in basic_subjects:
            Subject.objects.create(
                name=subject_name,
                description=f"Materia de {subject_name}"
            )
        print("✅ Materias básicas creadas")
    
    # Verificar cursos
    courses_count = Course.objects.count()
    print(f"Cursos registrados: {courses_count}")
    
    # Mostrar estadísticas finales
    print("\n=== ESTADÍSTICAS FINALES ===")
    print(f"Años académicos: {AcademicYear.objects.count()}")
    print(f"Grados: {Grade.objects.count()}")
    print(f"Materias: {Subject.objects.count()}")
    print(f"Cursos: {Course.objects.count()}")
    
    print("\n✅ Verificación completada")

if __name__ == "__main__":
    check_academic_data()