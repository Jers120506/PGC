#!/usr/bin/env python
"""
Script para crear grupos escolares realistas
Crea grados académicos con profesores monitores y estudiantes asignados
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
from authentication.models import UserGroup, GroupMembership

def create_school_groups():
    """Crear grupos académicos realistas para la escuela"""
    
    print("🏫 Creando estructura de grupos escolares...")
    
    try:
        with transaction.atomic():
            # Obtener usuarios
            admin_user = User.objects.filter(username='admin').first()
            if not admin_user:
                print("❌ Error: Usuario admin no encontrado")
                return
            
            teachers = list(User.objects.filter(profile__role='teacher', is_active=True))
            students = list(User.objects.filter(profile__role='student', is_active=True))
            
            print(f"📊 Usuarios disponibles:")
            print(f"   - Profesores: {len(teachers)}")
            print(f"   - Estudiantes: {len(students)}")
            
            if not teachers:
                print("⚠️  No hay profesores disponibles. Creando algunos...")
                # Crear profesores de ejemplo
                for i in range(1, 6):
                    user = User.objects.create_user(
                        username=f'profesor{i}',
                        email=f'profesor{i}@colegio.edu.co',
                        first_name=f'Profesor{i}',
                        last_name='Ejemplo',
                        password='profesor123'
                    )
                    user.profile.role = 'teacher'
                    user.profile.subject_area = ['Matemáticas', 'Español', 'Ciencias', 'Sociales', 'Inglés'][i-1]
                    user.profile.save()
                    teachers.append(user)
                print(f"✅ Creados {len(teachers)} profesores de ejemplo")
            
            # Eliminar grupos existentes para empezar limpio
            existing_groups = UserGroup.objects.all()
            if existing_groups.exists():
                print(f"🗑️  Eliminando {existing_groups.count()} grupos existentes...")
                existing_groups.delete()
            
            # Estructura de grados escolares
            school_structure = [
                # Primaria
                {'name': 'Primero A', 'type': 'academic', 'level': 'primaria', 'max_students': 25},
                {'name': 'Primero B', 'type': 'academic', 'level': 'primaria', 'max_students': 25},
                {'name': 'Segundo A', 'type': 'academic', 'level': 'primaria', 'max_students': 25},
                {'name': 'Tercero A', 'type': 'academic', 'level': 'primaria', 'max_students': 25},
                {'name': 'Cuarto A', 'type': 'academic', 'level': 'primaria', 'max_students': 25},
                {'name': 'Quinto A', 'type': 'academic', 'level': 'primaria', 'max_students': 25},
                
                # Bachillerato
                {'name': 'Sexto A', 'type': 'academic', 'level': 'bachillerato', 'max_students': 30},
                {'name': 'Séptimo A', 'type': 'academic', 'level': 'bachillerato', 'max_students': 30},
                {'name': 'Octavo A', 'type': 'academic', 'level': 'bachillerato', 'max_students': 30},
                {'name': 'Noveno A', 'type': 'academic', 'level': 'bachillerato', 'max_students': 30},
                {'name': 'Décimo A', 'type': 'academic', 'level': 'bachillerato', 'max_students': 30},
                {'name': 'Once A', 'type': 'academic', 'level': 'bachillerato', 'max_students': 30},
                
                # Grupos Departamentales
                {'name': 'Profesores de Matemáticas', 'type': 'departmental', 'level': 'departamental', 'max_students': 0},
                {'name': 'Profesores de Español', 'type': 'departmental', 'level': 'departamental', 'max_students': 0},
                {'name': 'Profesores de Ciencias', 'type': 'departmental', 'level': 'departamental', 'max_students': 0},
                {'name': 'Coordinación Académica', 'type': 'functional', 'level': 'administrativo', 'max_students': 0},
                {'name': 'Consejo Directivo', 'type': 'functional', 'level': 'administrativo', 'max_students': 0},
            ]
            
            created_groups = []
            student_index = 0
            teacher_index = 0
            
            for group_info in school_structure:
                # Seleccionar profesor monitor
                monitor = None
                if group_info['level'] in ['primaria', 'bachillerato']:
                    # Para grados académicos, asignar un profesor como director de grupo
                    if teacher_index < len(teachers):
                        monitor = teachers[teacher_index]
                        teacher_index += 1
                        if teacher_index >= len(teachers):
                            teacher_index = 0  # Reiniciar si se acaban los profesores
                
                # Crear el grupo
                group = UserGroup.objects.create(
                    name=group_info['name'],
                    description=f"Grupo {group_info['name']} - {group_info['level'].title()}",
                    group_type=group_info['type'],
                    created_by=admin_user,
                    is_public=True,
                    is_active=True
                )
                
                # Agregar admin como moderador
                GroupMembership.objects.create(
                    user=admin_user,
                    group=group,
                    role='moderator',
                    added_by=admin_user
                )
                
                # Agregar profesor monitor como líder si existe
                if monitor:
                    GroupMembership.objects.create(
                        user=monitor,
                        group=group,
                        role='leader',
                        added_by=admin_user
                    )
                    print(f"👨‍🏫 {monitor.get_full_name()} asignado como director de {group.name}")
                
                # Agregar estudiantes para grupos académicos
                if group_info['level'] in ['primaria', 'bachillerato'] and group_info['max_students'] > 0:
                    students_to_add = min(group_info['max_students'], len(students) - student_index)
                    if students_to_add > 0:
                        group_students = students[student_index:student_index + students_to_add]
                        for student in group_students:
                            GroupMembership.objects.create(
                                user=student,
                                group=group,
                                role='member',
                                added_by=admin_user
                            )
                        student_index += students_to_add
                        print(f"📚 {len(group_students)} estudiantes agregados a {group.name}")
                
                # Agregar profesores a grupos departamentales
                elif group_info['level'] == 'departamental':
                    # Agregar profesores relacionados con el área
                    subject_areas = {
                        'Profesores de Matemáticas': ['Matemáticas', 'Física'],
                        'Profesores de Español': ['Español', 'Literatura', 'Humanidades'],
                        'Profesores de Ciencias': ['Ciencias', 'Biología', 'Química', 'Física']
                    }
                    
                    relevant_areas = subject_areas.get(group.name, [])
                    for teacher in teachers:
                        if hasattr(teacher.profile, 'subject_area') and teacher.profile.subject_area in relevant_areas:
                            if not GroupMembership.objects.filter(user=teacher, group=group).exists():
                                GroupMembership.objects.create(
                                    user=teacher,
                                    group=group,
                                    role='member',
                                    added_by=admin_user
                                )
                
                # Agregar directivos a grupos administrativos
                elif group_info['level'] == 'administrativo':
                    # Agregar algunos profesores senior como coordinadores
                    coordinators = teachers[:3]  # Primeros 3 profesores como coordinadores
                    for coordinator in coordinators:
                        if not GroupMembership.objects.filter(user=coordinator, group=group).exists():
                            GroupMembership.objects.create(
                                user=coordinator,
                                group=group,
                                role='leader' if group.name == 'Consejo Directivo' else 'moderator',
                                added_by=admin_user
                            )
                
                created_groups.append(group)
                print(f"✅ Grupo '{group.name}' creado con {group.member_count} miembros")
            
            # Mostrar resumen
            print("\n📊 RESUMEN DE GRUPOS CREADOS:")
            print("=" * 50)
            
            academic_groups = [g for g in created_groups if g.group_type == 'academic']
            departmental_groups = [g for g in created_groups if g.group_type == 'departmental']
            functional_groups = [g for g in created_groups if g.group_type == 'functional']
            
            print(f"📚 Grupos Académicos: {len(academic_groups)}")
            for group in academic_groups:
                leader = group.memberships.filter(role='leader').first()
                leader_name = leader.user.get_full_name() if leader else "Sin director"
                print(f"   - {group.name}: {group.member_count} miembros (Director: {leader_name})")
            
            print(f"\n🏢 Grupos Departamentales: {len(departmental_groups)}")
            for group in departmental_groups:
                print(f"   - {group.name}: {group.member_count} miembros")
            
            print(f"\n⚙️  Grupos Funcionales: {len(functional_groups)}")
            for group in functional_groups:
                print(f"   - {group.name}: {group.member_count} miembros")
            
            print(f"\n🎯 Total de grupos creados: {len(created_groups)}")
            print(f"👥 Total de membresías creadas: {GroupMembership.objects.count()}")
            
            print("\n🎉 ¡Estructura de grupos escolares creada exitosamente!")
            print("\n💡 Ahora puedes:")
            print("   - Ver los grupos en /administration/admin/groups/")
            print("   - Gestionar miembros de cada grupo")
            print("   - Asignar profesores adicionales")
            print("   - Crear más grupos según sea necesario")
            
    except Exception as e:
        print(f"❌ Error al crear grupos: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    create_school_groups()