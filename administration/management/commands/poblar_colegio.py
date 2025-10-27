"""
Management command para poblar el Colegio La Balsa
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from academics_extended.models import *
from authentication.models import UserProfile
from communications.models import Announcement
from datetime import date, time
import random

class Command(BaseCommand):
    help = 'Poblar datos del Colegio La Balsa'

    def handle(self, *args, **options):
        self.stdout.write('🏫 Creando datos del Colegio La Balsa...')
        
        with transaction.atomic():
            # 1. Actualizar administrador existente
            admin = User.objects.get(username='admin')
            admin.first_name = 'Administrador'
            admin.last_name = 'Colegio La Balsa'
            admin.save()
            
            admin_profile, created = UserProfile.objects.get_or_create(
                user=admin,
                defaults={'role': 'admin', 'phone': '3001234567'}
            )
            self.stdout.write('✅ Administrador configurado')
            
            # 2. Crear secretario
            secretario, created = User.objects.get_or_create(
                username='secretario',
                defaults={
                    'email': 'secretario@colegiolabalsa.edu.co',
                    'first_name': 'María Elena',
                    'last_name': 'García Rodríguez'
                }
            )
            if created:
                secretario.set_password('secretario123')
                secretario.save()
            
            UserProfile.objects.get_or_create(
                user=secretario,
                defaults={'role': 'secretary', 'phone': '3007654321'}
            )
            self.stdout.write('✅ Secretario creado')
            
            # 3. Crear profesores
            profesores_nombres = [
                ('Carlos Alberto', 'García Pérez'),
                ('Ana Sofía', 'Rodríguez López'),
                ('Luis Miguel', 'González Martínez'),
                ('Diana Carolina', 'Hernández Silva'),
                ('Jorge Luis', 'López Torres'),
                ('Sandra Milena', 'Martínez Flores'),
                ('Fernando', 'Pérez Rivera'),
                ('Patricia Rosa', 'Sánchez Gómez'),
                ('Alejandro', 'Ramírez Díaz'),
                ('Claudia Patricia', 'Torres Cruz'),
                ('Miguel Ángel', 'Flores Morales'),
                ('Gloria Patricia', 'Rivera Jiménez'),
                ('Ricardo', 'Gómez Ruiz'),
                ('Liliana', 'Díaz Vargas'),
                ('Santiago', 'Cruz Castillo')
            ]
            
            profesores = []
            for i, (nombre, apellido) in enumerate(profesores_nombres):
                username = f'profesor{i+1:02d}'
                profesor, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': f'{username}@colegiolabalsa.edu.co',
                        'first_name': nombre,
                        'last_name': apellido
                    }
                )
                if created:
                    profesor.set_password('profesor123')
                    profesor.save()
                
                profile, _ = UserProfile.objects.get_or_create(
                    user=profesor,
                    defaults={'role': 'teacher', 'phone': f'30{random.randint(1000000, 9999999)}'}
                )
                profesores.append(profile)
            
            self.stdout.write(f'✅ {len(profesores)} profesores creados')
            
            # 4. Crear año académico
            year_2025, created = AcademicYear.objects.get_or_create(
                name='2025',
                defaults={
                    'start_date': date(2025, 2, 1),
                    'end_date': date(2025, 11, 30),
                    'is_current': True
                }
            )
            self.stdout.write('✅ Año académico 2025 creado')
            
            # 5. Crear grados y cursos
            grados = []
            cursos = []
            
            for num in range(1, 12):
                nivel = 'Primaria' if num <= 5 else 'Secundaria'
                grado, created = Grade.objects.get_or_create(
                    name=f'{num}°',
                    defaults={'level': nivel, 'order': num}
                )
                grados.append(grado)
                
                for seccion in ['A', 'B']:
                    curso, created = Course.objects.get_or_create(
                        grade=grado,
                        section=seccion,
                        defaults={'academic_year': year_2025, 'max_students': 25}
                    )
                    cursos.append(curso)
            
            self.stdout.write(f'✅ {len(grados)} grados y {len(cursos)} cursos creados')
            
            # 6. Crear materias
            materias_data = {
                'primaria_basica': ['Lengua Castellana', 'Matemáticas', 'Ciencias Naturales', 'Ciencias Sociales', 'Inglés', 'Educación Física', 'Ética y Valores', 'Educación Religiosa', 'Educación Artística'],
                'primaria_superior': ['Tecnología e Informática'],
                'secundaria': ['Lengua Castellana y Literatura', 'Álgebra', 'Geometría', 'Biología', 'Química', 'Física', 'Historia', 'Geografía', 'Constitución Política', 'Educación Física', 'Educación Artística', 'Ética y Religión', 'Tecnología e Informática', 'Filosofía']
            }
            
            todas_materias = set()
            for materias_list in materias_data.values():
                todas_materias.update(materias_list)
            
            materias_obj = []
            for materia_name in todas_materias:
                # Determinar área según la materia
                if 'Matemáticas' in materia_name or 'Álgebra' in materia_name or 'Geometría' in materia_name:
                    area = 'matematicas'
                elif 'Ciencias Naturales' in materia_name or 'Biología' in materia_name or 'Química' in materia_name or 'Física' in materia_name:
                    area = 'ciencias'
                elif 'Ciencias Sociales' in materia_name or 'Historia' in materia_name or 'Geografía' in materia_name or 'Constitución' in materia_name:
                    area = 'sociales'
                elif 'Lengua Castellana' in materia_name or 'Literatura' in materia_name:
                    area = 'lenguaje'
                elif 'Inglés' in materia_name:
                    area = 'ingles'
                elif 'Educación Física' in materia_name:
                    area = 'educacion_fisica'
                elif 'Educación Artística' in materia_name or 'Artística' in materia_name:
                    area = 'artes'
                elif 'Tecnología' in materia_name or 'Informática' in materia_name:
                    area = 'informatica'
                elif 'Religión' in materia_name or 'Religiosa' in materia_name:
                    area = 'religion'
                elif 'Ética' in materia_name or 'Valores' in materia_name or 'Filosofía' in materia_name:
                    area = 'etica'
                else:
                    area = 'sociales'  # Default
                
                materia, created = Subject.objects.get_or_create(
                    name=materia_name,
                    defaults={
                        'code': materia_name[:3].upper(),
                        'area': area,
                        'hours_per_week': 3,
                        'description': f'Materia {materia_name} - Colegio La Balsa'
                    }
                )
                materias_obj.append(materia)
            
            self.stdout.write(f'✅ {len(materias_obj)} materias creadas')
            
            # 7. Crear algunos estudiantes de muestra
            nombres_estudiantes = ['Juan Carlos', 'María Elena', 'Luis Miguel', 'Ana Sofía', 'Santiago', 'Valentina', 'Sebastián', 'Isabella', 'Daniel', 'Camila']
            apellidos = ['García', 'Rodríguez', 'González', 'Hernández', 'López', 'Martínez', 'Pérez', 'Sánchez']
            
            estudiantes_total = 0
            
            # Solo crear estudiantes para algunos cursos como muestra
            for curso in cursos[:6]:  # Primeros 6 cursos
                num_estudiantes = random.randint(8, 12)
                
                for i in range(num_estudiantes):
                    nombre = random.choice(nombres_estudiantes)
                    apellido1 = random.choice(apellidos)
                    apellido2 = random.choice(apellidos)
                    username = f'est{curso.grade.order:02d}{curso.section.lower()}{i+1:02d}'
                    
                    estudiante, created = User.objects.get_or_create(
                        username=username,
                        defaults={
                            'email': f'{username}@estudiantes.colegiolabalsa.edu.co',
                            'first_name': nombre,
                            'last_name': f'{apellido1} {apellido2}'
                        }
                    )
                    if created:
                        estudiante.set_password('estudiante123')
                        estudiante.save()
                    
                    profile, _ = UserProfile.objects.get_or_create(
                        user=estudiante,
                        defaults={'role': 'student', 'phone': f'31{random.randint(1000000, 9999999)}'}
                    )
                    
                    edad = 5 + curso.grade.order
                    fecha_nac = date(2025 - edad, random.randint(1, 12), random.randint(1, 28))
                    
                    student, created = Student.objects.get_or_create(
                        user=estudiante,
                        defaults={
                            'student_id': f'2025{curso.grade.order:02d}{curso.section}{i+1:03d}',
                            'course': curso,
                            'date_of_birth': fecha_nac,
                            'gender': random.choice(['M', 'F']),
                            'emergency_contact': f'Padre/Madre de {nombre}',
                            'emergency_phone': f'32{random.randint(1000000, 9999999)}'
                        }
                    )
                    estudiantes_total += 1
                
                self.stdout.write(f'✅ Curso {curso.grade.name}-{curso.section}: {num_estudiantes} estudiantes')
            
            # 8. Crear anuncio de bienvenida
            Announcement.objects.get_or_create(
                title='¡Bienvenidos al Colegio La Balsa!',
                defaults={
                    'content': '''¡Bienvenidos al sistema académico del Colegio La Balsa!
                    
CREDENCIALES DE ACCESO:
👑 Administrador: admin / admin123
👩‍💼 Secretario: secretario / secretario123
👨‍🏫 Profesores: profesor01-15 / profesor123
🎓 Estudiantes: estudiante123

El colegio atiende grados de 1° a 11° con dos secciones (A y B) por grado.
Horarios: 6:30 AM - 12:30 PM con descanso de 9:00 a 9:30 AM.

¡Gracias por ser parte de nuestra comunidad educativa!''',
                    'author': admin,
                    'priority': 'high',
                    'is_active': True
                }
            )
            
            self.stdout.write('📢 Anuncio de bienvenida creado')
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'''
🎉 ¡COLEGIO LA BALSA CONFIGURADO EXITOSAMENTE!
=====================================
👤 Total usuarios: {User.objects.count()}
🎓 Estudiantes muestra: {estudiantes_total}
👨‍🏫 Profesores: {len(profesores)}
🏫 Grados: {len(grados)} (1° a 11°)
📚 Cursos: {len(cursos)} (2 secciones por grado)
📖 Materias: {len(materias_obj)}

CREDENCIALES:
admin / admin123 (Administrador)
secretario / secretario123 (Secretario)
profesor01-15 / profesor123 (Profesores)
est[grado][seccion][num] / estudiante123 (Estudiantes)
=====================================
                    '''
                )
            )