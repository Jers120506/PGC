#!/usr/bin/env python#!/usr/bin/env python

import os

import osimport sys

import sysimport django

import djangofrom decimal import Decimal

from datetime import date, timedelta

# Configurar Djangoimport random

sys.path.append('C:\\Users\\jbang\\OneDrive\\Desktop\\gestion de proyectos')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')# Agregar el directorio del proyecto al path

django.setup()sys.path.append(os.path.dirname(os.path.abspath(__file__)))



from academics_extended.models import Grade# Configurar Django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')

def create_sample_grades():django.setup()

    """Crear grados de ejemplo para probar"""

    from django.contrib.auth.models import User

    print("=== CREANDO GRADOS DE EJEMPLO ===")from academics_extended.models import (

        Student, Subject, GradeRecord, SubjectAssignment, AcademicYear

    # Grados de Primaria)

    primary_grades = [

        {"name": "1° Primaria", "level": "primaria", "order": 1},def create_sample_grades():

        {"name": "2° Primaria", "level": "primaria", "order": 2},    print("=== CREANDO CALIFICACIONES DE EJEMPLO ===\n")

        {"name": "3° Primaria", "level": "primaria", "order": 3},    

        {"name": "4° Primaria", "level": "primaria", "order": 4},    # Obtener año académico actual

        {"name": "5° Primaria", "level": "primaria", "order": 5},    current_year = AcademicYear.objects.filter(is_current=True).first()

    ]    if not current_year:

            print("❌ No hay año académico activo")

    # Grados de Bachillerato        return

    secondary_grades = [    

        {"name": "6° Bachillerato", "level": "bachillerato", "order": 6},    # Obtener profesor con asignaciones

        {"name": "7° Bachillerato", "level": "bachillerato", "order": 7},    teacher = User.objects.filter(username='prof_rodriguez').first()

        {"name": "8° Bachillerato", "level": "bachillerato", "order": 8},    if not teacher:

        {"name": "9° Bachillerato", "level": "bachillerato", "order": 9},        print("❌ No se encontró el profesor prof_rodriguez")

        {"name": "10° Bachillerato", "level": "bachillerato", "order": 10},        return

        {"name": "11° Bachillerato", "level": "bachillerato", "order": 11},    

    ]    print(f"👨‍🏫 Profesor: {teacher.get_full_name()}")

        

    all_grades = primary_grades + secondary_grades    # Obtener asignaciones del profesor

        assignments = SubjectAssignment.objects.filter(

    for grade_data in all_grades:        teacher=teacher,

        grade, created = Grade.objects.get_or_create(        academic_year=current_year

            order=grade_data["order"],    )

            defaults=grade_data    

        )    print(f"📚 Asignaciones encontradas: {assignments.count()}")

            

        if created:    activities = [

            print(f"✅ Creado: {grade.name} - {grade.get_level_display()}")        ('Quiz de entrada', 'quiz'),

        else:        ('Examen parcial', 'exam'),

            print(f"⚠️  Ya existe: {grade.name} - {grade.get_level_display()}")        ('Tarea de práctica', 'homework'),

            ('Participación en clase', 'participation'),

    print(f"\n=== RESUMEN ===")        ('Proyecto final', 'project'),

    print(f"Total grados creados: {Grade.objects.count()}")    ]

    print(f"Primaria: {Grade.objects.filter(level='primaria').count()}")    

    print(f"Bachillerato: {Grade.objects.filter(level='bachillerato').count()}")    periods = ['period_1', 'period_2', 'period_3']

        

    print("\n=== LISTA DE GRADOS ===")    created_count = 0

    for grade in Grade.objects.all().order_by('order'):    

        print(f"  {grade.order}. {grade.name} - {grade.get_level_display()}")    for assignment in assignments:

        print(f"\n📖 Materia: {assignment.subject.name}")

if __name__ == "__main__":        print(f"🏫 Curso: {assignment.course.grade.name} {assignment.course.section}")

    create_sample_grades()        
        # Obtener estudiantes del curso
        students = Student.objects.filter(course=assignment.course, status='active')
        print(f"👥 Estudiantes: {students.count()}")
        
        # Crear algunas calificaciones para cada estudiante
        for student in students[:5]:  # Solo primeros 5 estudiantes
            for i, (activity_name, activity_type) in enumerate(activities[:3]):  # Solo 3 actividades
                grade_value = Decimal(str(round(random.uniform(2.5, 5.0), 1)))
                period = random.choice(periods)
                date_recorded = date.today() - timedelta(days=random.randint(1, 30))
                
                grade_record, created = GradeRecord.objects.get_or_create(
                    student=student,
                    subject=assignment.subject,
                    teacher=teacher,
                    activity_name=activity_name,
                    activity_type=activity_type,
                    period=period,
                    defaults={
                        'grade_value': grade_value,
                        'max_value': Decimal('5.00'),
                        'weight': Decimal('1.00'),
                        'date_recorded': date_recorded,
                        'observations': f'Calificación de {activity_name.lower()}'
                    }
                )
                
                if created:
                    created_count += 1
                    print(f"   ✅ {student.user.get_full_name()}: {activity_name} = {grade_value}")
    
    print(f"\n🎉 Total de calificaciones creadas: {created_count}")
    
    # Mostrar resumen
    total_grades = GradeRecord.objects.filter(teacher=teacher).count()
    print(f"📊 Total de calificaciones del profesor: {total_grades}")

if __name__ == "__main__":
    create_sample_grades()