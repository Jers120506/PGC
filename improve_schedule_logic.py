#!/usr/bin/env python
"""
Mejora de la lógica del sistema de horarios, salones y asignaciones
Este script optimiza la distribución de recursos para un funcionamiento completo del sistema
"""

import os
import sys
import django
from datetime import time, date
from django.db import transaction

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')
django.setup()

from academics_extended.models import (
    AcademicYear, Grade, Subject, Course, Classroom, TimeSlot, 
    Schedule, Student, SubjectAssignment, GradeSubjectAssignment,
    TeacherSubjectAssignment
)
from django.contrib.auth.models import User
from authentication.models import UserProfile
from django.db import models
import random

def print_header(title):
    """Imprimir encabezado formateado"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def get_current_academic_year():
    """Obtener el año académico actual"""
    year = AcademicYear.objects.filter(is_current=True).first()
    if not year:
        year = AcademicYear.objects.first()
    return year

def create_comprehensive_grade_subject_assignments():
    """Crear asignaciones de materias a grados de manera integral"""
    print_header("CREANDO ASIGNACIONES DE MATERIAS A GRADOS")
    
    # Definir materias por nivel y grado
    grade_subject_config = {
        # PRIMARIA
        'primaria': {
            'basic_subjects': [
                ('MAT', 'Matemáticas', 'matematicas', 5),
                ('ESP', 'Español', 'lenguaje', 5), 
                ('CN', 'Ciencias Naturales', 'ciencias', 3),
                ('CS', 'Ciencias Sociales', 'sociales', 3),
                ('ING', 'Inglés', 'ingles', 2),
                ('EF', 'Educación Física', 'educacion_fisica', 2),
                ('ART', 'Artes', 'artes', 2),
                ('REL', 'Religión', 'religion', 1),
                ('ETI', 'Ética y Valores', 'etica', 1),
            ]
        },
        # BACHILLERATO  
        'bachillerato': {
            'basic_subjects': [
                ('MAT', 'Matemáticas', 'matematicas', 4),
                ('ESP', 'Español', 'lenguaje', 4),
                ('CN', 'Ciencias Naturales', 'ciencias', 4),
                ('CS', 'Ciencias Sociales', 'sociales', 3),
                ('ING', 'Inglés', 'ingles', 3),
                ('EF', 'Educación Física', 'educacion_fisica', 2),
                ('ART', 'Artes', 'artes', 1),
                ('INF', 'Informática', 'informatica', 2),
                ('REL', 'Religión', 'religion', 1),
                ('ETI', 'Ética y Valores', 'etica', 1),
            ]
        }
    }
    
    created_assignments = 0
    
    for grade in Grade.objects.all():
        print(f"\nProcesando grado: {grade.name} ({grade.level})")
        
        subjects_config = grade_subject_config.get(grade.level, {}).get('basic_subjects', [])
        
        for subject_code, subject_name, area, hours in subjects_config:
            # Buscar o crear la materia
            subject, created = Subject.objects.get_or_create(
                code=subject_code,
                defaults={
                    'name': subject_name,
                    'area': area,
                    'hours_per_week': hours
                }
            )
            
            if created:
                print(f"  ✓ Materia creada: {subject}")
            
            # Crear asignación de materia a grado
            assignment, created = GradeSubjectAssignment.objects.get_or_create(
                grade=grade,
                subject=subject,
                defaults={
                    'hours_per_week': hours,
                    'is_mandatory': True,
                    'semester': 'anual'
                }
            )
            
            if created:
                print(f"    → Asignación creada: {hours}h/semana")
                created_assignments += 1
    
    print(f"\n✅ Total asignaciones de grado-materia creadas: {created_assignments}")
    return created_assignments

def create_comprehensive_time_slots():
    """Crear franjas horarias completas para el día escolar"""
    print_header("CREANDO FRANJAS HORARIAS COMPLETAS")
    
    time_slots_config = [
        ("1° Hora", "07:00", "07:45", 1),
        ("2° Hora", "07:45", "08:30", 2),
        ("Descanso 1", "08:30", "08:45", 3),
        ("3° Hora", "08:45", "09:30", 4),
        ("4° Hora", "09:30", "10:15", 5),
        ("Descanso 2", "10:15", "10:30", 6),
        ("5° Hora", "10:30", "11:15", 7),
        ("6° Hora", "11:15", "12:00", 8),
        ("Almuerzo", "12:00", "13:00", 9),
        ("7° Hora", "13:00", "13:45", 10),
        ("8° Hora", "13:45", "14:30", 11),
    ]
    
    created_slots = 0
    
    for name, start_str, end_str, order in time_slots_config:
        start_time = time.fromisoformat(start_str)
        end_time = time.fromisoformat(end_str)
        
        slot, created = TimeSlot.objects.get_or_create(
            name=name,
            defaults={
                'start_time': start_time,
                'end_time': end_time,
                'order': order,
                'is_active': True
            }
        )
        
        if created:
            print(f"  ✓ Franja creada: {slot}")
            created_slots += 1
    
    print(f"\n✅ Total franjas horarias creadas: {created_slots}")
    return created_slots

def assign_students_to_courses_intelligently():
    """Asignar estudiantes a cursos de manera inteligente"""
    print_header("ASIGNANDO ESTUDIANTES A CURSOS")
    
    # Obtener estudiantes sin curso
    students_without_course = Student.objects.filter(course__isnull=True, status='active')
    print(f"Estudiantes sin curso: {students_without_course.count()}")
    
    assignments_made = 0
    
    for student in students_without_course:
        # Calcular edad aproximada del estudiante para asignar grado apropiado
        age = student.age
        
        # Mapeo edad -> grado aproximado
        if age <= 6:
            target_grade_names = ['1° Primaria']
        elif age <= 7:
            target_grade_names = ['2° Primaria']
        elif age <= 8:
            target_grade_names = ['3° Primaria']
        elif age <= 9:
            target_grade_names = ['4° Primaria']
        elif age <= 10:
            target_grade_names = ['5° Primaria']
        elif age <= 11:
            target_grade_names = ['6° Bachillerato']
        elif age <= 12:
            target_grade_names = ['7° Bachillerato']
        elif age <= 13:
            target_grade_names = ['8° Bachillerato']
        elif age <= 14:
            target_grade_names = ['9° Bachillerato']
        elif age <= 15:
            target_grade_names = ['10° Bachillerato']
        else:
            target_grade_names = ['11° Bachillerato']
        
        # Buscar cursos apropiados con cupo disponible
        available_courses = Course.objects.filter(
            grade__name__in=target_grade_names,
            is_active=True
        ).annotate(
            student_count=models.Count('students')
        ).filter(
            student_count__lt=models.F('max_students')
        ).order_by('student_count')
        
        if available_courses.exists():
            chosen_course = available_courses.first()
            student.course = chosen_course
            student.save()
            
            print(f"  ✓ {student.user.get_full_name()} ({age} años) → {chosen_course}")
            assignments_made += 1
        else:
            print(f"  ⚠️ No hay cupo disponible para {student.user.get_full_name()} ({age} años)")
    
    print(f"\n✅ Estudiantes asignados a cursos: {assignments_made}")
    return assignments_made

def create_subject_assignments_for_all_courses():
    """Crear asignaciones de profesores a materias para todos los cursos"""
    print_header("CREANDO ASIGNACIONES DE PROFESORES A MATERIAS")
    
    academic_year = get_current_academic_year()
    teachers = User.objects.filter(profile__role='teacher', is_active=True)
    teachers_list = list(teachers)
    
    if not teachers_list:
        print("⚠️ No hay profesores disponibles")
        return 0
    
    created_assignments = 0
    
    for course in Course.objects.filter(is_active=True):
        print(f"\nProcesando curso: {course}")
        
        # Obtener materias asignadas al grado de este curso
        grade_subjects = GradeSubjectAssignment.objects.filter(grade=course.grade)
        
        for grade_subject in grade_subjects:
            subject = grade_subject.subject
            
            # Verificar si ya existe asignación para esta materia y curso
            existing_assignment = SubjectAssignment.objects.filter(
                subject=subject,
                course=course,
                academic_year=academic_year
            ).first()
            
            if not existing_assignment:
                # Asignar profesor aleatoriamente (en un sistema real sería más específico)
                teacher = random.choice(teachers_list)
                
                assignment = SubjectAssignment.objects.create(
                    teacher=teacher,
                    subject=subject,
                    course=course,
                    academic_year=academic_year
                )
                
                print(f"  ✓ {teacher.get_full_name()} → {subject.name}")
                created_assignments += 1
    
    print(f"\n✅ Total asignaciones profesor-materia creadas: {created_assignments}")
    return created_assignments

def create_comprehensive_schedule_distribution():
    """Crear distribución completa de horarios para todos los cursos"""
    print_header("CREANDO DISTRIBUCIÓN COMPLETA DE HORARIOS")
    
    academic_year = get_current_academic_year()
    
    # Obtener recursos disponibles
    courses = Course.objects.filter(is_active=True)
    classrooms = list(Classroom.objects.filter(is_active=True))
    time_slots = TimeSlot.objects.filter(
        is_active=True,
        name__icontains='hora'  # Solo franjas de clase, no descansos
    ).order_by('order')
    
    if not classrooms:
        print("⚠️ No hay salones disponibles")
        return 0
    
    if not time_slots:
        print("⚠️ No hay franjas horarias disponibles")
        return 0
    
    created_schedules = 0
    weekdays = [1, 2, 3, 4, 5]  # Lunes a viernes
    
    print(f"Recursos disponibles:")
    print(f"  - Cursos: {courses.count()}")
    print(f"  - Salones: {len(classrooms)}")
    print(f"  - Franjas: {time_slots.count()}")
    
    # Diccionario para rastrear ocupación de recursos
    classroom_schedule = {}  # {(classroom_id, weekday, time_slot_id): True}
    teacher_schedule = {}    # {(teacher_id, weekday, time_slot_id): True}
    
    for course in courses:
        print(f"\nCreando horarios para: {course}")
        
        # Obtener asignaciones de materias para este curso
        subject_assignments = SubjectAssignment.objects.filter(
            course=course,
            academic_year=academic_year
        )
        
        if not subject_assignments:
            print(f"  ⚠️ No hay asignaciones de materias para {course}")
            continue
        
        # Obtener materias con sus horas semanales
        course_subjects = []
        for assignment in subject_assignments:
            grade_subject = GradeSubjectAssignment.objects.filter(
                grade=course.grade,
                subject=assignment.subject
            ).first()
            
            if grade_subject:
                hours_needed = grade_subject.hours_per_week
                course_subjects.append({
                    'assignment': assignment,
                    'subject': assignment.subject,
                    'teacher': assignment.teacher,
                    'hours_needed': hours_needed
                })
        
        # Distribuir las horas de cada materia a lo largo de la semana
        for subject_info in course_subjects:
            hours_assigned = 0
            hours_needed = subject_info['hours_needed']
            subject = subject_info['subject']
            teacher = subject_info['teacher']
            
            # Intentar asignar las horas necesarias
            for attempt in range(hours_needed * 3):  # Múltiples intentos
                if hours_assigned >= hours_needed:
                    break
                
                # Elegir día y franja aleatoriamente
                weekday = random.choice(weekdays)
                time_slot = random.choice(list(time_slots))
                
                # Elegir salón basándose en capacidad del curso
                suitable_classrooms = [
                    c for c in classrooms 
                    if c.capacity >= course.current_students_count + 5  # Margen de seguridad
                ]
                
                if not suitable_classrooms:
                    suitable_classrooms = classrooms  # Usar cualquier salón si no hay opciones
                
                classroom = random.choice(suitable_classrooms)
                
                # Verificar conflictos
                classroom_key = (classroom.id, weekday, time_slot.id)
                teacher_key = (teacher.id, weekday, time_slot.id)
                
                if (classroom_key in classroom_schedule or 
                    teacher_key in teacher_schedule):
                    continue  # Hay conflicto, intentar otro
                
                # Verificar si ya existe un horario para este curso en este momento
                existing_schedule = Schedule.objects.filter(
                    course=course,
                    weekday=weekday,
                    time_slot=time_slot,
                    academic_year=academic_year
                ).first()
                
                if existing_schedule:
                    continue  # Ya hay una clase programada para este curso
                
                # Crear el horario
                try:
                    schedule = Schedule.objects.create(
                        course=course,
                        subject=subject,
                        teacher=teacher,
                        classroom=classroom,
                        time_slot=time_slot,
                        weekday=weekday,
                        academic_year=academic_year,
                        is_active=True
                    )
                    
                    # Marcar recursos como ocupados
                    classroom_schedule[classroom_key] = True
                    teacher_schedule[teacher_key] = True
                    
                    hours_assigned += 1
                    created_schedules += 1
                    
                    weekday_name = dict(Schedule.WEEKDAY_CHOICES)[weekday]
                    print(f"    ✓ {subject.name} - {weekday_name} {time_slot.name} - {classroom.name}")
                    
                except Exception as e:
                    print(f"    ⚠️ Error creando horario: {e}")
                    continue
            
            if hours_assigned < hours_needed:
                print(f"    ⚠️ {subject.name}: Solo se asignaron {hours_assigned}/{hours_needed} horas")
    
    print(f"\n✅ Total horarios creados: {created_schedules}")
    return created_schedules

def optimize_classroom_assignments():
    """Optimizar asignaciones de salones basándose en capacidad y ubicación"""
    print_header("OPTIMIZANDO ASIGNACIONES DE SALONES")
    
    # Obtener estadísticas actuales
    schedules = Schedule.objects.filter(is_active=True)
    optimizations_made = 0
    
    for schedule in schedules:
        course = schedule.course
        current_classroom = schedule.classroom
        students_count = course.current_students_count
        
        # Si el salón actual es muy grande o muy pequeño, buscar uno mejor
        if (current_classroom.capacity > students_count * 2 or 
            current_classroom.capacity < students_count):
            
            # Buscar salón más apropiado
            better_classrooms = Classroom.objects.filter(
                is_active=True,
                capacity__gte=students_count,
                capacity__lte=students_count + 10
            ).exclude(id=current_classroom.id)
            
            if better_classrooms.exists():
                # Verificar disponibilidad del nuevo salón
                for new_classroom in better_classrooms:
                    conflict = Schedule.objects.filter(
                        classroom=new_classroom,
                        weekday=schedule.weekday,
                        time_slot=schedule.time_slot,
                        academic_year=schedule.academic_year,
                        is_active=True
                    ).exclude(id=schedule.id).exists()
                    
                    if not conflict:
                        old_classroom = schedule.classroom
                        schedule.classroom = new_classroom
                        schedule.save()
                        
                        print(f"  ✓ {schedule.course} - {schedule.subject.name}")
                        print(f"    {old_classroom.name} (cap: {old_classroom.capacity}) → {new_classroom.name} (cap: {new_classroom.capacity})")
                        optimizations_made += 1
                        break
    
    print(f"\n✅ Optimizaciones de salones realizadas: {optimizations_made}")
    return optimizations_made

def print_system_summary():
    """Imprimir resumen del estado del sistema"""
    print_header("RESUMEN DEL SISTEMA MEJORADO")
    
    academic_year = get_current_academic_year()
    
    # Estadísticas generales
    total_courses = Course.objects.filter(is_active=True).count()
    total_students = Student.objects.filter(status='active').count()
    total_teachers = User.objects.filter(profile__role='teacher', is_active=True).count()
    total_classrooms = Classroom.objects.filter(is_active=True).count()
    total_subjects = Subject.objects.count()
    
    print(f"📊 ESTADÍSTICAS GENERALES:")
    print(f"   • Cursos activos: {total_courses}")
    print(f"   • Estudiantes activos: {total_students}")
    print(f"   • Profesores activos: {total_teachers}")
    print(f"   • Salones disponibles: {total_classrooms}")
    print(f"   • Materias disponibles: {total_subjects}")
    
    # Estadísticas de horarios
    total_schedules = Schedule.objects.filter(is_active=True, academic_year=academic_year).count()
    courses_with_schedules = Schedule.objects.filter(
        is_active=True, 
        academic_year=academic_year
    ).values('course').distinct().count()
    
    print(f"\n📅 HORARIOS Y ASIGNACIONES:")
    print(f"   • Total horarios programados: {total_schedules}")
    print(f"   • Cursos con horarios: {courses_with_schedules}/{total_courses}")
    print(f"   • Cobertura de cursos: {(courses_with_schedules/total_courses*100):.1f}%")
    
    # Estadísticas de asignaciones
    total_subject_assignments = SubjectAssignment.objects.filter(academic_year=academic_year).count()
    total_grade_assignments = GradeSubjectAssignment.objects.count()
    
    print(f"   • Asignaciones profesor-materia: {total_subject_assignments}")
    print(f"   • Asignaciones grado-materia: {total_grade_assignments}")
    
    # Estadísticas de estudiantes
    students_with_course = Student.objects.filter(status='active', course__isnull=False).count()
    students_without_course = Student.objects.filter(status='active', course__isnull=True).count()
    
    print(f"\n👥 INSCRIPCIONES DE ESTUDIANTES:")
    print(f"   • Estudiantes inscritos en cursos: {students_with_course}")
    print(f"   • Estudiantes sin curso: {students_without_course}")
    print(f"   • Tasa de inscripción: {(students_with_course/total_students*100):.1f}%")
    
    # Uso de salones
    classrooms_in_use = Schedule.objects.filter(
        is_active=True, 
        academic_year=academic_year
    ).values('classroom').distinct().count()
    
    print(f"\n🏫 USO DE SALONES:")
    print(f"   • Salones en uso: {classrooms_in_use}/{total_classrooms}")
    print(f"   • Utilización de salones: {(classrooms_in_use/total_classrooms*100):.1f}%")

def main():
    """Función principal para mejorar la lógica del sistema"""
    print_header("INICIO DE MEJORA DEL SISTEMA ACADÉMICO")
    
    try:
        with transaction.atomic():
            # 1. Crear asignaciones de materias a grados
            create_comprehensive_grade_subject_assignments()
            
            # 2. Crear franjas horarias completas
            create_comprehensive_time_slots()
            
            # 3. Asignar estudiantes a cursos
            assign_students_to_courses_intelligently()
            
            # 4. Crear asignaciones de profesores a materias
            create_subject_assignments_for_all_courses()
            
            # 5. Crear distribución completa de horarios
            create_comprehensive_schedule_distribution()
            
            # 6. Optimizar asignaciones de salones
            optimize_classroom_assignments()
            
            # 7. Mostrar resumen final
            print_system_summary()
            
            print_header("✅ MEJORA DEL SISTEMA COMPLETADA EXITOSAMENTE")
            
    except Exception as e:
        print(f"\n❌ ERROR DURANTE LA MEJORA: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    main()