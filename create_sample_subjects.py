#!/usr/bin/env python
"""
Script para crear materias de ejemplo en el sistema académico
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')
django.setup()

from academics_extended.models import Subject

def create_sample_subjects():
    """Crear materias de ejemplo para el sistema"""
    
    print("=== CREANDO MATERIAS DE EJEMPLO ===")
    
    # Lista de materias por área
    subjects_data = [
        # Matemáticas
        {'name': 'Matemáticas', 'code': 'MAT', 'area': 'matematicas', 'hours_per_week': 5, 'description': 'Matemáticas básicas y avanzadas'},
        {'name': 'Álgebra', 'code': 'ALG', 'area': 'matematicas', 'hours_per_week': 4, 'description': 'Álgebra elemental y superior'},
        {'name': 'Geometría', 'code': 'GEO', 'area': 'matematicas', 'hours_per_week': 3, 'description': 'Geometría plana y espacial'},
        {'name': 'Cálculo', 'code': 'CAL', 'area': 'matematicas', 'hours_per_week': 4, 'description': 'Cálculo diferencial e integral'},
        {'name': 'Estadística', 'code': 'EST', 'area': 'matematicas', 'hours_per_week': 3, 'description': 'Estadística y probabilidades'},
        
        # Ciencias Naturales
        {'name': 'Biología', 'code': 'BIO', 'area': 'ciencias', 'hours_per_week': 4, 'description': 'Ciencias biológicas y naturales'},
        {'name': 'Física', 'code': 'FIS', 'area': 'ciencias', 'hours_per_week': 4, 'description': 'Física general y aplicada'},
        {'name': 'Química', 'code': 'QUI', 'area': 'ciencias', 'hours_per_week': 4, 'description': 'Química general e inorgánica'},
        {'name': 'Ciencias Naturales', 'code': 'CNT', 'area': 'ciencias', 'hours_per_week': 3, 'description': 'Ciencias naturales integradas'},
        
        # Ciencias Sociales
        {'name': 'Historia', 'code': 'HIS', 'area': 'sociales', 'hours_per_week': 3, 'description': 'Historia universal y nacional'},
        {'name': 'Geografía', 'code': 'GEF', 'area': 'sociales', 'hours_per_week': 2, 'description': 'Geografía física y humana'},
        {'name': 'Ciencias Sociales', 'code': 'CSO', 'area': 'sociales', 'hours_per_week': 4, 'description': 'Ciencias sociales integradas'},
        {'name': 'Filosofía', 'code': 'FIL', 'area': 'sociales', 'hours_per_week': 2, 'description': 'Filosofía e historia del pensamiento'},
        
        # Lenguaje y Literatura
        {'name': 'Español', 'code': 'ESP', 'area': 'lenguaje', 'hours_per_week': 5, 'description': 'Lengua española y literatura'},
        {'name': 'Literatura', 'code': 'LIT', 'area': 'lenguaje', 'hours_per_week': 3, 'description': 'Literatura universal y nacional'},
        {'name': 'Lectura Crítica', 'code': 'LEC', 'area': 'lenguaje', 'hours_per_week': 2, 'description': 'Comprensión lectora y análisis textual'},
        
        # Inglés
        {'name': 'Inglés', 'code': 'ING', 'area': 'ingles', 'hours_per_week': 3, 'description': 'Idioma inglés básico e intermedio'},
        {'name': 'Inglés Avanzado', 'code': 'INA', 'area': 'ingles', 'hours_per_week': 4, 'description': 'Inglés avanzado y conversación'},
        
        # Educación Física
        {'name': 'Educación Física', 'code': 'EDF', 'area': 'educacion_fisica', 'hours_per_week': 2, 'description': 'Actividad física y deportes'},
        {'name': 'Deportes', 'code': 'DEP', 'area': 'educacion_fisica', 'hours_per_week': 2, 'description': 'Práctica deportiva especializada'},
        
        # Artes
        {'name': 'Artes Plásticas', 'code': 'ART', 'area': 'artes', 'hours_per_week': 2, 'description': 'Dibujo, pintura y manualidades'},
        {'name': 'Música', 'code': 'MUS', 'area': 'artes', 'hours_per_week': 2, 'description': 'Educación musical y coro'},
        {'name': 'Danzas', 'code': 'DAN', 'area': 'artes', 'hours_per_week': 1, 'description': 'Danzas folclóricas y modernas'},
        
        # Informática
        {'name': 'Informática', 'code': 'INF', 'area': 'informatica', 'hours_per_week': 2, 'description': 'Computación básica y ofimática'},
        {'name': 'Programación', 'code': 'PRO', 'area': 'informatica', 'hours_per_week': 3, 'description': 'Programación y desarrollo de software'},
        
        # Religión y Ética
        {'name': 'Religión', 'code': 'REL', 'area': 'religion', 'hours_per_week': 1, 'description': 'Educación religiosa'},
        {'name': 'Ética y Valores', 'code': 'ETI', 'area': 'etica', 'hours_per_week': 1, 'description': 'Formación ética y en valores'},
    ]
    
    created_count = 0
    existing_count = 0
    
    for subject_data in subjects_data:
        # Verificar si la materia ya existe
        existing = Subject.objects.filter(code=subject_data['code']).first()
        if existing:
            print(f"⚠️  Ya existe: {existing.name} ({existing.code})")
            existing_count += 1
        else:
            # Crear nueva materia
            subject = Subject.objects.create(**subject_data)
            print(f"✅ Creada: {subject.name} ({subject.code}) - {subject.get_area_display()}")
            created_count += 1
    
    print(f"\n=== RESUMEN ===")
    print(f"Total materias creadas: {created_count}")
    print(f"Total materias existentes: {existing_count}")
    
    # Mostrar estadísticas por área
    print(f"\n=== MATERIAS POR ÁREA ===")
    for area_code, area_name in Subject.AREA_CHOICES:
        count = Subject.objects.filter(area=area_code).count()
        print(f"{area_name}: {count} materias")
    
    print(f"\n=== LISTA DE TODAS LAS MATERIAS ===")
    subjects = Subject.objects.all().order_by('area', 'name')
    for i, subject in enumerate(subjects, 1):
        print(f"  {i:2d}. {subject.name} ({subject.code}) - {subject.get_area_display()} - {subject.hours_per_week}h/semana")

if __name__ == '__main__':
    create_sample_subjects()