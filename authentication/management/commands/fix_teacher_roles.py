from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from authentication.models import UserProfile

class Command(BaseCommand):
    help = 'Corregir los roles de los profesores'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== CORRIGIENDO ROLES DE PROFESORES ==='))
        
        # Usuarios que deben ser profesores
        teachers = ['maria.rodriguez', 'carlos.martinez', 'ana.lopez']
        
        for username in teachers:
            try:
                user = User.objects.get(username=username)
                if hasattr(user, 'profile'):
                    old_role = user.profile.role
                    user.profile.role = 'teacher'
                    user.profile.save()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✅ {username}: {old_role} → teacher'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f'❌ {username}: No tiene perfil')
                    )
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'❌ {username}: Usuario no encontrado')
                )
        
        self.stdout.write(self.style.SUCCESS('\n=== CORRECCIÓN COMPLETADA ==='))