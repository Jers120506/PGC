#!/usr/bin/env python
"""
Script simple para verificar datos y APIs sin requerir servidor externo
"""

import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')
django.setup()

from django.contrib.auth.models import User
from authentication.models import UserProfile
from academics_extended.models import (
    Course, Subject, Classroom, TimeSlot, Schedule, Student
)

def verify_system_data():
    """Verificar estado del sistema"""
    print("🔍 VERIFICANDO SISTEMA DE HORARIOS")
    print("=" * 50)
    
    # Usuarios
    admin_users = User.objects.filter(is_superuser=True, is_active=True)
    teachers = User.objects.filter(profile__role='teacher', is_active=True)
    students = User.objects.filter(profile__role='student', is_active=True)
    
    print(f"👑 Administradores: {admin_users.count()}")
    print(f"👨‍🏫 Profesores: {teachers.count()}")
    print(f"👨‍🎓 Estudiantes: {students.count()}")
    
    # Datos académicos
    courses = Course.objects.filter(is_active=True)
    subjects = Subject.objects.all()
    classrooms = Classroom.objects.filter(is_active=True)
    time_slots = TimeSlot.objects.filter(is_active=True)
    schedules = Schedule.objects.all()
    
    print(f"📚 Cursos activos: {courses.count()}")
    print(f"📖 Materias: {subjects.count()}")
    print(f"🏫 Salones activos: {classrooms.count()}")
    print(f"⏰ Franjas horarias: {time_slots.count()}")
    print(f"📅 Horarios creados: {schedules.count()}")
    
    # Mostrar algunos ejemplos
    if teachers.exists():
        print(f"\n👨‍🏫 PROFESORES EJEMPLO:")
        for teacher in teachers[:3]:
            print(f"   • {teacher.get_full_name()} ({teacher.username})")
    
    if courses.exists():
        print(f"\n📚 CURSOS EJEMPLO:")
        for course in courses[:3]:
            print(f"   • {course.grade.name} - {course.section} ({course.academic_year.name})")
    
    if subjects.exists():
        print(f"\n📖 MATERIAS EJEMPLO:")
        for subject in subjects[:3]:
            print(f"   • {subject.name}")
    
    if classrooms.exists():
        print(f"\n🏫 SALONES EJEMPLO:")
        for classroom in classrooms[:3]:
            print(f"   • {classroom.name} (Cap: {classroom.capacity})")
    
    if time_slots.exists():
        print(f"\n⏰ FRANJAS EJEMPLO:")
        for slot in time_slots[:3]:
            print(f"   • {slot.name}: {slot.start_time}-{slot.end_time}")
    
    # Verificar si hay problemas
    problems = []
    
    if not admin_users.exists():
        problems.append("❌ No hay usuarios administradores")
    
    if teachers.count() == 0:
        problems.append("❌ No hay profesores disponibles")
        
    if courses.count() == 0:
        problems.append("❌ No hay cursos disponibles")
        
    if subjects.count() == 0:
        problems.append("❌ No hay materias disponibles")
        
    if classrooms.count() == 0:
        problems.append("❌ No hay salones disponibles")
        
    if time_slots.count() == 0:
        problems.append("❌ No hay franjas horarias disponibles")
    
    if problems:
        print(f"\n⚠️ PROBLEMAS DETECTADOS:")
        for problem in problems:
            print(f"   {problem}")
        
        print(f"\n💡 SOLUCIÓN:")
        print(f"   Ejecuta: python complete_system_improvements.py")
    else:
        print(f"\n✅ SISTEMA COMPLETO - LISTO PARA USAR")
        
        # Crear usuario admin de prueba si no existe
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@test.com',
                'first_name': 'Admin',
                'last_name': 'System',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True
            }
        )
        
        if created or not admin.check_password('admin123'):
            admin.set_password('admin123')
            admin.save()
            print(f"🔑 Usuario admin configurado")
        
        # Crear perfil si no existe
        profile, profile_created = UserProfile.objects.get_or_create(
            user=admin,
            defaults={
                'role': 'admin',
                'phone': '123456789',
                'address': 'Admin Address',
                'date_of_birth': '1990-01-01',
                'profile_completion_percentage': 100
            }
        )
        
        if profile.role != 'admin':
            profile.role = 'admin'
            profile.save()
        
        print(f"👑 Perfil admin configurado")
        print(f"\n🌐 ACCESO AL SISTEMA:")
        print(f"   URL: http://127.0.0.1:8000/academic-system/schedules/")
        print(f"   Usuario: admin")
        print(f"   Contraseña: admin123")

def test_data_structure():
    """Probar estructura de datos para API"""
    print(f"\n🧪 PROBANDO ESTRUCTURA DE DATOS PARA API:")
    print("=" * 50)
    
    try:
        from django.core.serializers import serialize
        import json
        
        # Simular datos de API
        courses = Course.objects.filter(is_active=True)[:5]
        teachers = User.objects.filter(profile__role='teacher', is_active=True)[:5]
        classrooms = Classroom.objects.filter(is_active=True)[:5]
        subjects = Subject.objects.all()[:5]
        time_slots = TimeSlot.objects.filter(is_active=True)[:5]
        
        api_data = {
            'courses': [{'id': c.id, 'name': f"{c.grade.name} - {c.section}"} for c in courses],
            'teachers': [{'id': t.id, 'name': t.get_full_name()} for t in teachers],
            'classrooms': [{'id': c.id, 'name': c.name} for c in classrooms],
            'subjects': [{'id': s.id, 'name': s.name} for s in subjects],
            'time_slots': [{'id': t.id, 'name': t.name} for t in time_slots]
        }
        
        print(f"📊 DATOS DISPONIBLES PARA API:")
        for key, items in api_data.items():
            print(f"   • {key}: {len(items)} elementos")
            if items:
                print(f"     Ejemplo: {items[0]}")
        
        # Verificar si hay datos suficientes
        if all(len(items) > 0 for items in api_data.values()):
            print(f"\n✅ DATOS SUFICIENTES PARA CREAR HORARIOS")
            return True
        else:
            empty_fields = [key for key, items in api_data.items() if len(items) == 0]
            print(f"\n❌ FALTAN DATOS EN: {', '.join(empty_fields)}")
            return False
            
    except Exception as e:
        print(f"❌ Error probando estructura: {e}")
        return False

if __name__ == "__main__":
    verify_system_data()
    test_data_structure()