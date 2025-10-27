import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')
django.setup()

from django.contrib.auth.models import User

print("=== Verificando atributos de UserProfile ===")

try:
    admin_user = User.objects.get(username='admin')
    profile = admin_user.profile
    
    print(f"Usuario: {admin_user.username}")
    print(f"Atributos disponibles:")
    print(f"  - is_profile_complete: {profile.is_profile_complete}")
    print(f"  - profile_completion_percentage: {profile.profile_completion_percentage}%")
    
    # Probar método mark_profile_complete
    profile.mark_profile_complete()
    print(f"  - Después de mark_profile_complete: {profile.is_profile_complete}")
    
    print("✅ Todos los atributos funcionan correctamente")
    
except Exception as e:
    print(f"❌ Error: {e}")