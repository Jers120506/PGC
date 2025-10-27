"""
Comando simple para crear datos básicos del Colegio La Balsa
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from academics_extended.models import *
from authentication.models import UserProfile
from communications.models import Announcement
from datetime import date
import random

class Command(BaseCommand):
    help = 'Crear datos básicos del Colegio La Balsa'

    def handle(self, *args, **options):
        self.stdout.write('🏫 Creando datos básicos del Colegio La Balsa...')
        
        try:
            with transaction.atomic():
                # 1. Crear usuarios básicos adicionales
                self.crear_usuarios_basicos()
                
                # 2. Crear estructura académica básica
                self.crear_estructura_basica()
                
                # 3. Crear estudiantes de muestra
                self.crear_estudiantes_muestra()
                
                # 4. Crear anuncio
                self.crear_anuncio_bienvenida()
                
                self.mostrar_resumen_final()
                
        except Exception as e:
            self.stdout.write(f"❌ Error: {e}")
            
    def crear_usuarios_basicos(self):
        """Crear usuarios básicos adicionales"""
        # Secretario
        if not User.objects.filter(username='secretario').exists():
            secretario = User.objects.create_user(
                username='secretario',
                email='secretario@colegiolabalsa.edu.co',
                password='secretario123',
                first_name='María Elena',
                last_name='García Rodríguez'
            )
            UserProfile.objects.create(
                user=secretario,
                role='secretary',
                phone='3007654321'
            )
            self.stdout.write('✅ Secretario creado')
        
        # Profesor de muestra
        if not User.objects.filter(username='profesor01').exists():
            profesor = User.objects.create_user(
                username='profesor01',
                email='profesor01@colegiolabalsa.edu.co',
                password='profesor123',
                first_name='Carlos Alberto',
                last_name='García Pérez'
            )
            UserProfile.objects.create(
                user=profesor,
                role='teacher',
                phone='3001111111'
            )
            self.stdout.write('✅ Profesor de muestra creado')
            
    def crear_estructura_basica(self):
        """Crear estructura académica básica"""
        # Año académico
        year_2025, created = AcademicYear.objects.get_or_create(
            name='2025',
            defaults={
                'start_date': date(2025, 2, 1),
                'end_date': date(2025, 11, 30),
                'is_current': True
            }
        )
        
        # Crear algunos grados de muestra
        grados_muestra = [
            ('1°', 'Primaria', 1),
            ('2°', 'Primaria', 2),
            ('5°', 'Primaria', 5),
            ('6°', 'Bachillerato', 6),
            ('11°', 'Bachillerato', 11),
        ]
        
        for nombre, nivel, orden in grados_muestra:
            grado, created = Grade.objects.get_or_create(
                name=nombre,
                defaults={'level': nivel.lower(), 'order': orden}
            )
            
            # Crear secciones A y B para cada grado
            for seccion in ['A', 'B']:
                Course.objects.get_or_create(
                    grade=grado,
                    section=seccion,
                    defaults={'academic_year': year_2025, 'max_students': 25}
                )
        
        # Crear algunas materias básicas
        materias_basicas = [
            ('Lengua Castellana', 'LCA', 'lenguaje'),
            ('Matemáticas', 'MAT', 'matematicas'),
            ('Ciencias Naturales', 'CNT', 'ciencias'),
            ('Ciencias Sociales', 'CSO', 'sociales'),
            ('Inglés', 'ING', 'ingles'),
            ('Educación Física', 'EDF', 'educacion_fisica'),
        ]
        
        for nombre, codigo, area in materias_basicas:
            Subject.objects.get_or_create(
                name=nombre,
                defaults={
                    'code': codigo,
                    'area': area,
                    'hours_per_week': 4,
                    'description': f'{nombre} - Colegio La Balsa'
                }
            )
            
        self.stdout.write('✅ Estructura académica básica creada')
        
    def crear_estudiantes_muestra(self):
        """Crear algunos estudiantes de muestra"""
        nombres = ['Juan Carlos', 'María Elena', 'Luis Miguel', 'Ana Sofía', 'Santiago']
        apellidos = ['García López', 'Rodríguez Pérez', 'González Silva', 'Hernández Torres']
        
        # Solo crear para el primer curso encontrado
        primer_curso = Course.objects.first()
        if primer_curso:
            for i, nombre in enumerate(nombres):
                apellido = random.choice(apellidos)
                username = f'est{primer_curso.grade.order:02d}{primer_curso.section.lower()}{i+1:02d}'
                
                if not User.objects.filter(username=username).exists():
                    estudiante = User.objects.create_user(
                        username=username,
                        email=f'{username}@estudiantes.colegiolabalsa.edu.co',
                        password='estudiante123',
                        first_name=nombre,
                        last_name=apellido
                    )
                    
                    UserProfile.objects.create(
                        user=estudiante,
                        role='student',
                        phone=f'31{random.randint(1000000, 9999999)}'
                    )
                    
                    Student.objects.create(
                        user=estudiante,
                        student_id=f'2025{primer_curso.grade.order:02d}{primer_curso.section}{i+1:03d}',
                        course=primer_curso,
                        date_of_birth=date(2025 - (5 + primer_curso.grade.order), 6, 15),
                        gender=random.choice(['M', 'F']),
                        emergency_contact=f'Padre/Madre de {nombre}',
                        emergency_phone=f'32{random.randint(1000000, 9999999)}'
                    )
            
            self.stdout.write(f'✅ {len(nombres)} estudiantes de muestra creados para {primer_curso.grade.name}-{primer_curso.section}')
            
    def crear_anuncio_bienvenida(self):
        """Crear anuncio de bienvenida"""
        admin = User.objects.get(username='admin')
        
        Announcement.objects.get_or_create(
            title='¡Bienvenidos al Colegio La Balsa!',
            defaults={
                'content': '''¡Bienvenidos al sistema académico del Colegio La Balsa!

🏫 INFORMACIÓN DEL COLEGIO:
- Grados: 1° a 11° (Primaria y Bachillerato)
- Secciones: A y B por cada grado
- Horarios: 6:30 AM - 12:30 PM
- Descanso: 9:00 AM - 9:30 AM

🔑 CREDENCIALES DE ACCESO:
👑 Administrador: admin / admin123
👩‍💼 Secretario: secretario / secretario123
👨‍🏫 Profesor: profesor01 / profesor123
🎓 Estudiantes: estudiante123

¡Gracias por ser parte de nuestra comunidad educativa!

- Dirección Colegio La Balsa''',
                'author': admin,
                'priority': 'high',
                'is_active': True
            }
        )
        self.stdout.write('📢 Anuncio de bienvenida creado')
        
    def mostrar_resumen_final(self):
        """Mostrar resumen final"""
        self.stdout.write(
            self.style.SUCCESS(
                f'''
🎉 ¡COLEGIO LA BALSA CONFIGURADO!
===============================
👤 Usuarios totales: {User.objects.count()}
🎓 Estudiantes: {Student.objects.count()}
👨‍🏫 Profesores: {UserProfile.objects.filter(role='teacher').count()}
👩‍💼 Secretarios: {UserProfile.objects.filter(role='secretary').count()}
🏫 Grados: {Grade.objects.count()}
📚 Cursos: {Course.objects.count()}
📖 Materias: {Subject.objects.count()}

🔑 CREDENCIALES PRINCIPALES:
admin / admin123 (Administrador)
secretario / secretario123 (Secretario)
profesor01 / profesor123 (Profesor)
est[XX][X][XX] / estudiante123 (Estudiantes)

🚀 Sistema listo para usar!
===============================
                '''
            )
        )