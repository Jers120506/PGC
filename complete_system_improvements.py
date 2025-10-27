#!/usr/bin/env python
"""
Mejora de la lógica del sistema de horarios - Continuación sin transacciones atómicas
"""

import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')
django.setup()

from academics_extended.models import (
    AcademicYear, Grade, Subject, Course, Classroom, TimeSlot, 
    Schedule, Student, SubjectAssignment, GradeSubjectAssignment
)
from django.contrib.auth.models import User
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

def complete_subject_assignments():
    """Completar asignaciones de profesores a materias faltantes"""
    print_header("COMPLETANDO ASIGNACIONES DE PROFESORES")
    
    academic_year = get_current_academic_year()
    teachers = list(User.objects.filter(profile__role='teacher', is_active=True))
    
    if not teachers:
        print("⚠️ No hay profesores disponibles")
        return 0
    
    created_assignments = 0
    
    for course in Course.objects.filter(is_active=True):
        print(f"Procesando curso: {course}")
        
        # Obtener materias que deberían estar asignadas para este grado
        grade_subjects = GradeSubjectAssignment.objects.filter(grade=course.grade)
        
        for grade_subject in grade_subjects:
            subject = grade_subject.subject
            
            # Verificar si ya existe asignación
            existing = SubjectAssignment.objects.filter(
                subject=subject,
                course=course,
                academic_year=academic_year
            ).exists()
            
            if not existing:
                # Asignar profesor aleatoriamente
                teacher = random.choice(teachers)
                
                try:
                    assignment = SubjectAssignment.objects.create(
                        teacher=teacher,
                        subject=subject,
                        course=course,
                        academic_year=academic_year
                    )
                    print(f"  ✓ {teacher.get_full_name()} → {subject.name}")
                    created_assignments += 1
                except Exception as e:
                    print(f"  ⚠️ Error: {e}")
    
    print(f"\n✅ Asignaciones creadas: {created_assignments}")
    return created_assignments

def smart_schedule_creation():
    """Crear horarios de manera inteligente evitando conflictos"""
    print_header("CREACIÓN INTELIGENTE DE HORARIOS")
    
    academic_year = get_current_academic_year()
    
    # Recursos disponibles
    courses = Course.objects.filter(is_active=True)
    classrooms = list(Classroom.objects.filter(is_active=True))
    teaching_slots = TimeSlot.objects.filter(
        is_active=True,
        name__icontains='hora'
    ).exclude(
        name__icontains='descanso'
    ).exclude(
        name__icontains='almuerzo'
    ).order_by('order')
    
    if not classrooms or not teaching_slots:
        print("⚠️ Faltan recursos (salones o franjas horarias)")
        return 0
    
    print(f"Recursos disponibles:")
    print(f"  - Cursos: {courses.count()}")
    print(f"  - Salones: {len(classrooms)}")
    print(f"  - Franjas de clase: {teaching_slots.count()}")
    
    created_schedules = 0
    weekdays = [1, 2, 3, 4, 5]  # Lunes a viernes
    
    # Diccionarios para rastrear ocupación
    occupied_slots = set()  # {(classroom_id, weekday, time_slot_id)}
    teacher_occupied = set()  # {(teacher_id, weekday, time_slot_id)}
    course_occupied = set()  # {(course_id, weekday, time_slot_id)}
    
    # Obtener horarios existentes para evitar duplicados
    existing_schedules = Schedule.objects.filter(
        is_active=True,
        academic_year=academic_year
    )
    
    for schedule in existing_schedules:
        occupied_slots.add((schedule.classroom.id, schedule.weekday, schedule.time_slot.id))
        teacher_occupied.add((schedule.teacher.id, schedule.weekday, schedule.time_slot.id))
        course_occupied.add((schedule.course.id, schedule.weekday, schedule.time_slot.id))
    
    print(f"\nHorarios existentes: {existing_schedules.count()}")
    
    # Procesar cada curso
    for course in courses:
        print(f"\nProcesando: {course}")
        
        # Obtener asignaciones de materias para este curso
        subject_assignments = SubjectAssignment.objects.filter(
            course=course,
            academic_year=academic_year
        )
        
        if not subject_assignments:
            print(f"  ⚠️ No hay asignaciones de materias")
            continue
        
        # Para cada materia asignada
        for assignment in subject_assignments:
            subject = assignment.subject
            teacher = assignment.teacher
            
            # Obtener horas semanales necesarias
            grade_subject = GradeSubjectAssignment.objects.filter(
                grade=course.grade,
                subject=subject
            ).first()
            
            if not grade_subject:
                continue
            
            hours_needed = grade_subject.hours_per_week
            hours_assigned = 0
            
            # Contar horarios ya existentes para esta materia y curso
            existing_for_subject = Schedule.objects.filter(
                course=course,
                subject=subject,
                academic_year=academic_year,
                is_active=True
            ).count()
            
            hours_to_assign = max(0, hours_needed - existing_for_subject)
            
            if hours_to_assign == 0:
                continue
            
            print(f"  → {subject.name}: necesita {hours_to_assign} horas más")
            
            # Intentar asignar las horas necesarias
            attempts = 0
            max_attempts = 50
            
            while hours_assigned < hours_to_assign and attempts < max_attempts:
                attempts += 1
                
                # Elegir día y franja aleatoriamente
                weekday = random.choice(weekdays)
                time_slot = random.choice(list(teaching_slots))
                
                # Verificar si el curso ya tiene clase en este momento
                course_key = (course.id, weekday, time_slot.id)
                if course_key in course_occupied:
                    continue
                
                # Verificar si el profesor está ocupado
                teacher_key = (teacher.id, weekday, time_slot.id)
                if teacher_key in teacher_occupied:
                    continue
                
                # Elegir salón apropiado
                student_count = course.current_students_count if hasattr(course, 'current_students_count') else 25
                
                # Filtrar salones disponibles
                available_classrooms = []
                for classroom in classrooms:
                    classroom_key = (classroom.id, weekday, time_slot.id)
                    if classroom_key not in occupied_slots:
                        # Verificar capacidad
                        if classroom.capacity >= student_count:
                            available_classrooms.append(classroom)
                
                if not available_classrooms:
                    continue
                
                # Elegir el salón más apropiado (capacidad similar al número de estudiantes)
                chosen_classroom = min(available_classrooms, 
                                     key=lambda c: abs(c.capacity - student_count - 5))
                
                # Crear el horario
                try:
                    schedule = Schedule.objects.create(
                        course=course,
                        subject=subject,
                        teacher=teacher,
                        classroom=chosen_classroom,
                        time_slot=time_slot,
                        weekday=weekday,
                        academic_year=academic_year,
                        is_active=True
                    )
                    
                    # Actualizar registros de ocupación
                    occupied_slots.add((chosen_classroom.id, weekday, time_slot.id))
                    teacher_occupied.add((teacher.id, weekday, time_slot.id))
                    course_occupied.add((course.id, weekday, time_slot.id))
                    
                    hours_assigned += 1
                    created_schedules += 1
                    
                    weekday_name = dict(Schedule.WEEKDAY_CHOICES)[weekday]
                    print(f"    ✓ {weekday_name} {time_slot.name} - {chosen_classroom.name}")
                    
                except Exception as e:
                    print(f"    ⚠️ Error: {e}")
                    continue
            
            if hours_assigned < hours_to_assign:
                print(f"    ⚠️ Solo se asignaron {hours_assigned}/{hours_to_assign} horas")
    
    print(f"\n✅ Total horarios creados: {created_schedules}")
    return created_schedules

def assign_remaining_students():
    """Asignar estudiantes restantes a cursos apropiados"""
    print_header("ASIGNANDO ESTUDIANTES RESTANTES")
    
    students_without_course = Student.objects.filter(
        course__isnull=True, 
        status='active'
    )
    
    print(f"Estudiantes sin curso: {students_without_course.count()}")
    
    assignments_made = 0
    
    for student in students_without_course:
        # Buscar cursos con cupo disponible
        available_courses = Course.objects.filter(
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
            
            print(f"  ✓ {student.user.get_full_name()} → {chosen_course}")
            assignments_made += 1
        else:
            print(f"  ⚠️ No hay cupo para {student.user.get_full_name()}")
    
    print(f"\n✅ Estudiantes asignados: {assignments_made}")
    return assignments_made

def optimize_classroom_usage():
    """Optimizar el uso de salones"""
    print_header("OPTIMIZANDO USO DE SALONES")
    
    academic_year = get_current_academic_year()
    schedules = Schedule.objects.filter(is_active=True, academic_year=academic_year)
    optimizations = 0
    
    for schedule in schedules:
        course = schedule.course
        current_classroom = schedule.classroom
        
        # Calcular estudiantes en el curso (usar un valor por defecto si falla)
        try:
            students_count = course.students.count()
        except:
            students_count = 25  # Valor por defecto
        
        # Si el salón es muy grande para el curso, buscar uno mejor
        if current_classroom.capacity > students_count * 2:
            # Buscar salón más apropiado
            better_classrooms = Classroom.objects.filter(
                is_active=True,
                capacity__gte=students_count,
                capacity__lt=current_classroom.capacity
            )
            
            for new_classroom in better_classrooms:
                # Verificar disponibilidad
                conflict = Schedule.objects.filter(
                    classroom=new_classroom,
                    weekday=schedule.weekday,
                    time_slot=schedule.time_slot,
                    academic_year=academic_year,
                    is_active=True
                ).exclude(id=schedule.id).exists()
                
                if not conflict:
                    old_classroom = schedule.classroom
                    schedule.classroom = new_classroom
                    schedule.save()
                    
                    print(f"  ✓ {schedule.course} - {schedule.subject.name}")
                    print(f"    {old_classroom.name} (cap: {old_classroom.capacity}) → {new_classroom.name} (cap: {new_classroom.capacity})")
                    optimizations += 1
                    break
    
    print(f"\n✅ Optimizaciones realizadas: {optimizations}")
    return optimizations

def print_final_summary():
    """Imprimir resumen final"""
    print_header("RESUMEN FINAL DEL SISTEMA")
    
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
    print(f"   • Estudiantes inscritos: {students_with_course}")
    print(f"   • Estudiantes sin curso: {students_without_course}")
    if total_students > 0:
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
    """Función principal para completar las mejoras"""
    print_header("COMPLETANDO MEJORAS DEL SISTEMA ACADÉMICO")
    
    try:
        # 1. Completar asignaciones de profesores
        complete_subject_assignments()
        
        # 2. Crear horarios inteligentemente
        smart_schedule_creation()
        
        # 3. Asignar estudiantes restantes
        assign_remaining_students()
        
        # 4. Optimizar uso de salones
        optimize_classroom_usage()
        
        # 5. Mostrar resumen final
        print_final_summary()
        
        print_header("✅ MEJORAS COMPLETADAS EXITOSAMENTE")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    main()