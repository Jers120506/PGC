from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from academics_extended.models import (
    AcademicYear, Grade, Subject, Course, Student
)
from datetime import date, datetime


class Command(BaseCommand):
    help = 'Poblar la base de datos con datos académicos básicos para La Balsa'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🏫 Iniciando población de datos académicos para IE La Balsa...'))
        
        # 1. Crear año académico actual
        self.create_academic_year()
        
        # 2. Crear grados
        self.create_grades()
        
        # 3. Crear materias
        self.create_subjects()
        
        # 4. Crear cursos
        self.create_courses()
        
        # 5. Crear algunos estudiantes de ejemplo
        self.create_sample_students()
        
        self.stdout.write(self.style.SUCCESS('✅ ¡Población de datos académicos completada exitosamente!'))

    def create_academic_year(self):
        """Crear año académico 2025"""
        academic_year, created = AcademicYear.objects.get_or_create(
            name="2025",
            defaults={
                'start_date': date(2025, 1, 29),  # Inicio típico del año escolar en Colombia
                'end_date': date(2025, 11, 30),   # Fin típico del año escolar
                'is_current': True
            }
        )
        if created:
            self.stdout.write(f'✅ Año académico creado: {academic_year.name}')
        else:
            self.stdout.write(f'ℹ️  Año académico ya existe: {academic_year.name}')

    def create_grades(self):
        """Crear grados de primaria y bachillerato"""
        grades_data = [
            # Primaria
            {'name': '1° Primaria', 'level': 'primaria', 'order': 1},
            {'name': '2° Primaria', 'level': 'primaria', 'order': 2},
            {'name': '3° Primaria', 'level': 'primaria', 'order': 3},
            {'name': '4° Primaria', 'level': 'primaria', 'order': 4},
            {'name': '5° Primaria', 'level': 'primaria', 'order': 5},
            
            # Bachillerato
            {'name': '6° Bachillerato', 'level': 'bachillerato', 'order': 6},
            {'name': '7° Bachillerato', 'level': 'bachillerato', 'order': 7},
            {'name': '8° Bachillerato', 'level': 'bachillerato', 'order': 8},
            {'name': '9° Bachillerato', 'level': 'bachillerato', 'order': 9},
            {'name': '10° Bachillerato', 'level': 'bachillerato', 'order': 10},
            {'name': '11° Bachillerato', 'level': 'bachillerato', 'order': 11},
        ]
        
        for grade_data in grades_data:
            grade, created = Grade.objects.get_or_create(
                name=grade_data['name'],
                defaults=grade_data
            )
            if created:
                self.stdout.write(f'✅ Grado creado: {grade.name}')

    def create_subjects(self):
        """Crear materias básicas del currículo colombiano"""
        subjects_data = [
            # Matemáticas
            {'name': 'Matemáticas', 'code': 'MAT', 'area': 'matematicas', 'hours_per_week': 5},
            {'name': 'Geometría', 'code': 'GEO', 'area': 'matematicas', 'hours_per_week': 2},
            {'name': 'Estadística', 'code': 'EST', 'area': 'matematicas', 'hours_per_week': 2},
            
            # Ciencias
            {'name': 'Ciencias Naturales', 'code': 'CN', 'area': 'ciencias', 'hours_per_week': 4},
            {'name': 'Biología', 'code': 'BIO', 'area': 'ciencias', 'hours_per_week': 3},
            {'name': 'Química', 'code': 'QUI', 'area': 'ciencias', 'hours_per_week': 3},
            {'name': 'Física', 'code': 'FIS', 'area': 'ciencias', 'hours_per_week': 3},
            
            # Ciencias Sociales
            {'name': 'Ciencias Sociales', 'code': 'CS', 'area': 'sociales', 'hours_per_week': 4},
            {'name': 'Historia', 'code': 'HIS', 'area': 'sociales', 'hours_per_week': 2},
            {'name': 'Geografía', 'code': 'GEO', 'area': 'sociales', 'hours_per_week': 2},
            
            # Lenguaje
            {'name': 'Lenguaje', 'code': 'LEN', 'area': 'lenguaje', 'hours_per_week': 5},
            {'name': 'Literatura', 'code': 'LIT', 'area': 'lenguaje', 'hours_per_week': 2},
            
            # Otros
            {'name': 'Inglés', 'code': 'ING', 'area': 'ingles', 'hours_per_week': 3},
            {'name': 'Educación Física', 'code': 'EF', 'area': 'educacion_fisica', 'hours_per_week': 2},
            {'name': 'Artes', 'code': 'ART', 'area': 'artes', 'hours_per_week': 2},
            {'name': 'Informática', 'code': 'INF', 'area': 'informatica', 'hours_per_week': 2},
            {'name': 'Religión', 'code': 'REL', 'area': 'religion', 'hours_per_week': 1},
            {'name': 'Ética y Valores', 'code': 'ETI', 'area': 'etica', 'hours_per_week': 1},
        ]
        
        for subject_data in subjects_data:
            subject, created = Subject.objects.get_or_create(
                code=subject_data['code'],
                defaults=subject_data
            )
            if created:
                self.stdout.write(f'✅ Materia creada: {subject.name} ({subject.code})')

    def create_courses(self):
        """Crear cursos para el año académico actual"""
        academic_year = AcademicYear.objects.get(is_current=True)
        grades = Grade.objects.all()
        sections = ['A', 'B']  # Empezamos con 2 secciones por grado
        
        for grade in grades:
            for section in sections:
                course, created = Course.objects.get_or_create(
                    grade=grade,
                    section=section,
                    academic_year=academic_year,
                    defaults={
                        'max_students': 35
                    }
                )
                if created:
                    self.stdout.write(f'✅ Curso creado: {course}')

    def create_sample_students(self):
        """Crear algunos estudiantes de ejemplo"""
        # Obtener cursos de primeros grados para ejemplo
        primary_courses = Course.objects.filter(
            grade__level='primaria',
            grade__order__in=[1, 2, 3]
        )[:3]
        
        students_data = [
            {
                'username': 'estudiante_ana',
                'first_name': 'Ana María',
                'last_name': 'García López',
                'email': 'ana.garcia@estudiante.labalsa.edu.co',
                'student_id': '2025001',
                'guardian_name': 'Carlos García',
                'guardian_phone': '3001234567',
                'address': 'Calle 15 #23-45, La Balsa',
                'birth_date': date(2015, 3, 15),
            },
            {
                'username': 'estudiante_luis',
                'first_name': 'Luis Fernando',
                'last_name': 'Rodríguez Mesa',
                'email': 'luis.rodriguez@estudiante.labalsa.edu.co',
                'student_id': '2025002',
                'guardian_name': 'María Mesa',
                'guardian_phone': '3002345678',
                'address': 'Carrera 8 #12-34, La Balsa',
                'birth_date': date(2014, 7, 22),
            },
            {
                'username': 'estudiante_sofia',
                'first_name': 'Sofía',
                'last_name': 'Martínez Peña',
                'email': 'sofia.martinez@estudiante.labalsa.edu.co',
                'student_id': '2025003',
                'guardian_name': 'Jorge Martínez',
                'guardian_phone': '3003456789',
                'address': 'Avenida Principal #45-67, La Balsa',
                'birth_date': date(2015, 11, 8),
            },
        ]
        
        for i, student_data in enumerate(students_data):
            if i < len(primary_courses):
                course = primary_courses[i]
                
                # Crear usuario
                user, user_created = User.objects.get_or_create(
                    username=student_data['username'],
                    defaults={
                        'first_name': student_data['first_name'],
                        'last_name': student_data['last_name'],
                        'email': student_data['email'],
                        'is_active': True,
                    }
                )
                
                if user_created:
                    user.set_password('estudiante123')  # Contraseña temporal
                    user.save()
                    
                    # Configurar perfil como estudiante
                    user.profile.role = 'student'
                    user.profile.save()
                    
                    # Crear perfil extendido de estudiante
                    student, student_created = Student.objects.get_or_create(
                        user=user,
                        defaults={
                            'student_id': student_data['student_id'],
                            'course': course,
                            'enrollment_date': date(2025, 1, 29),
                            'guardian_name': student_data['guardian_name'],
                            'guardian_phone': student_data['guardian_phone'],
                            'guardian_email': '',
                            'address': student_data['address'],
                            'birth_date': student_data['birth_date'],
                            'status': 'active',
                        }
                    )
                    
                    if student_created:
                        self.stdout.write(f'✅ Estudiante creado: {student.user.get_full_name()} - {student.student_id} ({course})')
                else:
                    self.stdout.write(f'ℹ️  Usuario estudiante ya existe: {user.username}')