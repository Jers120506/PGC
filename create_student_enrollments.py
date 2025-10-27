#!/usr/bin/env python
"""
Script para crear matrículas de estudiantes de prueba
Integra estudiantes existentes con el nuevo sistema de matrículas
"""

import os
import sys
import django
from django.db import transaction

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')
django.setup()

from django.contrib.auth.models import User
from authentication.models import StudentEnrollment

def create_student_enrollments():
    """Crear matrículas para estudiantes existentes"""
    
    print("📚 Creando matrículas para estudiantes existentes...")
    
    try:
        with transaction.atomic():
            # Obtener admin user
            admin_user = User.objects.filter(username='admin').first()
            if not admin_user:
                print("❌ Error: Usuario admin no encontrado")
                return
            
            # Obtener estudiantes existentes
            students = User.objects.filter(profile__role='student', is_active=True)
            print(f"📊 Estudiantes encontrados: {students.count()}")
            
            # Obtener profesores para asignar como directores
            teachers = list(User.objects.filter(profile__role='teacher', is_active=True))
            print(f"👨‍🏫 Profesores disponibles: {len(teachers)}")
            
            if not teachers:
                print("⚠️  No hay profesores disponibles")
                return
            
            # Estructura de grados
            grade_structure = [
                {'grade': 'primero', 'sections': ['A', 'B']},
                {'grade': 'segundo', 'sections': ['A']},
                {'grade': 'tercero', 'sections': ['A']},
                {'grade': 'cuarto', 'sections': ['A']},
                {'grade': 'quinto', 'sections': ['A']},
                {'grade': 'sexto', 'sections': ['A']},
                {'grade': 'septimo', 'sections': ['A']},
                {'grade': 'octavo', 'sections': ['A']},
                {'grade': 'noveno', 'sections': ['A']},
                {'grade': 'decimo', 'sections': ['A']},
                {'grade': 'once', 'sections': ['A']},
            ]
            
            created_enrollments = 0
            teacher_index = 0
            
            for student in students:
                # Verificar si ya tiene matrícula
                existing_enrollment = StudentEnrollment.objects.filter(
                    student=student,
                    academic_year='2025'
                ).first()
                
                if existing_enrollment:
                    print(f"⚠️  {student.get_full_name()} ya tiene matrícula")
                    continue
                
                # Asignar grado y sección basado en el índice
                grade_info = grade_structure[created_enrollments % len(grade_structure)]
                grade = grade_info['grade']
                section = grade_info['sections'][0]  # Por simplicidad, usar la primera sección
                
                # Asignar profesor director
                homeroom_teacher = teachers[teacher_index % len(teachers)]
                teacher_index += 1
                
                # Generar datos de acudiente ficticios
                parent_names = [
                    "María González", "José Martínez", "Ana Rodríguez", "Carlos López",
                    "Elena Hernández", "Miguel Sánchez", "Lucía Torres", "Pablo Ruiz",
                    "Carmen Jiménez", "Antonio Moreno", "Isabel Muñoz", "Francisco Gil"
                ]
                
                parent_name = parent_names[created_enrollments % len(parent_names)]
                parent_phone = f"300-555-{str(created_enrollments + 1000).zfill(4)}"
                parent_email = f"{parent_name.lower().replace(' ', '.')}@email.com"
                
                # Crear la matrícula
                enrollment = StudentEnrollment.objects.create(
                    student=student,
                    academic_year='2025',
                    grade=grade,
                    section=section,
                    homeroom_teacher=homeroom_teacher,
                    status='active',
                    parent_guardian_name=parent_name,
                    parent_guardian_phone=parent_phone,
                    parent_guardian_email=parent_email,
                    created_by=admin_user
                )
                
                # Asignar automáticamente al grupo académico
                group_assigned = enrollment.assign_to_academic_group()
                
                created_enrollments += 1
                print(f"✅ Matrícula creada: {student.get_full_name()} - {enrollment.full_grade} - Director: {homeroom_teacher.get_full_name()}")
                
                if group_assigned:
                    print(f"   👥 Asignado al grupo académico: {enrollment.get_academic_group_name()}")
                elif group_assigned is None:
                    print(f"   ⚠️  Grupo académico '{enrollment.get_academic_group_name()}' no existe")
            
            print("\n📊 RESUMEN DE MATRÍCULAS CREADAS:")
            print("=" * 50)
            
            # Mostrar estadísticas por grado
            for grade_info in grade_structure:
                grade = grade_info['grade']
                count = StudentEnrollment.objects.filter(
                    academic_year='2025',
                    grade=grade
                ).count()
                
                if count > 0:
                    enrollments_in_grade = StudentEnrollment.objects.filter(
                        academic_year='2025',
                        grade=grade
                    ).select_related('homeroom_teacher')
                    
                    print(f"📚 {grade.title()}: {count} estudiantes")
                    for enrollment in enrollments_in_grade:
                        print(f"   - {enrollment.student.get_full_name()} (Sección {enrollment.section}) - Director: {enrollment.homeroom_teacher.get_full_name() if enrollment.homeroom_teacher else 'Sin asignar'}")
            
            # Estadísticas generales
            total_enrollments = StudentEnrollment.objects.filter(academic_year='2025').count()
            active_enrollments = StudentEnrollment.objects.filter(academic_year='2025', status='active').count()
            
            print(f"\n🎯 TOTALES:")
            print(f"   Total matrículas 2025: {total_enrollments}")
            print(f"   Estudiantes activos: {active_enrollments}")
            print(f"   Nuevas matrículas creadas: {created_enrollments}")
            
            print("\n🎉 ¡Sistema de matrículas configurado exitosamente!")
            print("\n💡 Ahora puedes:")
            print("   - Ver estudiantes en /administration/admin/users/ (pestaña Estudiantes)")
            print("   - Gestionar matrículas desde la interfaz web")
            print("   - Asignar/cambiar profesores directores")
            print("   - Cambiar estados de estudiantes")
            
    except Exception as e:
        print(f"❌ Error al crear matrículas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    create_student_enrollments()