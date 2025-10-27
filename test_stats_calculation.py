import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')
django.setup()

from django.contrib.auth.models import User
from authentication.models import UserProfile

print("=== Probando cálculo de estadísticas ===")

try:
    # Obtener todas las estadísticas manualmente
    total_users = User.objects.count()
    complete_profiles = UserProfile.objects.filter(is_profile_complete=True).count()
    with_avatars = UserProfile.objects.exclude(avatar='').count()
    
    print(f"📊 Total usuarios: {total_users}")
    print(f"✅ Perfiles completos: {complete_profiles}")
    print(f"📸 Con avatar: {with_avatars}")
    
    # Calcular completitud promedio
    all_profiles = UserProfile.objects.all()
    if all_profiles.exists():
        total_completion = sum(profile.profile_completion_percentage for profile in all_profiles)
        avg_completion = total_completion / all_profiles.count()
        print(f"📈 Completitud promedio: {avg_completion:.1f}%")
    else:
        print("⚠️ No hay perfiles para calcular promedio")
    
    # Estadísticas por rol
    print("\n📋 Estadísticas por rol:")
    for role_code, role_name in UserProfile.ROLE_CHOICES:
        role_profiles = UserProfile.objects.filter(role=role_code)
        if role_profiles.exists():
            print(f"  🎭 {role_name}: {role_profiles.count()} usuarios")
            complete_count = role_profiles.filter(is_profile_complete=True).count()
            print(f"      ✅ Completos: {complete_count}")
    
    print("\n✅ Cálculo de estadísticas exitoso!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()