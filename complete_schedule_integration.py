#!/usr/bin/env python3
"""
Script para mejorar la integración entre horarios, asignaciones e inscripciones
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')
django.setup()

from academics_extended.models import (
    Schedule, Course, Subject, SubjectAssignment, Student, 
    AcademicYear, TimeSlot, Classroom
)
from django.contrib.auth.models import User
from django.db import models

def create_subject_assignments():
    """Crear asignaciones de materias basadas en los horarios existentes"""
    print("📚 CREANDO ASIGNACIONES DE MATERIAS BASADAS EN HORARIOS")
    print("=" * 60)
    
    current_year = AcademicYear.objects.filter(is_current=True).first()
    if not current_year:
        print("❌ No hay año académico activo")
        return
    
    # Obtener todos los horarios activos
    schedules = Schedule.objects.filter(
        academic_year=current_year,
        is_active=True
    ).select_related('teacher', 'subject', 'course')
    
    assignments_created = 0
    
    for schedule in schedules:
        # Verificar si ya existe la asignación
        assignment, created = SubjectAssignment.objects.get_or_create(
            teacher=schedule.teacher,
            subject=schedule.subject,
            course=schedule.course,
            academic_year=current_year,
            defaults={
                'teacher': schedule.teacher,
                'subject': schedule.subject,
                'course': schedule.course,
                'academic_year': current_year
            }
        )
        
        if created:
            assignments_created += 1
            print(f"✅ Creada asignación: {schedule.teacher.get_full_name()} -> {schedule.subject.name} -> {schedule.course}")
    
    print(f"\n📊 Resumen:")
    print(f"   - Horarios procesados: {schedules.count()}")
    print(f"   - Asignaciones creadas: {assignments_created}")
    print(f"   - Asignaciones existentes: {schedules.count() - assignments_created}")

def validate_schedule_integrity():
    """Validar la integridad del sistema de horarios"""
    print("\n🔍 VALIDANDO INTEGRIDAD DEL SISTEMA")
    print("=" * 60)
    
    current_year = AcademicYear.objects.filter(is_current=True).first()
    issues = []
    
    # Verificar horarios sin asignaciones
    schedules_without_assignments = Schedule.objects.filter(
        academic_year=current_year,
        is_active=True
    ).exclude(
        teacher__in=SubjectAssignment.objects.filter(
            academic_year=current_year
        ).values_list('teacher', flat=True)
    )
    
    if schedules_without_assignments.exists():
        issues.append(f"⚠️  {schedules_without_assignments.count()} horarios sin asignaciones de materia")
    
    # Verificar estudiantes sin curso
    students_without_course = Student.objects.filter(
        status='active',
        course__isnull=True
    )
    
    if students_without_course.exists():
        issues.append(f"⚠️  {students_without_course.count()} estudiantes activos sin curso asignado")
    
    # Verificar cursos sin horarios
    courses_without_schedules = Course.objects.filter(
        academic_year=current_year,
        is_active=True
    ).exclude(
        id__in=Schedule.objects.filter(
            academic_year=current_year,
            is_active=True
        ).values_list('course_id', flat=True)
    )
    
    if courses_without_schedules.exists():
        issues.append(f"⚠️  {courses_without_schedules.count()} cursos sin horarios asignados")
    
    # Verificar conflictos de horarios
    conflicts = []
    time_slots = TimeSlot.objects.all()
    weekdays = [1, 2, 3, 4, 5]  # Lunes a Viernes
    
    for weekday in weekdays:
        for time_slot in time_slots:
            # Conflictos de profesor
            teacher_schedules = Schedule.objects.filter(
                weekday=weekday,
                time_slot=time_slot,
                academic_year=current_year,
                is_active=True
            ).values('teacher').annotate(count=models.Count('teacher')).filter(count__gt=1)
            
            for conflict in teacher_schedules:
                conflicts.append(f"Profesor {conflict['teacher']} tiene {conflict['count']} clases en {time_slot.name} el día {weekday}")
    
    if conflicts:
        issues.append(f"❌ {len(conflicts)} conflictos de horarios detectados")
    
    # Mostrar resultados
    if issues:
        print("🚨 PROBLEMAS DETECTADOS:")
        for issue in issues:
            print(f"   {issue}")
    else:
        print("✅ ¡Sistema de horarios íntegro! No se detectaron problemas.")
    
    return len(issues) == 0

def generate_schedule_statistics():
    """Generar estadísticas del sistema de horarios"""
    print("\n📊 ESTADÍSTICAS DEL SISTEMA DE HORARIOS")
    print("=" * 60)
    
    current_year = AcademicYear.objects.filter(is_current=True).first()
    
    # Estadísticas generales
    total_schedules = Schedule.objects.filter(academic_year=current_year, is_active=True).count()
    total_courses = Course.objects.filter(academic_year=current_year, is_active=True).count()
    total_students = Student.objects.filter(status='active').count()
    total_teachers = User.objects.filter(profile__role='teacher').count()
    
    print(f"📈 ESTADÍSTICAS GENERALES:")
    print(f"   - Total horarios activos: {total_schedules}")
    print(f"   - Total cursos activos: {total_courses}")
    print(f"   - Total estudiantes activos: {total_students}")
    print(f"   - Total profesores: {total_teachers}")
    
    # Estadísticas por curso
    courses = Course.objects.filter(academic_year=current_year, is_active=True)
    print(f"\n📚 ESTADÍSTICAS POR CURSO:")
    
    for course in courses:
        schedules_count = course.schedules.filter(is_active=True).count()
        students_count = course.current_students_count
        subjects = course.schedules.filter(is_active=True).values_list('subject__name', flat=True).distinct()
        
        print(f"   📖 {course}:")
        print(f"      - Horarios: {schedules_count}")
        print(f"      - Estudiantes: {students_count}/{course.max_students}")
        print(f"      - Materias: {len(subjects)} ({', '.join(subjects)})")
    
    # Estadísticas por profesor
    teachers = User.objects.filter(profile__role='teacher')
    print(f"\n👨‍🏫 ESTADÍSTICAS POR PROFESOR:")
    
    for teacher in teachers:
        schedules_count = Schedule.objects.filter(
            teacher=teacher,
            academic_year=current_year,
            is_active=True
        ).count()
        
        courses_taught = Schedule.objects.filter(
            teacher=teacher,
            academic_year=current_year,
            is_active=True
        ).values_list('course__grade__name', 'course__section').distinct()
        
        if schedules_count > 0:
            print(f"   👨‍🏫 {teacher.get_full_name()}:")
            print(f"      - Horas semanales: {schedules_count}")
            print(f"      - Cursos: {len(courses_taught)}")

def fix_common_issues():
    """Corregir problemas comunes del sistema"""
    print("\n🔧 CORRIGIENDO PROBLEMAS COMUNES")
    print("=" * 60)
    
    current_year = AcademicYear.objects.filter(is_current=True).first()
    fixes_applied = 0
    
    # Corregir horarios con academic_year null
    schedules_without_year = Schedule.objects.filter(academic_year__isnull=True)
    if schedules_without_year.exists():
        updated = schedules_without_year.update(academic_year=current_year)
        print(f"✅ Corregidos {updated} horarios sin año académico")
        fixes_applied += updated
    
    # Asegurar que todos los cursos tengan año académico actual
    courses_wrong_year = Course.objects.filter(is_active=True).exclude(academic_year=current_year)
    if courses_wrong_year.exists():
        for course in courses_wrong_year:
            print(f"⚠️  Curso {course} tiene año académico incorrecto: {course.academic_year}")
    
    print(f"\n📊 Total de correcciones aplicadas: {fixes_applied}")

def main():
    """Función principal"""
    print("🔄 MEJORANDO INTEGRACIÓN DEL SISTEMA DE HORARIOS")
    print("=" * 80)
    
    try:
        # Paso 1: Crear asignaciones basadas en horarios
        create_subject_assignments()
        
        # Paso 2: Validar integridad
        is_valid = validate_schedule_integrity()
        
        # Paso 3: Corregir problemas comunes
        fix_common_issues()
        
        # Paso 4: Generar estadísticas
        generate_schedule_statistics()
        
        print(f"\n{'='*80}")
        if is_valid:
            print("🎉 ¡SISTEMA DE HORARIOS COMPLETAMENTE INTEGRADO!")
        else:
            print("⚠️  SISTEMA MEJORADO - Revisa los problemas detectados arriba")
        
        print("\n📝 SIGUIENTES PASOS:")
        print("   1. Inicia sesión en el sistema: http://127.0.0.1:8000/auth/login/")
        print("   2. Ve al sistema de horarios: http://127.0.0.1:8000/academic-system/schedules/")
        print("   3. Prueba todas las funcionalidades: crear, editar, consultar")
        print("   4. Verifica que los estudiantes vean sus horarios correctamente")
        
    except Exception as e:
        print(f"❌ Error durante la integración: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()