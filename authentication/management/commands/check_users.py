from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from authentication.models import UserProfile

class Command(BaseCommand):
    help = 'Verificar y mostrar información de usuarios'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== VERIFICACIÓN DE USUARIOS ==='))
        
        users = User.objects.all()
        for user in users:
            self.stdout.write(f"\nUsuario: {user.username}")
            self.stdout.write(f"Nombre: {user.first_name} {user.last_name}")
            self.stdout.write(f"Email: {user.email}")
            
            if hasattr(user, 'profile'):
                self.stdout.write(f"Rol: {user.profile.role}")
                self.stdout.write(f"Perfil ID: {user.profile.id}")
            else:
                self.stdout.write(self.style.ERROR("¡NO TIENE PERFIL!"))
                # Crear perfil si no existe
                profile = UserProfile.objects.create(user=user, role='student')
                self.stdout.write(self.style.WARNING(f"Perfil creado como estudiante: {profile.id}"))
            
            self.stdout.write("-" * 40)
        
        self.stdout.write(self.style.SUCCESS('\n=== VERIFICACIÓN COMPLETADA ==='))