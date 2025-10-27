#!/usr/bin/env python
"""
Script para crear usuarios de prueba para la escuela
Crea profesores adicionales y estudiantes para poblar los grupos
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

def create_test_users():
    """Crear usuarios de prueba para la escuela"""
    
    print("👥 Creando usuarios de prueba para la escuela...")
    
    try:
        with transaction.atomic():
            # Crear profesores adicionales
            teachers_data = [
                {
                    'username': 'prof_matematicas',
                    'first_name': 'María',
                    'last_name': 'Rodríguez',
                    'email': 'maria.rodriguez@colegio.edu.co',
                    'subject_area': 'Matemáticas',
                    'department': 'Ciencias Exactas'
                },
                {
                    'username': 'prof_espanol',
                    'first_name': 'Juan',
                    'last_name': 'García',
                    'email': 'juan.garcia@colegio.edu.co',
                    'subject_area': 'Español',
                    'department': 'Humanidades'
                },
                {
                    'username': 'prof_ciencias',
                    'first_name': 'Ana',
                    'last_name': 'López',
                    'email': 'ana.lopez@colegio.edu.co',
                    'subject_area': 'Ciencias Naturales',
                    'department': 'Ciencias'
                },
                {
                    'username': 'prof_sociales',
                    'first_name': 'Pedro',
                    'last_name': 'Martín',
                    'email': 'pedro.martin@colegio.edu.co',
                    'subject_area': 'Ciencias Sociales',
                    'department': 'Sociales'
                },
                {
                    'username': 'prof_ingles',
                    'first_name': 'Laura',
                    'last_name': 'González',
                    'email': 'laura.gonzalez@colegio.edu.co',
                    'subject_area': 'Inglés',
                    'department': 'Idiomas'
                },
                {
                    'username': 'prof_educfisica',
                    'first_name': 'Carlos',
                    'last_name': 'Ruiz',
                    'email': 'carlos.ruiz@colegio.edu.co',
                    'subject_area': 'Educación Física',
                    'department': 'Deportes'
                },
                {
                    'username': 'prof_informatica',
                    'first_name': 'Sofía',
                    'last_name': 'Hernández',
                    'email': 'sofia.hernandez@colegio.edu.co',
                    'subject_area': 'Informática',
                    'department': 'Tecnología'
                },
                {
                    'username': 'prof_arte',
                    'first_name': 'Miguel',
                    'last_name': 'Torres',
                    'email': 'miguel.torres@colegio.edu.co',
                    'subject_area': 'Educación Artística',
                    'department': 'Artes'
                }
            ]
            
            created_teachers = 0
            for teacher_data in teachers_data:
                if not User.objects.filter(username=teacher_data['username']).exists():
                    user = User.objects.create_user(
                        username=teacher_data['username'],
                        email=teacher_data['email'],
                        first_name=teacher_data['first_name'],
                        last_name=teacher_data['last_name'],
                        password='profesor123'
                    )
                    
                    # Configurar perfil
                    user.profile.role = 'teacher'
                    user.profile.subject_area = teacher_data['subject_area']
                    user.profile.department = teacher_data['department']
                    user.profile.phone = f'300-555-{str(created_teachers + 1).zfill(4)}'
                    user.profile.birth_date = '1980-01-01'
                    user.profile.save()
                    
                    created_teachers += 1
                    print(f"✅ Profesor creado: {user.get_full_name()} - {teacher_data['subject_area']}")
            
            # Crear estudiantes de primaria y bachillerato
            student_names = [
                ('Alejandro', 'Moreno'), ('Valentina', 'Castro'), ('Sebastián', 'Ramírez'),
                ('Isabella', 'Jiménez'), ('Santiago', 'Vargas'), ('Camila', 'Herrera'),
                ('Mateo', 'Rojas'), ('Sofía', 'Mendoza'), ('Nicolás', 'Guerrero'),
                ('Emma', 'Córdoba'), ('Diego', 'Peña'), ('Lucía', 'Salazar'),
                ('Andrés', 'Vega'), ('Mariana', 'Ortiz'), ('Daniel', 'Silva'),
                ('Gabriela', 'Restrepo'), ('Samuel', 'Morales'), ('Natalia', 'Aguilar'),
                ('Tomás', 'Delgado'), ('Paulina', 'Sánchez'), ('Julián', 'Romero'),
                ('Violeta', 'Pardo'), ('Felipe', 'Mejía'), ('Antonella', 'Carvajal'),
                ('Emilio', 'Giraldo'), ('Valeria', 'Molina'), ('Joaquín', 'Zapata'),
                ('Renata', 'Osorio'), ('Maximiliano', 'Castaño'), ('Delfina', 'Quintero'),
                ('Agustín', 'Acosta'), ('Catalina', 'Bermúdez'), ('Benjamín', 'Cardona'),
                ('Miranda', 'Durán'), ('Lorenzo', 'Escobar'), ('Amparo', 'Franco'),
                ('Gael', 'Galvis'), ('Esperanza', 'Henao'), ('Thiago', 'Jaramillo'),
                ('Paloma', 'León'), ('Ian', 'Medina'), ('Alma', 'Navarro'),
                ('Bruno', 'Orozco'), ('Pilar', 'Posada'), ('Luca', 'Ríos'),
                ('Clementina', 'Suárez'), ('Dante', 'Uribe'), ('Estrella', 'Valencia'),
                ('Enzo', 'Vélez'), ('Aurora', 'Villegas')
            ]
            
            created_students = 0
            grades = [
                'primero', 'segundo', 'tercero', 'cuarto', 'quinto',  # Primaria
                'sexto', 'septimo', 'octavo', 'noveno', 'decimo', 'once'  # Bachillerato
            ]
            
            for i, (first_name, last_name) in enumerate(student_names):
                grade = grades[i % len(grades)]
                username = f'est_{first_name.lower()}_{last_name.lower()}'
                
                if not User.objects.filter(username=username).exists():
                    user = User.objects.create_user(
                        username=username,
                        email=f'{first_name.lower()}.{last_name.lower()}@estudiantes.colegio.edu.co',
                        first_name=first_name,
                        last_name=last_name,
                        password='estudiante123'
                    )
                    
                    # Configurar perfil
                    user.profile.role = 'student'
                    user.profile.grade = grade
                    user.profile.academic_year = '2025'
                    user.profile.phone = f'321-555-{str(i + 1).zfill(4)}'
                    
                    # Edad aproximada según el grado
                    grade_ages = {
                        'primero': 6, 'segundo': 7, 'tercero': 8, 'cuarto': 9, 'quinto': 10,
                        'sexto': 11, 'septimo': 12, 'octavo': 13, 'noveno': 14, 'decimo': 15, 'once': 16
                    }
                    age = grade_ages.get(grade, 12)
                    birth_year = 2025 - age
                    user.profile.birth_date = f'{birth_year}-06-15'
                    
                    user.profile.save()
                    
                    created_students += 1
                    print(f"✅ Estudiante creado: {user.get_full_name()} - Grado {grade.title()}")
            
            # Crear algunos usuarios administrativos
            admin_users = [
                {
                    'username': 'coordinador_academico',
                    'first_name': 'Roberto',
                    'last_name': 'Serrano',
                    'email': 'coordinacion@colegio.edu.co',
                    'role': 'coordinator'
                },
                {
                    'username': 'secretaria',
                    'first_name': 'Carmen',
                    'last_name': 'Villamil',
                    'email': 'secretaria@colegio.edu.co',
                    'role': 'secretary'
                },
                {
                    'username': 'psicologo',
                    'first_name': 'Andrea',
                    'last_name': 'Montoya',
                    'email': 'psicologia@colegio.edu.co',
                    'role': 'counselor'
                }
            ]
            
            created_admin = 0
            for admin_data in admin_users:
                if not User.objects.filter(username=admin_data['username']).exists():
                    user = User.objects.create_user(
                        username=admin_data['username'],
                        email=admin_data['email'],
                        first_name=admin_data['first_name'],
                        last_name=admin_data['last_name'],
                        password='admin123'
                    )
                    
                    user.profile.role = admin_data['role']
                    user.profile.phone = f'310-555-{str(created_admin + 1).zfill(4)}'
                    user.profile.birth_date = '1975-01-01'
                    user.profile.save()
                    
                    created_admin += 1
                    print(f"✅ Personal administrativo creado: {user.get_full_name()} - {admin_data['role'].title()}")
            
            print("\n📊 RESUMEN DE USUARIOS CREADOS:")
            print("=" * 50)
            print(f"👨‍🏫 Profesores creados: {created_teachers}")
            print(f"👨‍🎓 Estudiantes creados: {created_students}")
            print(f"👔 Personal administrativo: {created_admin}")
            
            # Mostrar totales del sistema
            total_users = User.objects.count()
            total_teachers = User.objects.filter(profile__role='teacher').count()
            total_students = User.objects.filter(profile__role='student').count()
            total_admin = User.objects.filter(profile__role='admin').count()
            
            print(f"\n🎯 TOTALES EN EL SISTEMA:")
            print(f"   Total usuarios: {total_users}")
            print(f"   Profesores: {total_teachers}")
            print(f"   Estudiantes: {total_students}")
            print(f"   Administradores: {total_admin}")
            print(f"   Otros roles: {total_users - total_teachers - total_students - total_admin}")
            
            print("\n🎉 ¡Usuarios de prueba creados exitosamente!")
            print("\n💡 Credenciales de acceso:")
            print("   - Profesores: usuario / profesor123")
            print("   - Estudiantes: usuario / estudiante123")
            print("   - Administrativos: usuario / admin123")
            
    except Exception as e:
        print(f"❌ Error al crear usuarios: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    create_test_users()