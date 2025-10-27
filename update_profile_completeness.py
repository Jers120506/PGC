#!/usr/bin/env python
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')
django.setup()

from authentication.models import UserProfile

def update_profile_completeness():
    """Actualizar la completitud de todos los perfiles existentes"""
    print("=== Actualizando completitud de perfiles ===\n")
    
    profiles = UserProfile.objects.all()
    total_updated = 0
    
    for profile in profiles:
        old_completion = profile.profile_completion_percentage
        old_complete = profile.is_profile_complete
        
        # Recalcular completitud
        profile.mark_profile_complete()
        
        new_completion = profile.profile_completion_percentage
        new_complete = profile.is_profile_complete
        
        print(f"👤 {profile.user.username} ({profile.get_role_display()})")
        print(f"   Completitud: {old_completion}% → {new_completion}%")
        print(f"   Estado: {'Completo' if old_complete else 'Incompleto'} → {'Completo' if new_complete else 'Incompleto'}")
        print("-" * 50)
        
        total_updated += 1
    
    print(f"\n✅ Completitud actualizada para {total_updated} perfiles")

if __name__ == '__main__':
    update_profile_completeness()