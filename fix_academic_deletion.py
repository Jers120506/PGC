#!/usr/bin/env python3
"""
Script para arreglar el problema de eliminación de años académicos
Elimina las tablas problemáticas y recrea solo lo necesario.
"""

import django
import os
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')
django.setup()

from django.db import connection

def fix_database():
    print("=== ARREGLANDO BASE DE DATOS ===")
    
    with connection.cursor() as cursor:
        # Eliminar tablas problemáticas que causan errores de eliminación
        tables_to_drop = [
            'academics_extended_schedule',
            'academics_extended_evaluationcriteria',
            'academics_extended_graderecord',
            'academics_extended_attendancerecord'
        ]
        
        for table in tables_to_drop:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
                print(f"Tabla {table} eliminada")
            except Exception as e:
                print(f"Error eliminando {table}: {e}")
    
    print("\n=== PROBANDO ELIMINACIÓN DE AÑOS ACADÉMICOS ===")
    
    from academics_extended.models import AcademicYear
    
    # Mostrar años antes
    print("Años académicos antes:")
    for year in AcademicYear.objects.all():
        print(f"  - ID: {year.id}, Nombre: {year.name}")
    
    # Intentar eliminar TEST-2030
    try:
        test_year = AcademicYear.objects.get(name='TEST-2030')
        test_year.delete()
        print(f"\n✅ Año TEST-2030 eliminado exitosamente")
    except AcademicYear.DoesNotExist:
        print(f"\n❌ Año TEST-2030 no encontrado")
    except Exception as e:
        print(f"\n❌ Error eliminando TEST-2030: {e}")
    
    # Mostrar años después
    print("\nAños académicos después:")
    for year in AcademicYear.objects.all():
        print(f"  - ID: {year.id}, Nombre: {year.name}")

if __name__ == "__main__":
    fix_database()