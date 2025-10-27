#!/usr/bin/env python
"""
Script para eliminar usuarios específicos
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')
django.setup()

from django.contrib.auth.models import User

# Usuarios a eliminar
users_to_delete = ['profesor_test', 'profesor_nuevo', 'angel', 'luis']

print("🗑️ Eliminando usuarios de prueba...")
print("=" * 50)

for username in users_to_delete:
    try:
        user = User.objects.get(username=username)
        print(f"❌ Eliminando usuario: {username} (ID: {user.id})")
        user.delete()
        print(f"✅ Usuario {username} eliminado exitosamente")
    except User.DoesNotExist:
        print(f"⚠️ Usuario {username} no encontrado")
    except Exception as e:
        print(f"❌ Error eliminando {username}: {e}")
    print()

print("🔍 Verificando usuarios restantes...")
remaining_users = User.objects.all()
print(f"Total de usuarios en el sistema: {remaining_users.count()}")
for user in remaining_users:
    role = "Sin perfil"
    if hasattr(user, 'profile') and user.profile:
        role = user.profile.role
    status = "Activo" if user.is_active else "Inactivo"
    print(f"- {user.username} | {role} | {status}")

print("\n✅ Proceso completado")