#!/usr/bin/env python

import os
import sys
import django

# Configurar Django
sys.path.append('C:\\Users\\jbang\\OneDrive\\Desktop\\gestion de proyectos')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')
django.setup()

from django.contrib.auth.models import User

def create_test_user():
    """Crear usuario de prueba"""
    
    print("=== CREANDO USUARIO DE PRUEBA ===")
    
    username = "admin"
    password = "admin123"
    
    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
        print(f"⚠️  El usuario '{username}' ya existe")
    else:
        user = User.objects.create_user(
            username=username,
            password=password,
            email="admin@test.com",
            is_staff=True,
            is_superuser=True
        )
        print(f"✅ Usuario '{username}' creado exitosamente")
    
    print(f"Usuario: {username}")
    print(f"Contraseña: {password}")
    print(f"URL de login: http://localhost:8000/auth/login/")

if __name__ == "__main__":
    create_test_user()