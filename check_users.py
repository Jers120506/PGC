#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')
django.setup()

from django.contrib.auth.models import User
from authentication.models import UserProfile

print("=== USUARIOS DISPONIBLES ===")
users = User.objects.all()

if not users.exists():
    print("❌ No hay usuarios en el sistema")
else:
    for u in users:
        try:
            role = u.profile.role if hasattr(u, 'profile') and u.profile else "Sin perfil"
        except:
            role = "Sin perfil"
        
        print(f"Usuario: {u.username}")
        print(f"  - Nombre: {u.first_name} {u.last_name}")
        print(f"  - Email: {u.email}")
        print(f"  - Role: {role}")
        print(f"  - Staff: {u.is_staff}")
        print(f"  - Superuser: {u.is_superuser}")
        print(f"  - Activo: {u.is_active}")
        print("---")

print(f"\nTotal usuarios: {users.count()}")