#!/usr/bin/env python
"""
Verificar y corregir roles de usuarios
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')
django.setup()

from django.contrib.auth.models import User
from authentication.models import UserProfile

def verificar_y_corregir_roles():
    print("🔍 VERIFICANDO USUARIOS Y ROLES")
    print("=" * 50)
    
    # Verificar usuarios existentes
    usuarios = User.objects.all()
    
    for usuario in usuarios:
        print(f"\n👤 Usuario: {usuario.username}")
        print(f"   Nombre: {usuario.first_name} {usuario.last_name}")
        
        # Verificar si tiene perfil
        if hasattr(usuario, 'profile'):
            perfil = usuario.profile
            print(f"   Rol actual: {perfil.role}")
            
            # Corregir rol según el username si está incorrecto
            if usuario.username == 'admin' and perfil.role != 'admin':
                print(f"   🔧 Corrigiendo rol admin...")
                perfil.role = 'admin'
                perfil.save()
                print(f"   ✅ Rol actualizado a: admin")
                
            elif usuario.username == 'secretario' and perfil.role != 'secretary':
                print(f"   🔧 Corrigiendo rol secretario...")
                perfil.role = 'secretary'
                perfil.save()
                print(f"   ✅ Rol actualizado a: secretary")
                
            elif usuario.username == 'profesor' and perfil.role != 'teacher':
                print(f"   🔧 Corrigiendo rol profesor...")
                perfil.role = 'teacher'
                perfil.save()
                print(f"   ✅ Rol actualizado a: teacher")
            else:
                print(f"   ✅ Rol correcto")
        else:
            print(f"   ❌ Sin perfil UserProfile")
            # Crear perfil según username
            if usuario.username == 'admin':
                UserProfile.objects.create(
                    user=usuario,
                    role='admin',
                    phone='320-555-0001',
                    bio='Administrador principal del colegio'
                )
                print(f"   ✅ Perfil de admin creado")
            elif usuario.username == 'secretario':
                UserProfile.objects.create(
                    user=usuario,
                    role='secretary',
                    phone='320-555-0002',
                    bio='Secretaria académica'
                )
                print(f"   ✅ Perfil de secretario creado")
            elif usuario.username == 'profesor':
                UserProfile.objects.create(
                    user=usuario,
                    role='teacher',
                    phone='320-555-0003',
                    bio='Profesor del colegio'
                )
                print(f"   ✅ Perfil de profesor creado")
    
    print("\n" + "=" * 50)
    print("🎯 RESUMEN FINAL DE ROLES:")
    for usuario in User.objects.all():
        if hasattr(usuario, 'profile'):
            print(f"   {usuario.username}: {usuario.profile.role}")
        else:
            print(f"   {usuario.username}: SIN PERFIL")

if __name__ == '__main__':
    verificar_y_corregir_roles()