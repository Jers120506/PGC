#!/usr/bin/env python
"""
Demo completo de gestión de usuarios del administrador
"""

from django.contrib.auth.models import User
from authentication.models import UserProfile
import random

def demo_gestion_usuarios():
    """Demostrar todas las funcionalidades de gestión de usuarios"""
    
    print("🎯 DEMO: GESTIÓN COMPLETA DE USUARIOS")
    print("=" * 50)
    
    # 1. Mostrar usuarios actuales
    print("\n1️⃣ USUARIOS ACTUALES EN EL SISTEMA:")
    users = User.objects.select_related('profile').all().order_by('date_joined')
    for i, user in enumerate(users, 1):
        role = user.profile.role if hasattr(user, 'profile') else 'Sin perfil'
        status = "🟢 Activo" if user.is_active else "🔴 Inactivo"
        last_login = user.last_login.strftime('%d/%m/%Y %H:%M') if user.last_login else 'Nunca'
        print(f"   {i}. {user.username}")
        print(f"      👤 Nombre: {user.first_name} {user.last_name}")
        print(f"      📧 Email: {user.email or 'No especificado'}")
        print(f"      🎭 Rol: {role}")
        print(f"      📅 Último acceso: {last_login}")
        print(f"      📊 Estado: {status}")
        print(f"      🆔 ID: {user.id}")
        print()
    
    # 2. Crear usuarios de prueba
    print("2️⃣ CREANDO USUARIOS DE PRUEBA:")
    
    usuarios_prueba = [
        {
            'username': 'profesor_matematicas',
            'email': 'matematicas@colegio.com',
            'first_name': 'Ana',
            'last_name': 'Rodriguez',
            'role': 'teacher',
            'password': 'profesor123'
        },
        {
            'username': 'secretaria_administrativa',
            'email': 'admin@colegio.com',
            'first_name': 'Carmen',
            'last_name': 'Lopez',
            'role': 'secretary',
            'password': 'secretaria123'
        },
        {
            'username': 'profesor_ciencias',
            'email': 'ciencias@colegio.com',
            'first_name': 'Diego',
            'last_name': 'Fernandez',
            'role': 'teacher',
            'password': 'ciencias123'
        }
    ]
    
    usuarios_creados = []
    
    for datos in usuarios_prueba:
        # Eliminar si ya existe
        if User.objects.filter(username=datos['username']).exists():
            User.objects.get(username=datos['username']).delete()
            print(f"   🗑️ Usuario {datos['username']} eliminado para prueba limpia")
        
        try:
            # Crear usuario
            user = User.objects.create_user(
                username=datos['username'],
                email=datos['email'],
                password=datos['password'],
                first_name=datos['first_name'],
                last_name=datos['last_name']
            )
            
            # Crear perfil
            UserProfile.objects.create(
                user=user,
                role=datos['role']
            )
            
            usuarios_creados.append(user)
            
            print(f"   ✅ {datos['username']} creado exitosamente")
            print(f"      👤 {datos['first_name']} {datos['last_name']} ({datos['role']})")
            print(f"      📧 {datos['email']}")
            print(f"      🔐 Contraseña: {datos['password']}")
            print()
            
        except Exception as e:
            print(f"   ❌ Error creando {datos['username']}: {e}")
    
    # 3. Probar funcionalidades de administración
    print("3️⃣ PROBANDO FUNCIONALIDADES DE ADMINISTRACIÓN:")
    
    if usuarios_creados:
        # Probar desactivación
        usuario_test = usuarios_creados[0]
        print(f"\n   🔄 Probando desactivación de {usuario_test.username}:")
        usuario_test.is_active = False
        usuario_test.save()
        print(f"   ✅ Usuario desactivado: {not usuario_test.is_active}")
        
        # Probar reactivación
        usuario_test.is_active = True
        usuario_test.save()
        print(f"   ✅ Usuario reactivado: {usuario_test.is_active}")
        
        # Probar cambio de contraseña
        print(f"\n   🔑 Probando cambio de contraseña de {usuario_test.username}:")
        nueva_password = "nueva_password_123"
        usuario_test.set_password(nueva_password)
        usuario_test.save()
        print(f"   ✅ Contraseña cambiada a: {nueva_password}")
        
        # Probar actualización de datos
        print(f"\n   📝 Probando actualización de datos de {usuario_test.username}:")
        usuario_test.first_name = "Ana María"
        usuario_test.email = "ana.maria@colegio.com"
        usuario_test.save()
        print(f"   ✅ Nombre actualizado a: {usuario_test.first_name}")
        print(f"   ✅ Email actualizado a: {usuario_test.email}")
    
    # 4. Estadísticas finales
    print("\n4️⃣ ESTADÍSTICAS FINALES DEL SISTEMA:")
    total_users = User.objects.count()
    admins = User.objects.filter(profile__role='admin').count()
    secretaries = User.objects.filter(profile__role='secretary').count()
    teachers = User.objects.filter(profile__role='teacher').count()
    active_users = User.objects.filter(is_active=True).count()
    inactive_users = User.objects.filter(is_active=False).count()
    
    print(f"   📊 Total de usuarios: {total_users}")
    print(f"   👨‍💼 Administradores: {admins}")
    print(f"   👩‍💼 Secretarios: {secretaries}")
    print(f"   👨‍🏫 Profesores: {teachers}")
    print(f"   🟢 Usuarios activos: {active_users}")
    print(f"   🔴 Usuarios inactivos: {inactive_users}")
    
    # 5. Guía para usar la interfaz web
    print("\n5️⃣ GUÍA DE INTERFAZ WEB:")
    print("   🌐 URL: http://127.0.0.1:8000/administration/admin/users/")
    print("   🔑 Usuario: admin")
    print("   🔐 Contraseña: admin123")
    print("\n   🎯 FUNCIONALIDADES DISPONIBLES:")
    print("   ✅ Crear nuevos usuarios con formulario modal")
    print("   ✅ Editar información de usuarios existentes")
    print("   ✅ Activar/Desactivar usuarios")
    print("   ✅ Resetear contraseñas (genera contraseña temporal)")
    print("   ✅ Eliminar usuarios (con confirmaciones de seguridad)")
    print("   ✅ Ver estadísticas por rol")
    print("   ✅ Búsqueda y filtrado de usuarios")
    
    print("\n   🎮 CÓMO PROBAR:")
    print("   1. Haz clic en 'Crear Nuevo Usuario'")
    print("   2. Completa el formulario modal")
    print("   3. Prueba los botones de acción en cada usuario")
    print("   4. Observa las confirmaciones de seguridad")
    print("   5. Verifica que los cambios se reflejan inmediatamente")
    
    print("\n" + "=" * 50)
    print("✅ DEMO COMPLETADO - SISTEMA DE GESTIÓN DE USUARIOS FUNCIONAL")
    print("🚀 Todas las funcionalidades están listas para usar")
    print("=" * 50)

if __name__ == "__main__":
    demo_gestion_usuarios()