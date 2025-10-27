#!/usr/bin/env python
"""
Script para verificar y crear datos necesarios para el sistema de horarios
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
    Course, Subject, Classroom, TimeSlot, AcademicYear, Grade
)

def create_admin_user():
    """Crear usuario admin si no existe"""
    admin_user, created = User.objects.get_or_create(
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
    
    if created or not admin_user.check_password('admin123'):
        admin_user.set_password('admin123')
        admin_user.save()
        print(f"✅ Usuario admin {'creado' if created else 'actualizado'}")
    
    # Crear perfil si no existe
    profile, profile_created = UserProfile.objects.get_or_create(
        user=admin_user,
        defaults={
            'role': 'admin',
            'phone': '123456789',
            'address': 'Admin Address',
            'date_of_birth': '1990-01-01',
            'profile_completion_percentage': 100
        }
    )
    
    if profile_created:
        print("✅ Perfil de admin creado")
    else:
        profile.role = 'admin'
        profile.save()
        print("✅ Perfil de admin actualizado")

def verify_data():
    """Verificar que los datos necesarios existen"""
    print("\n🔍 VERIFICANDO DATOS DEL SISTEMA:")
    print("=" * 50)
    
    # Verificar usuarios
    total_users = User.objects.count()
    teachers = User.objects.filter(profile__role='teacher', is_active=True)
    print(f"👥 Usuarios totales: {total_users}")
    print(f"👨‍🏫 Profesores: {teachers.count()}")
    
    # Verificar datos académicos
    courses = Course.objects.filter(is_active=True)
    subjects = Subject.objects.all()
    classrooms = Classroom.objects.filter(is_active=True)
    time_slots = TimeSlot.objects.filter(is_active=True)
    
    print(f"📚 Cursos activos: {courses.count()}")
    print(f"📖 Materias: {subjects.count()}")
    print(f"🏫 Salones activos: {classrooms.count()}")
    print(f"⏰ Franjas horarias: {time_slots.count()}")
    
    # Mostrar detalles si hay pocos datos
    if teachers.count() > 0:
        print(f"\n👨‍🏫 PROFESORES DISPONIBLES:")
        for teacher in teachers[:5]:
            print(f"   • {teacher.get_full_name()} ({teacher.username})")
    
    if courses.count() > 0:
        print(f"\n📚 CURSOS DISPONIBLES:")
        for course in courses[:5]:
            print(f"   • {course}")
    
    if classrooms.count() > 0:
        print(f"\n🏫 SALONES DISPONIBLES:")
        for classroom in classrooms[:5]:
            print(f"   • {classroom.name} - Cap: {classroom.capacity}")
    
    if time_slots.count() > 0:
        print(f"\n⏰ FRANJAS HORARIAS:")
        for slot in time_slots[:5]:
            print(f"   • {slot.name}: {slot.start_time} - {slot.end_time}")
    
    return {
        'teachers': teachers.count(),
        'courses': courses.count(),
        'subjects': subjects.count(),
        'classrooms': classrooms.count(),
        'time_slots': time_slots.count()
    }

def create_teacher_if_needed():
    """Crear un profesor de prueba si no hay ninguno"""
    teachers = User.objects.filter(profile__role='teacher', is_active=True)
    
    if teachers.count() == 0:
        print("\n⚠️ No hay profesores disponibles. Creando profesor de prueba...")
        
        teacher_user, created = User.objects.get_or_create(
            username='profesor1',
            defaults={
                'email': 'profesor1@test.com',
                'first_name': 'Juan',
                'last_name': 'Pérez',
                'is_active': True
            }
        )
        
        if created:
            teacher_user.set_password('profesor123')
            teacher_user.save()
        
        profile, profile_created = UserProfile.objects.get_or_create(
            user=teacher_user,
            defaults={
                'role': 'teacher',
                'phone': '123456789',
                'address': 'Dirección del profesor',
                'date_of_birth': '1985-01-01',
                'profile_completion_percentage': 100
            }
        )
        
        if profile_created or profile.role != 'teacher':
            profile.role = 'teacher'
            profile.save()
        
        print(f"✅ Profesor creado: {teacher_user.get_full_name()}")
        return True
    
    return False

def test_api_response():
    """Probar la API de recursos"""
    print(f"\n🧪 PROBANDO API DE RECURSOS:")
    print("=" * 50)
    
    try:
        import requests
        
        # Primero hacer login
        session = requests.Session()
        
        # Obtener CSRF token
        login_page = session.get('http://127.0.0.1:8000/auth/login/')
        if login_page.status_code == 200:
            print("✅ Página de login accesible")
        
        # Hacer login
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        # Extraer CSRF token
        import re
        csrf_token = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)', login_page.text)
        if csrf_token:
            login_data['csrfmiddlewaretoken'] = csrf_token.group(1)
            print("✅ CSRF token obtenido")
        
        login_response = session.post('http://127.0.0.1:8000/auth/login/', data=login_data)
        
        if login_response.status_code == 302 or 'dashboard' in login_response.url:
            print("✅ Login exitoso")
            
            # Probar API de recursos
            api_response = session.get('http://127.0.0.1:8000/academic-system/schedules/resources/')
            
            print(f"📡 Status API: {api_response.status_code}")
            print(f"📋 Content-Type: {api_response.headers.get('content-type')}")
            
            if api_response.status_code == 200:
                try:
                    data = api_response.json()
                    if data.get('status') == 'success':
                        api_data = data.get('data', {})
                        print("✅ API funcionando correctamente:")
                        print(f"   • Cursos: {len(api_data.get('courses', []))}")
                        print(f"   • Profesores: {len(api_data.get('teachers', []))}")
                        print(f"   • Salones: {len(api_data.get('classrooms', []))}")
                        print(f"   • Materias: {len(api_data.get('subjects', []))}")
                        print(f"   • Franjas: {len(api_data.get('time_slots', []))}")
                        return True
                    else:
                        print(f"❌ Error en API: {data.get('message')}")
                except Exception as e:
                    print(f"❌ Error procesando JSON: {e}")
                    print(f"Respuesta: {api_response.text[:200]}")
            else:
                print(f"❌ Error en API: {api_response.status_code}")
                print(f"Respuesta: {api_response.text[:200]}")
        else:
            print(f"❌ Error en login: {login_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error en prueba de API: {e}")
    
    return False

def main():
    """Función principal"""
    print("🚀 VERIFICACIÓN Y CORRECCIÓN DEL SISTEMA DE HORARIOS")
    print("=" * 60)
    
    # 1. Crear usuario admin
    create_admin_user()
    
    # 2. Verificar datos
    stats = verify_data()
    
    # 3. Crear profesor si es necesario
    teacher_created = create_teacher_if_needed()
    
    # 4. Si se creó un profesor, verificar de nuevo
    if teacher_created:
        stats = verify_data()
    
    # 5. Probar API
    api_works = test_api_response()
    
    print(f"\n📊 RESUMEN:")
    print("=" * 30)
    print(f"👨‍🏫 Profesores: {stats['teachers']}")
    print(f"📚 Cursos: {stats['courses']}")
    print(f"📖 Materias: {stats['subjects']}")
    print(f"🏫 Salones: {stats['classrooms']}")
    print(f"⏰ Franjas: {stats['time_slots']}")
    print(f"🔗 API funciona: {'✅' if api_works else '❌'}")
    
    if all(v > 0 for v in stats.values()) and api_works:
        print(f"\n🎉 ¡SISTEMA LISTO! Puedes crear horarios ahora.")
        print(f"🔑 Login: admin / admin123")
        print(f"🌐 URL: http://127.0.0.1:8000/academic-system/schedules/")
    else:
        print(f"\n⚠️ Faltan datos. Ejecuta el script de mejoras primero:")
        print(f"python complete_system_improvements.py")

if __name__ == "__main__":
    main()