#!/usr/bin/env python

from django.contrib.auth.models import User
from authentication.models import UserProfile

print("LIMPIANDO Y CORRIGIENDO USUARIOS")
print("=" * 40)

# 1. Listar usuarios actuales
print("\n1. USUARIOS ACTUALES:")
users = User.objects.select_related('profile').all()
for user in users:
    if hasattr(user, 'profile'):
        role = user.profile.role
    else:
        role = 'Sin perfil'
    print(f"- {user.username}: {user.first_name} {user.last_name} ({role})")

# 2. Corregir usuarios con roles incorrectos
print("\n2. CORRIGIENDO ROLES:")

# Corregir profesor_test si existe
if User.objects.filter(username='profesor_test').exists():
    user = User.objects.get(username='profesor_test')
    if hasattr(user, 'profile'):
        user.profile.role = 'teacher'
        user.profile.save()
        print(f"✅ {user.username} corregido a 'teacher'")
    else:
        UserProfile.objects.create(user=user, role='teacher')
        print(f"✅ {user.username} perfil creado como 'teacher'")

# Corregir profesor_nuevo si existe
if User.objects.filter(username='profesor_nuevo').exists():
    user = User.objects.get(username='profesor_nuevo')
    if hasattr(user, 'profile'):
        user.profile.role = 'teacher'
        user.profile.save()
        print(f"✅ {user.username} corregido a 'teacher'")
    else:
        UserProfile.objects.create(user=user, role='teacher')
        print(f"✅ {user.username} perfil creado como 'teacher'")

# 3. Eliminar usuarios de prueba si no son necesarios
print("\n3. LIMPIANDO USUARIOS DE PRUEBA:")
usuarios_prueba = ['profesor_test', 'profesor_nuevo']
for username in usuarios_prueba:
    if User.objects.filter(username=username).exists():
        User.objects.get(username=username).delete()
        print(f"🗑️ {username} eliminado")

# 4. Estado final
print("\n4. USUARIOS FINALES:")
users = User.objects.select_related('profile').all()
for user in users:
    if hasattr(user, 'profile'):
        role = user.profile.role
    else:
        role = 'Sin perfil'
    print(f"- {user.username}: {user.first_name} {user.last_name} ({role})")

print(f"\nTotal usuarios: {User.objects.count()}")
print("✅ Limpieza completada")