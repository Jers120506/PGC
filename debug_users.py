#!/usr/bin/env python
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')
django.setup()

from django.contrib.auth.models import User
from authentication.models import UserProfile

def debug_users():
    print("=== DEBUG: Estado de usuarios y botones ===\n")
    
    # Obtener todos los usuarios
    users = User.objects.select_related('profile').order_by('date_joined')
    
    print(f"Total de usuarios: {users.count()}\n")
    
    for user in users:
        print(f"👤 Usuario: {user.username}")
        print(f"   - ID: {user.id}")
        print(f"   - Nombre: {user.first_name} {user.last_name}")
        print(f"   - Email: {user.email}")
        print(f"   - Superusuario: {user.is_superuser}")
        print(f"   - Activo: {user.is_active}")
        
        # Verificar perfil
        try:
            profile = user.profile
            print(f"   - Perfil: {profile.role}")
        except UserProfile.DoesNotExist:
            print(f"   - Perfil: ❌ NO EXISTE")
        
        # Determinar qué botones deberían aparecer
        print("   - Botones que deberían aparecer:")
        print("     * Editar: ✅ Siempre visible")
        
        if not user.is_superuser:
            print("     * Activar/Desactivar: ✅ Visible (no es superusuario)")
        else:
            print("     * Activar/Desactivar: ❌ Oculto (es superusuario)")
            
        print("     * Resetear Contraseña: ✅ Siempre visible")
        
        try:
            profile = user.profile
            if not user.is_superuser and profile.role != 'admin':
                print("     * Eliminar: ✅ Visible (no es superusuario ni admin)")
            else:
                print("     * Eliminar: ❌ Oculto (es superusuario o admin)")
        except UserProfile.DoesNotExist:
            print("     * Eliminar: ❌ Oculto (sin perfil)")
        
        print("-" * 50)

if __name__ == '__main__':
    debug_users()