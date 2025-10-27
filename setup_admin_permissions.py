#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')
django.setup()

from django.contrib.auth.models import User

print("=== CONFIGURANDO PERMISOS DE ADMINISTRADOR ===")

try:
    admin_user = User.objects.get(username='admin')
    print(f"Usuario encontrado: {admin_user.username}")
    
    # Hacer staff y superuser
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.save()
    
    print("✅ Usuario 'admin' ahora es staff y superuser")
    print(f"  - Staff: {admin_user.is_staff}")
    print(f"  - Superuser: {admin_user.is_superuser}")
    print(f"  - Activo: {admin_user.is_active}")
    
    # Verificar contraseña
    print(f"\n📋 CREDENCIALES DE ACCESO:")
    print(f"   Username: admin")
    print(f"   Password: admin123")
    print(f"   Puede acceder a: /admin/ y /administration/")
    
except User.DoesNotExist:
    print("❌ Usuario 'admin' no encontrado")
    
    # Crear superuser si no existe
    print("Creando nuevo superuser...")
    admin_user = User.objects.create_superuser(
        username='admin',
        email='admin@colegialabalsa.edu.co',
        password='admin123',
        first_name='Administrador',
        last_name='Colegio La Balsa'
    )
    
    # Crear perfil de administrador
    from authentication.models import UserProfile
    profile, created = UserProfile.objects.get_or_create(
        user=admin_user,
        defaults={'role': 'admin'}
    )
    
    print("✅ Superuser creado exitosamente")

except Exception as e:
    print(f"❌ Error: {e}")

print("\n=== ESTADO FINAL ===")
for user in User.objects.filter(username='admin'):
    print(f"Usuario: {user.username}")
    print(f"  - Staff: {user.is_staff}")
    print(f"  - Superuser: {user.is_superuser}")
    print(f"  - Activo: {user.is_active}")