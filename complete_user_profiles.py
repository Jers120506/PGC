#!/usr/bin/env python
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')
django.setup()

from django.contrib.auth.models import User
from authentication.models import UserProfile
from datetime import date, datetime

def complete_user_profiles():
    """Completar información de los usuarios existentes"""
    print("=== Completando información de usuarios existentes ===\n")
    
    # Datos para cada usuario
    users_data = {
        'admin': {
            'first_name': 'María José',
            'last_name': 'Rodríguez González',
            'email': 'admin@colegialabalsa.edu.co',
            'profile_data': {
                'phone': '+57 (1) 234-5678',
                'mobile_phone': '+57 310 123 4567',
                'bio': 'Administradora del Colegio La Balsa con más de 15 años de experiencia en gestión educativa. Comprometida con la excelencia académica y el desarrollo integral de los estudiantes.',
                'date_of_birth': date(1980, 3, 15),
                'gender': 'F',
                'identification_number': '52123456',
                'address': 'Carrera 15 # 45-23, Barrio Centro',
                'city': 'Bogotá',
                'emergency_contact_name': 'Carlos Rodríguez (Esposo)',
                'emergency_contact_phone': '+57 311 987 6543',
                'education_level': 'magister',
                'institution': 'Universidad Javeriana',
                'graduation_year': 2005,
                'professional_title': 'Magíster en Administración Educativa',
                'specialization': 'Gestión Educativa y Liderazgo Pedagógico',
                'years_of_experience': 15,
                'department': 'Dirección General',
                'position': 'Rectora',
                'hire_date': date(2010, 2, 1),
                'work_schedule': 'Lunes a Viernes 7:00 AM - 6:00 PM',
                'notifications_enabled': True,
                'email_notifications': True,
            }
        },
        'secretario': {
            'first_name': 'María Elena',
            'last_name': 'García Rodríguez',
            'email': 'secretaria@colegialabalsa.edu.co',
            'profile_data': {
                'phone': '+57 (1) 234-5679',
                'mobile_phone': '+57 320 456 7890',
                'bio': 'Secretaria académica con amplia experiencia en atención al público y gestión administrativa. Responsable de matrículas, certificados y atención a padres de familia.',
                'date_of_birth': date(1985, 7, 22),
                'gender': 'F',
                'identification_number': '43987654',
                'address': 'Calle 25 # 12-34, Barrio San Luis',
                'city': 'Bogotá',
                'emergency_contact_name': 'Ana García (Hermana)',
                'emergency_contact_phone': '+57 315 234 5678',
                'education_level': 'tecnico',
                'professional_title': 'Técnica en Administración Documental',
                'years_of_experience': 8,
                'department': 'Secretaría Académica',
                'position': 'Secretaria Académica',
                'hire_date': date(2016, 8, 15),
                'work_schedule': 'Lunes a Viernes 7:30 AM - 4:30 PM',
                'notifications_enabled': True,
                'email_notifications': True,
            }
        },
        'profesor': {
            'first_name': 'Carlos Alberto',
            'last_name': 'Martínez Pérez',
            'email': 'profesor@colegialabalsa.edu.co',
            'profile_data': {
                'phone': '+57 (1) 234-5680',
                'mobile_phone': '+57 312 345 6789',
                'bio': 'Profesor de Matemáticas y Física con pasión por la enseñanza y la investigación. Especialista en metodologías activas de aprendizaje y uso de tecnología en el aula.',
                'date_of_birth': date(1978, 11, 8),
                'gender': 'M',
                'identification_number': '79123456',
                'address': 'Transversal 8 # 67-89, Barrio Los Rosales',
                'city': 'Bogotá',
                'emergency_contact_name': 'Lucía Pérez (Esposa)',
                'emergency_contact_phone': '+57 313 876 5432',
                'education_level': 'especialista',
                'institution': 'Universidad Nacional de Colombia',
                'graduation_year': 2002,
                'professional_title': 'Licenciado en Matemáticas y Física',
                'specialization': 'Matemáticas, Física, Cálculo, Trigonometría',
                'years_of_experience': 12,
                'department': 'Ciencias Exactas',
                'work_schedule': 'Lunes a Viernes 7:00 AM - 3:00 PM',
                'notifications_enabled': True,
                'email_notifications': True,
            }
        },
        'ana': {
            'first_name': 'Ana Carolina',
            'last_name': 'Rodríguez Morales',
            'email': 'ana@colegiolabalsa.edu.co',
            'profile_data': {
                'phone': '+57 (1) 234-5681',
                'mobile_phone': '+57 318 765 4321',
                'bio': 'Secretaria de coordinación académica, encargada del seguimiento estudiantil y comunicación con padres de familia. Comprometida con el bienestar estudiantil.',
                'date_of_birth': date(1990, 5, 3),
                'gender': 'F',
                'identification_number': '1023456789',
                'address': 'Diagonal 45 # 23-67, Barrio La Candelaria',
                'city': 'Bogotá',
                'emergency_contact_name': 'Sofía Morales (Madre)',
                'emergency_contact_phone': '+57 314 567 8901',
                'education_level': 'profesional',
                'professional_title': 'Administradora de Empresas',
                'years_of_experience': 3,
                'department': 'Coordinación Académica',
                'position': 'Secretaria de Coordinación',
                'hire_date': date(2021, 3, 1),
                'work_schedule': 'Lunes a Viernes 8:00 AM - 5:00 PM',
                'notifications_enabled': True,
                'email_notifications': True,
            }
        }
    }
    
    updated_count = 0
    
    for username, data in users_data.items():
        try:
            user = User.objects.get(username=username)
            profile = user.profile
            
            print(f"🔄 Actualizando usuario: {username}")
            
            # Actualizar datos básicos del User
            user.first_name = data['first_name']
            user.last_name = data['last_name']
            user.email = data['email']
            user.save()
            
            # Actualizar datos del perfil
            for field_name, value in data['profile_data'].items():
                if hasattr(profile, field_name):
                    setattr(profile, field_name, value)
            
            profile.save()
            
            # Recalcular completitud
            profile.mark_profile_complete()
            
            print(f"   ✅ {data['first_name']} {data['last_name']} - {profile.get_role_display()}")
            print(f"   📊 Completitud: {profile.profile_completion_percentage}%")
            print(f"   📧 Email: {user.email}")
            print(f"   🏢 Cargo: {profile.position or 'No especificado'}")
            print(f"   🎓 Título: {profile.professional_title or 'No especificado'}")
            print("-" * 60)
            
            updated_count += 1
            
        except User.DoesNotExist:
            print(f"❌ Usuario '{username}' no encontrado")
        except Exception as e:
            print(f"❌ Error actualizando '{username}': {str(e)}")
    
    print(f"\n🎉 ¡Actualización completada!")
    print(f"📊 Usuarios actualizados: {updated_count}/{len(users_data)}")
    
    # Mostrar resumen final
    print("\n=== RESUMEN FINAL ===")
    for user in User.objects.all().order_by('profile__role'):
        if hasattr(user, 'profile'):
            print(f"👤 {user.first_name} {user.last_name} (@{user.username})")
            print(f"   🎭 Rol: {user.profile.get_role_display()}")
            print(f"   📊 Completitud: {user.profile.profile_completion_percentage}%")
            print(f"   ✅ Estado: {'Completo' if user.profile.is_profile_complete else 'Incompleto'}")
            print()

if __name__ == '__main__':
    complete_user_profiles()