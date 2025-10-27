from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from authentication.models import UserProfile

class Command(BaseCommand):
    help = 'Crear usuarios de profesores para pruebas'

    def handle(self, *args, **options):
        profesores = [
            {
                'username': 'profesor_maria',
                'email': 'maria.garcia@labalsa.edu.co',
                'first_name': 'María',
                'last_name': 'García'
            },
            {
                'username': 'profesor_carlos',
                'email': 'carlos.lopez@labalsa.edu.co', 
                'first_name': 'Carlos',
                'last_name': 'López'
            },
            {
                'username': 'profesor_ana',
                'email': 'ana.rodriguez@labalsa.edu.co',
                'first_name': 'Ana',
                'last_name': 'Rodríguez'
            }
        ]
        
        for profesor_data in profesores:
            # Crear o actualizar usuario
            user, created = User.objects.get_or_create(
                username=profesor_data['username'],
                defaults={
                    'email': profesor_data['email'],
                    'first_name': profesor_data['first_name'],
                    'last_name': profesor_data['last_name'],
                    'is_active': True,
                }
            )
            
            # Establecer contraseña
            user.set_password('LaBalsa2024!')
            user.save()
            
            # Crear o actualizar perfil
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={'role': 'teacher'}
            )
            
            if not created:
                profile.role = 'teacher'
                profile.save()
            
            action = "Creado" if created else "Actualizado"
            self.stdout.write(
                self.style.SUCCESS(f'{action} profesor: {user.get_full_name()} ({user.username})')
            )