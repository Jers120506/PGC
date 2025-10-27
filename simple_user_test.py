#!/usr/bin/env python
"""
Script simple para probar usuarios
"""

from django.contrib.auth.models import User
from authentication.models import UserProfile

print("PROBANDO GESTION DE USUARIOS")
print("=" * 40)

# Listar usuarios actuales
print("\nUsuarios actuales:")
users = User.objects.select_related('profile').all()
for user in users:
    role = user.profile.role if hasattr(user, 'profile') else 'Sin perfil'
    status = "Activo" if user.is_active else "Inactivo"
    print(f"- {user.username}: {user.first_name} {user.last_name} ({role}) [{status}]")

# Crear usuario de prueba
test_username = "profesor_test"
if User.objects.filter(username=test_username).exists():
    User.objects.get(username=test_username).delete()
    print(f"\nUsuario {test_username} eliminado para prueba limpia")

# Crear nuevo usuario
test_user = User.objects.create_user(
    username=test_username,
    email="profesor.test@colegio.com",
    password="test123",
    first_name="Profesor",
    last_name="De Prueba"
)

# Crear perfil
UserProfile.objects.create(
    user=test_user,
    role='teacher'
)

print(f"\nUsuario {test_username} creado exitosamente!")
print(f"Email: {test_user.email}")
print(f"Nombre: {test_user.first_name} {test_user.last_name}")
print(f"Rol: teacher")

# Estadisticas
print(f"\nEstadisticas:")
print(f"Total usuarios: {User.objects.count()}")
print(f"Administradores: {User.objects.filter(profile__role='admin').count()}")
print(f"Secretarios: {User.objects.filter(profile__role='secretary').count()}")
print(f"Profesores: {User.objects.filter(profile__role='teacher').count()}")

print("\nPrueba la interfaz web en: http://127.0.0.1:8000/administration/admin/users/")
print("=" * 40)