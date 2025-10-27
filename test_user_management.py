#!/usr/bin/env python
"""
Script para probar la gestión de usuarios del administrador
"""

import os
import django
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')
django.setup()

from django.contrib.auth.models import User
from authentication.models import UserProfile

def probar_gestion_usuarios():
    """Prueba las funcionalidades de gestión de usuarios"""
    
    print("🧪 PROBANDO GESTIÓN DE USUARIOS DEL ADMINISTRADOR")
    print("=" * 60)
    
    # Verificar usuario admin existe
    print("\n1️⃣ Verificando usuario administrador:")
    try:
        admin_user = User.objects.get(username='admin')
        admin_profile = admin_user.profile
        print(f"   ✅ Usuario admin encontrado: {admin_user.first_name} {admin_user.last_name}")
        print(f"   ✅ Rol: {admin_profile.role}")
        print(f"   ✅ Activo: {'Sí' if admin_user.is_active else 'No'}")
    except User.DoesNotExist:
        print("   ❌ Usuario admin no encontrado")
        return False
    
    # Listar todos los usuarios actuales
    print("\n2️⃣ Usuarios actuales en el sistema:")
    users = User.objects.select_related('profile').all()
    for user in users:
        role = user.profile.role if hasattr(user, 'profile') else 'Sin perfil'
        status = "🟢 Activo" if user.is_active else "🔴 Inactivo"
        print(f"   📋 {user.username}: {user.first_name} {user.last_name} ({role}) {status}")
    
    # Crear usuario de prueba
    print("\n3️⃣ Creando usuario de prueba:")
    test_username = "profesor_test"
    
    # Eliminar si ya existe
    if User.objects.filter(username=test_username).exists():
        User.objects.get(username=test_username).delete()
        print(f"   🗑️ Usuario {test_username} eliminado para prueba limpia")
    
    # Crear usuario de prueba
    try:
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
        
        print(f"   ✅ Usuario {test_username} creado exitosamente")
        print(f"   📧 Email: {test_user.email}")
        print(f"   👤 Nombre: {test_user.first_name} {test_user.last_name}")
        print(f"   🎭 Rol: teacher")
        
    except Exception as e:
        print(f"   ❌ Error creando usuario: {e}")
        return False
    
    # Probar cambio de estado
    print("\n4️⃣ Probando cambio de estado:")
    test_user.is_active = False
    test_user.save()
    print(f"   ✅ Usuario {test_username} desactivado")
    
    test_user.is_active = True
    test_user.save()
    print(f"   ✅ Usuario {test_username} reactivado")
    
    # Probar cambio de contraseña
    print("\n5️⃣ Probando cambio de contraseña:")
    test_user.set_password("nueva_password_123")
    test_user.save()
    print(f"   ✅ Contraseña de {test_username} cambiada")
    
    # Estadísticas finales
    print("\n6️⃣ Estadísticas del sistema:")
    print(f"   👥 Total usuarios: {User.objects.count()}")
    print(f"   👨‍💼 Administradores: {User.objects.filter(profile__role='admin').count()}")
    print(f"   👩‍💼 Secretarios: {User.objects.filter(profile__role='secretary').count()}")
    print(f"   👨‍🏫 Profesores: {User.objects.filter(profile__role='teacher').count()}")
    print(f"   🟢 Usuarios activos: {User.objects.filter(is_active=True).count()}")
    print(f"   🔴 Usuarios inactivos: {User.objects.filter(is_active=False).count()}")
    
    print("\n" + "=" * 60)
    print("✅ TODAS LAS PRUEBAS DE GESTIÓN DE USUARIOS COMPLETADAS")
    print("🌐 Prueba la interfaz web en: http://127.0.0.1:8000/administration/admin/users/")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    probar_gestion_usuarios()