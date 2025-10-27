import os
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')
django.setup()

from django.contrib.auth.models import User
from authentication.models import UserProfile

print("=== Probando actualización de perfiles ===")

# Obtener usuario admin
admin_user = User.objects.get(username='admin')
profile = admin_user.profile

print(f"Usuario: {admin_user.username}")
print(f"Perfil antes - Teléfono: {profile.phone}")

# Actualizar teléfono
profile.phone = "3001234567"
profile.save()

print(f"Perfil después - Teléfono: {profile.phone}")
print("✅ Actualización manual exitosa")

# Verificar completitud
print(f"Completitud: {profile.profile_completion_percentage}%")