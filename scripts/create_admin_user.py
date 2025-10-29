
"""
Script para crear usuario administrador en Render durante el despliegue
Este script se ejecuta automáticamente cuando se despliega la aplicación en Render
"""

import os
import sys
import django
from pathlib import Path

# Agregar el directorio raíz del proyecto al path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')
django.setup()

from django.contrib.auth.models import User
from django.core.management import execute_from_command_line
from authentication.models import UserProfile

def create_admin_user():
    """Crear usuario administrador si no existe"""

    # Datos del administrador desde variables de entorno o valores por defecto
    admin_username = os.getenv('ADMIN_USERNAME', 'admin')
    admin_email = os.getenv('ADMIN_EMAIL', 'admin@colegialabalsa.edu.co')
    admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
    admin_first_name = os.getenv('ADMIN_FIRST_NAME', 'Administrador')
    admin_last_name = os.getenv('ADMIN_LAST_NAME', 'Sistema')

    print("🔧 Creando usuario administrador para despliegue en Render...")
    print(f"   Usuario: {admin_username}")
    print(f"   Email: {admin_email}")

    try:
        # Verificar si el usuario ya existe
        admin_user, created = User.objects.get_or_create(
            username=admin_username,
            defaults={
                'email': admin_email,
                'first_name': admin_first_name,
                'last_name': admin_last_name,
                'is_staff': True,
                'is_superuser': True,
                'is_active': True
            }
        )

        # Si el usuario ya existía, actualizar permisos
        if not created:
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.is_active = True
            admin_user.email = admin_email
            admin_user.first_name = admin_first_name
            admin_user.last_name = admin_last_name

        # Establecer contraseña
        admin_user.set_password(admin_password)
        admin_user.save()

        print(f"✅ Usuario administrador {'creado' if created else 'actualizado'} exitosamente")

        # Crear o actualizar perfil de administrador
        profile, profile_created = UserProfile.objects.get_or_create(
            user=admin_user,
            defaults={
                'role': 'admin',
                'phone': os.getenv('ADMIN_PHONE', '300-000-0000'),
                'address': 'Dirección del Administrador',
                'date_of_birth': '1980-01-01',
                'profile_completion_percentage': 100,
                'department': 'Administración',
                'position': 'Administrador del Sistema'
            }
        )

        if not profile_created:
            profile.role = 'admin'
            profile.save()

        print("✅ Perfil de administrador configurado")

        # Mostrar credenciales de acceso
        print("\n🔑 CREDENCIALES DE ACCESO:")
        print("=" * 40)
        print(f"   Usuario: {admin_username}")
        print(f"   Contraseña: {admin_password}")
        print(f"   Email: {admin_email}")
        print("\n🌐 URLs de acceso:")
        print(f"   Panel de administración: /admin/")
        print(f"   Sistema escolar: /administration/")
        print(f"   Login: /auth/login/")

        return True

    except Exception as e:
        print(f"❌ Error al crear usuario administrador: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_migrations():
    """Ejecutar migraciones si es necesario"""
    print("\n📦 Verificando migraciones...")

    try:
        # Ejecutar migraciones
        execute_from_command_line(['manage.py', 'migrate', '--verbosity=1'])
        print("✅ Migraciones ejecutadas correctamente")
        return True
    except Exception as e:
        print(f"❌ Error en migraciones: {e}")
        return False

def collect_static():
    """Recolectar archivos estáticos si es necesario"""
    print("\n📁 Recolectando archivos estáticos...")

    try:
        # Solo recolectar estáticos en producción
        if os.getenv('DEBUG', 'True').lower() == 'false':
            execute_from_command_line(['manage.py', 'collectstatic', '--noinput', '--verbosity=1'])
            print("✅ Archivos estáticos recolectados")
        else:
            print("⏭️  Modo desarrollo - saltando collectstatic")
        return True
    except Exception as e:
        print(f"❌ Error recolectando estáticos: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 INICIANDO CONFIGURACIÓN PARA RENDER")
    print("=" * 50)

    # Verificar variables de entorno críticas
    print("📋 VERIFICANDO CONFIGURACIÓN:")
    print(f"   DEBUG: {os.getenv('DEBUG', 'True')}")
    print(f"   USE_RENDER_DB: {os.getenv('USE_RENDER_DB', 'False')}")
    print(f"   SECRET_KEY: {'✅ Configurada' if os.getenv('SECRET_KEY') else '❌ No configurada'}")
    print(f"   DATABASE_URL: {'✅ Configurada' if os.getenv('DATABASE_URL') else '❌ No configurada'}")

    # Ejecutar migraciones
    if not run_migrations():
        print("❌ Falló la ejecución de migraciones")
        return False

    # Recolectar estáticos
    if not collect_static():
        print("❌ Falló la recolección de estáticos")
        return False

    # Crear usuario administrador
    if not create_admin_user():
        print("❌ Falló la creación del usuario administrador")
        return False

    print("\n🎉 ¡CONFIGURACIÓN COMPLETADA EXITOSAMENTE!")
    print("=" * 50)
    print("El sistema está listo para usar en Render.")
    print("Recuerda configurar las siguientes variables de entorno en Render:")
    print("  - SECRET_KEY")
    print("  - DATABASE_URL")
    print("  - DEBUG=False")
    print("  - USE_RENDER_DB=True")
    print("  - ALLOWED_HOSTS (tu dominio de Render)")

    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
