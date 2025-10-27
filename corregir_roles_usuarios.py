#!/usr/bin/env python

from django.contrib.auth.models import User
from authentication.models import UserProfile

print("VERIFICANDO Y CORRIGIENDO ROLES DE USUARIOS")
print("=" * 50)

# Mostrar usuarios actuales
users = User.objects.select_related('profile').all()

print(f"\n📋 USUARIOS ACTUALES ({users.count()}):")
for user in users:
    if hasattr(user, 'profile'):
        role = user.profile.role
        print(f"- {user.username}: {user.first_name} {user.last_name} ({role})")
    else:
        print(f"- {user.username}: {user.first_name} {user.last_name} (SIN PERFIL)")

# Identificar usuarios con rol 'student' que deberían tener otro rol
usuarios_student = User.objects.filter(profile__role='student').exclude(username__in=['admin', 'secretario', 'profesor'])

if usuarios_student.exists():
    print(f"\n🔍 USUARIOS CON ROL 'STUDENT' QUE PUEDEN NECESITAR CORRECCIÓN:")
    for user in usuarios_student:
        print(f"- {user.username}: {user.first_name} {user.last_name}")
        
        # Sugerir corrección basada en el nombre de usuario
        if 'profesor' in user.username.lower() or 'teacher' in user.username.lower():
            user.profile.role = 'teacher'
            user.profile.save()
            print(f"  ✅ Corregido a 'teacher'")
        elif 'secretario' in user.username.lower() or 'secretary' in user.username.lower():
            user.profile.role = 'secretary'
            user.profile.save()
            print(f"  ✅ Corregido a 'secretary'")
        elif 'admin' in user.username.lower():
            user.profile.role = 'admin'
            user.profile.save()
            print(f"  ✅ Corregido a 'admin'")
        else:
            print(f"  ⚠️ Revisar manualmente: {user.username}")

print(f"\n📊 ESTADÍSTICAS FINALES:")
print(f"- Total usuarios: {User.objects.count()}")
print(f"- Administradores: {User.objects.filter(profile__role='admin').count()}")
print(f"- Secretarios: {User.objects.filter(profile__role='secretary').count()}")
print(f"- Profesores: {User.objects.filter(profile__role='teacher').count()}")
print(f"- Estudiantes: {User.objects.filter(profile__role='student').count()}")

print("\n✅ Verificación completada")