#!/usr/bin/env python
"""
Script para limpiar la materia de prueba
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')
django.setup()

def clean_test_subject():
    """Eliminar la materia de prueba"""
    
    try:
        from academics_extended.models import Subject
        
        # Buscar y eliminar la materia de prueba
        test_subject = Subject.objects.filter(code='TEST').first()
        if test_subject:
            print(f"Eliminando materia de prueba: {test_subject.name} ({test_subject.code})")
            test_subject.delete()
            print("✅ Materia de prueba eliminada")
        else:
            print("ℹ️  No se encontró materia de prueba para eliminar")
        
        # Mostrar el total actual
        total = Subject.objects.count()
        print(f"Total de materias actuales: {total}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    clean_test_subject()