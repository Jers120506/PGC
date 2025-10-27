"""
Comando para poblar la base de datos con datos de prueba
Sistema offline para Institución Educativa La Balsa - Córdoba
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
import random

from authentication.models import UserProfile
from academics.models import (
    AcademicYear, AcademicPeriod, Grade, Subject, Course, 
    SubjectAssignment, Student, GradeRecord, Attendance, BehaviorRecord
)
from communications.models import Announcement

class Command(BaseCommand):
    help = 'Pobla la base de datos con datos de prueba para La Balsa'

    def handle(self, *args, **options):
        self.stdout.write("🔄 Creando datos de prueba para Institución Educativa La Balsa...")
        
        # 1. Crear año académico
        academic_year, created = AcademicYear.objects.get_or_create(
            name='2025',
            defaults={
                'start_date': date(2025, 1, 20),
                'end_date': date(2025, 11, 30),
                'is_current': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"✅ Año académico: {academic_year.name}"))
        
        # 2. Crear períodos académicos
        periods_data = [
            {'name': 'Primer Período', 'number': 1, 'start': date(2025, 1, 20), 'end': date(2025, 3, 28), 'is_current': True},
            {'name': 'Segundo Período', 'number': 2, 'start': date(2025, 4, 1), 'end': date(2025, 6, 6), 'is_current': False},
            {'name': 'Tercer Período', 'number': 3, 'start': date(2025, 6, 16), 'end': date(2025, 8, 24), 'is_current': False},
            {'name': 'Cuarto Período', 'number': 4, 'start': date(2025, 9, 1), 'end': date(2025, 11, 30), 'is_current': False},
        ]
        
        for period_data in periods_data:
            period, created = AcademicPeriod.objects.get_or_create(
                academic_year=academic_year,
                number=period_data['number'],
                defaults={
                    'name': period_data['name'],
                    'start_date': period_data['start'],
                    'end_date': period_data['end'],
                    'is_current': period_data['is_current']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"✅ Período: {period.name}"))
        
        # 3. Crear grados
        grades_data = [
            {'name': 'Transición', 'order': 1, 'level': 'primaria', 'numeric_grade': 0},
            {'name': '1° Primaria', 'order': 2, 'level': 'primaria', 'numeric_grade': 1},
            {'name': '2° Primaria', 'order': 3, 'level': 'primaria', 'numeric_grade': 2},
            {'name': '3° Primaria', 'order': 4, 'level': 'primaria', 'numeric_grade': 3},
            {'name': '4° Primaria', 'order': 5, 'level': 'primaria', 'numeric_grade': 4},
            {'name': '5° Primaria', 'order': 6, 'level': 'primaria', 'numeric_grade': 5},
        ]
        
        for grade_data in grades_data:
            grade, created = Grade.objects.get_or_create(
                name=grade_data['name'],
                defaults={
                    'order': grade_data['order'],
                    'level': grade_data['level'],
                    'numeric_grade': grade_data['numeric_grade']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"✅ Grado: {grade.name}"))
        
        # 4. Crear materias
        subjects_data = [
            {'name': 'Matemáticas', 'code': 'MAT', 'area': 'matematicas', 'hours': 5},
            {'name': 'Español', 'code': 'ESP', 'area': 'lenguaje', 'hours': 5},
            {'name': 'Ciencias Naturales', 'code': 'CIEN', 'area': 'ciencias_naturales', 'hours': 4},
            {'name': 'Ciencias Sociales', 'code': 'SOC', 'area': 'ciencias_sociales', 'hours': 4},
            {'name': 'Educación Física', 'code': 'EDF', 'area': 'educacion_fisica', 'hours': 2},
            {'name': 'Inglés', 'code': 'ING', 'area': 'ingles', 'hours': 3},
        ]
        
        for subject_data in subjects_data:
            subject, created = Subject.objects.get_or_create(
                code=subject_data['code'],
                defaults={
                    'name': subject_data['name'],
                    'area': subject_data['area'],
                    'hours_per_week': subject_data['hours']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"✅ Materia: {subject.name}"))
        
        # 5. Crear profesores
        teachers_data = [
            {'username': 'maria.rodriguez', 'first_name': 'María', 'last_name': 'Rodríguez', 'email': 'maria.rodriguez@labalsa.edu.co'},
            {'username': 'carlos.martinez', 'first_name': 'Carlos', 'last_name': 'Martínez', 'email': 'carlos.martinez@labalsa.edu.co'},
            {'username': 'ana.lopez', 'first_name': 'Ana', 'last_name': 'López', 'email': 'ana.lopez@labalsa.edu.co'},
        ]
        
        teachers = []
        for teacher_data in teachers_data:
            user, created = User.objects.get_or_create(
                username=teacher_data['username'],
                defaults={
                    'first_name': teacher_data['first_name'],
                    'last_name': teacher_data['last_name'],
                    'email': teacher_data['email'],
                    'is_active': True
                }
            )
            if created:
                user.set_password('profesor123')
                user.save()
                
                # Crear perfil de profesor
                profile, created = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'role': 'teacher',
                        'phone': f'300555{1000 + len(teachers)}',
                        'employee_id': f'PROF{1000 + len(teachers)}'
                    }
                )
                self.stdout.write(self.style.SUCCESS(f"✅ Profesor: {user.get_full_name()}"))
            
            teachers.append(user)
        
        # 6. Crear cursos
        target_grades = Grade.objects.all()
        courses_created = []
        
        for grade in target_grades:
            homeroom_teacher = teachers[len(courses_created) % len(teachers)]
            
            course, created = Course.objects.get_or_create(
                grade=grade,
                section='A',
                academic_year=academic_year,
                defaults={
                    'homeroom_teacher': homeroom_teacher,
                    'max_students': 20,
                    'is_active': True
                }
            )
            
            if created:
                courses_created.append(course)
                self.stdout.write(self.style.SUCCESS(f"✅ Curso: {course.full_name} - Docente: {homeroom_teacher.get_full_name()}"))
        
        # 7. Crear estudiantes (4 por curso)
        student_names = [
            ('Sofía', 'Hernández'), ('Miguel', 'Torres'), ('Isabella', 'Ramírez'), ('Diego', 'Morales'),
            ('Camila', 'Vargas'), ('Sebastián', 'Castillo'), ('Valeria', 'Jiménez'), ('Alejandro', 'Ruiz'),
            ('Emma', 'Delgado'), ('Mateo', 'Ortega'), ('Lucía', 'Mendoza'), ('Nicolás', 'Cruz'),
            ('Gabriela', 'Flores'), ('Daniel', 'Reyes'), ('Martina', 'Aguilar'), ('Samuel', 'Vega'),
            ('Paula', 'Castro'), ('Andrés', 'Silva'), ('Carolina', 'Moreno'), ('Felipe', 'Ramos'),
            ('Valentina', 'Ospina'), ('Santiago', 'Herrera'), ('Mariana', 'Gómez'), ('Tomás', 'Pineda')
        ]
        
        student_count = 1
        name_index = 0
        
        for course in courses_created:
            for i in range(4):  # 4 estudiantes por curso
                if name_index < len(student_names):
                    first_name, last_name = student_names[name_index]
                    name_index += 1
                    
                    # Crear usuario para el estudiante
                    username = f"{first_name.lower()}.{last_name.lower()}"
                    user, created = User.objects.get_or_create(
                        username=username,
                        defaults={
                            'first_name': first_name,
                            'last_name': last_name,
                            'email': f"{username}@estudiante.labalsa.edu.co",
                            'is_active': True
                        }
                    )
                    
                    if created:
                        user.set_password('estudiante123')
                        user.save()
                        
                        # Crear perfil de estudiante
                        profile, created = UserProfile.objects.get_or_create(
                            user=user,
                            defaults={'role': 'student'}
                        )
                    
                    # Crear estudiante
                    birth_year = 2025 - course.grade.numeric_grade - 5  # Edad aproximada
                    student, created = Student.objects.get_or_create(
                        user=user,
                        defaults={
                            'student_id': f'EST{2025}{student_count:04d}',
                            'birth_date': date(birth_year, random.randint(1, 12), random.randint(1, 28)),
                            'course': course,
                            'enrollment_date': date(2025, 1, 20),  # Inicio del año académico
                            'is_active': True
                        }
                    )
                    
                    if created:
                        student_count += 1
                        self.stdout.write(self.style.SUCCESS(f"✅ Estudiante: {student.user.get_full_name()} - {course.full_name}"))
        
        # 8. Crear asignaciones de materias
        basic_subjects = Subject.objects.filter(area__in=['matematicas', 'lenguaje', 'ciencias_naturales', 'ciencias_sociales'])[:4]
        
        for course in courses_created:
            for i, subject in enumerate(basic_subjects):
                teacher = teachers[i % len(teachers)]
                
                assignment, created = SubjectAssignment.objects.get_or_create(
                    teacher=teacher,
                    subject=subject,
                    course=course,
                    academic_year=academic_year,
                    defaults={'is_active': True}
                )
                
                if created:
                    self.stdout.write(self.style.SUCCESS(f"✅ Asignación: {teacher.get_full_name()} - {subject.name} - {course.name}"))
        
        # 9. Crear asistencia de los últimos días
        current_period = AcademicPeriod.objects.get(is_current=True)
        today = timezone.now().date()
        
        for days_back in range(5):
            attendance_date = today - timedelta(days=days_back)
            
            if attendance_date.weekday() < 5:  # Solo días de semana
                for assignment in SubjectAssignment.objects.filter(is_active=True)[:6]:  # Primeras 6 asignaciones
                    students = Student.objects.filter(course=assignment.course, is_active=True)
                    
                    for student in students:
                        status = 'present' if random.random() > 0.15 else 'absent'  # 85% presentes
                        
                        Attendance.objects.get_or_create(
                            student=student,
                            course=assignment.course,
                            subject=assignment.subject,
                            teacher=assignment.teacher,
                            date=attendance_date,
                            defaults={'status': status}
                        )
        
        self.stdout.write(self.style.SUCCESS("✅ Registros de asistencia creados"))
        
        # 10. Crear calificaciones
        for assignment in SubjectAssignment.objects.filter(is_active=True)[:6]:
            students = Student.objects.filter(course=assignment.course, is_active=True)
            
            activities = [
                {'name': 'Quiz 1', 'type': 'quiz'},
                {'name': 'Taller', 'type': 'workshop'}
            ]
            
            for activity in activities:
                for student in students:
                    grade_value = round(random.uniform(3.0, 5.0), 1)
                    
                    GradeRecord.objects.get_or_create(
                        student=student,
                        subject=assignment.subject,
                        course=assignment.course,
                        teacher=assignment.teacher,
                        period=current_period,
                        activity_name=activity['name'],
                        activity_type=activity['type'],
                        defaults={
                            'grade_value': Decimal(str(grade_value)),
                            'date_recorded': today - timedelta(days=random.randint(1, 10))
                        }
                    )
        
        self.stdout.write(self.style.SUCCESS("✅ Calificaciones creadas"))
        
        # 11. Crear anuncio
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = teachers[0]  # Usar primer profesor como autor
        
        Announcement.objects.get_or_create(
            title="Bienvenidos al Sistema Académico La Balsa",
            defaults={
                'content': "Sistema offline para gestión académica. Aquí pueden registrar asistencia, calificaciones y comunicaciones internas.",
                'created_by': admin_user,
                'target_audience': 'all',
                'priority': 'high',
                'is_active': True,
                'active_from': timezone.now(),
                'active_until': timezone.now() + timedelta(days=30)
            }
        )
        
        self.stdout.write(self.style.SUCCESS("✅ Anuncio creado"))
        
        # Resumen final
        self.stdout.write(self.style.SUCCESS("\n🎉 ¡Datos de prueba creados exitosamente!"))
        self.stdout.write("\n📋 CREDENCIALES DE ACCESO:")
        self.stdout.write("=" * 50)
        self.stdout.write("👨‍🏫 PROFESORES:")
        for teacher in teachers:
            self.stdout.write(f"   Usuario: {teacher.username}")
            self.stdout.write(f"   Contraseña: profesor123")
            self.stdout.write(f"   Nombre: {teacher.get_full_name()}\n")
        
        self.stdout.write("🔗 ACCESOS:")
        self.stdout.write(f"   Dashboard Docente: http://127.0.0.1:8000/academics/teacher/dashboard/")
        self.stdout.write(f"   Admin Django: http://127.0.0.1:8000/admin/")
        
        self.stdout.write("\n📊 ESTADÍSTICAS:")
        self.stdout.write(f"   👥 Estudiantes: {Student.objects.count()}")
        self.stdout.write(f"   👨‍🏫 Profesores: {User.objects.filter(profile__role='teacher').count()}")
        self.stdout.write(f"   📚 Cursos: {Course.objects.count()}")
        self.stdout.write(f"   📖 Materias: {Subject.objects.count()}")
        self.stdout.write(f"   ✅ Asistencias: {Attendance.objects.count()}")
        self.stdout.write(f"   📝 Calificaciones: {GradeRecord.objects.count()}")