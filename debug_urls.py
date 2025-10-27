#!/usr/bin/env python3
"""
Script para debuggear las URLs de Django
"""

import os
import sys
import django

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')
django.setup()

from django.urls import get_resolver

def print_urls(urlpatterns, prefix=''):
    """Imprime recursivamente todos los patrones de URL"""
    for pattern in urlpatterns:
        if hasattr(pattern, 'url_patterns'):
            # Es un include, recursivamente imprimir los patrones internos
            print(f"{prefix}{pattern.pattern} -> INCLUDE")
            print_urls(pattern.url_patterns, prefix + '  ')
        else:
            # Es un patrón directo
            callback_name = getattr(pattern.callback, '__name__', str(pattern.callback))
            print(f"{prefix}{pattern.pattern} -> {callback_name}")

def main():
    print("🔍 ANÁLISIS DE URLs DE DJANGO")
    print("=" * 50)
    
    resolver = get_resolver()
    print_urls(resolver.url_patterns)
    
    print("\n" + "=" * 50)
    print("🎯 URLs específicas de academics_extended/schedules:")
    
    # Buscar específicamente patrones relacionados con schedules
    schedules_patterns = []
    
    def find_schedules_patterns(patterns, base_path=''):
        for pattern in patterns:
            if hasattr(pattern, 'url_patterns'):
                new_base = base_path + str(pattern.pattern)
                find_schedules_patterns(pattern.url_patterns, new_base)
            else:
                full_path = base_path + str(pattern.pattern)
                if 'schedules' in full_path:
                    schedules_patterns.append((full_path, pattern.callback))
    
    find_schedules_patterns(resolver.url_patterns)
    
    for path, callback in schedules_patterns:
        callback_name = getattr(callback, '__name__', str(callback))
        print(f"  {path} -> {callback_name}")

if __name__ == "__main__":
    main()