#!/usr/bin/env python

from django.contrib.auth.models import User
from authentication.models import UserProfile

# Usuarios específicos a corregir
usuarios_a_corregir = {
    'luis': 'teacher',
    'angel': 'teacher', 
    'profesor_nuevo': 'teacher',
    'profesor_test': 'teacher'
}

print("CORRIGIENDO ROLES DE USUARIOS ESPECÍFICOS")
print("=" * 45)

for username, rol_correcto in usuarios_a_corregir.items():
    try:
        user = User.objects.get(username=username)
        if hasattr(user, 'profile'):
            rol_anterior = user.profile.role
            user.profile.role = rol_correcto
            user.profile.save()
            
            if rol_anterior == 'student':
                print(f"✅ {username}: {rol_anterior} → {rol_correcto}")
            else:
                print(f"ℹ️ {username}: ya tenía rol {rol_anterior}")
        else:
            print(f"⚠️ {username}: sin perfil")
    except User.DoesNotExist:
        print(f"❌ {username}: no existe")

print("\n📊 ESTADÍSTICAS FINALES:")
print(f"- Administradores: {User.objects.filter(profile__role='admin').count()}")
print(f"- Secretarios: {User.objects.filter(profile__role='secretary').count()}")
print(f"- Profesores: {User.objects.filter(profile__role='teacher').count()}")
print(f"- Estudiantes: {User.objects.filter(profile__role='student').count()}")

print("\n✅ Corrección completada")