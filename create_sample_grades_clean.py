#!/usr/bin/env python

import os
import sys
import django

# Configurar Django
sys.path.append('C:\\Users\\jbang\\OneDrive\\Desktop\\gestion de proyectos')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')
django.setup()

from academics_extended.models import Grade

def create_sample_grades():
    """Crear grados de ejemplo para probar"""
    
    print("=== CREANDO GRADOS DE EJEMPLO ===")
    
    # Grados de Primaria
    primary_grades = [
        {"name": "1° Primaria", "level": "primaria", "order": 1},
        {"name": "2° Primaria", "level": "primaria", "order": 2},
        {"name": "3° Primaria", "level": "primaria", "order": 3},
        {"name": "4° Primaria", "level": "primaria", "order": 4},
        {"name": "5° Primaria", "level": "primaria", "order": 5},
    ]
    
    # Grados de Bachillerato
    secondary_grades = [
        {"name": "6° Bachillerato", "level": "bachillerato", "order": 6},
        {"name": "7° Bachillerato", "level": "bachillerato", "order": 7},
        {"name": "8° Bachillerato", "level": "bachillerato", "order": 8},
        {"name": "9° Bachillerato", "level": "bachillerato", "order": 9},
        {"name": "10° Bachillerato", "level": "bachillerato", "order": 10},
        {"name": "11° Bachillerato", "level": "bachillerato", "order": 11},
    ]
    
    all_grades = primary_grades + secondary_grades
    
    for grade_data in all_grades:
        grade, created = Grade.objects.get_or_create(
            order=grade_data["order"],
            defaults=grade_data
        )
        
        if created:
            print(f"✅ Creado: {grade.name} - {grade.get_level_display()}")
        else:
            print(f"⚠️  Ya existe: {grade.name} - {grade.get_level_display()}")
    
    print(f"\n=== RESUMEN ===")
    print(f"Total grados creados: {Grade.objects.count()}")
    print(f"Primaria: {Grade.objects.filter(level='primaria').count()}")
    print(f"Bachillerato: {Grade.objects.filter(level='bachillerato').count()}")
    
    print("\n=== LISTA DE GRADOS ===")
    for grade in Grade.objects.all().order_by('order'):
        print(f"  {grade.order}. {grade.name} - {grade.get_level_display()}")

if __name__ == "__main__":
    create_sample_grades()