#!/usr/bin/env python
"""
Script para crear usuario de prueba para testing
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')
django.setup()

from django.contrib.auth.models import User
from authentication.models import UserProfile

print("👤 Creando usuario de prueba para testing...")
print("=" * 50)

# Crear usuario de prueba
username = "usuario_prueba"

# Eliminar si existe
if User.objects.filter(username=username).exists():
    User.objects.get(username=username).delete()
    print(f"⚠️ Usuario {username} ya existía, eliminado")

try:
    # Crear nuevo usuario
    user = User.objects.create_user(
        username=username,
        email="prueba@test.com",
        password="123456",
        first_name="Usuario",
        last_name="Prueba"
    )

    # Crear perfil
    profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={'role': 'teacher'}
    )
    
    if not created:
        profile.role = 'teacher'
        profile.save()

    print(f"✅ Usuario {username} creado exitosamente!")
    print(f"📧 Email: {user.email}")
    print(f"👤 Nombre: {user.first_name} {user.last_name}")
    print(f"🎭 Rol: {profile.role}")
    print(f"🟢 Activo: {user.is_active}")
    
except Exception as e:
    print(f"❌ Error: {e}")

print("\n🔍 Usuarios actuales en el sistema:")
for u in User.objects.all():
    role = u.profile.role if hasattr(u, 'profile') and u.profile else 'Sin perfil'
    status = "🟢 Activo" if u.is_active else "🔴 Inactivo"
    print(f"- {u.username}: {u.first_name} {u.last_name} ({role}) {status}")

print(f"\n📊 Total usuarios: {User.objects.count()}")