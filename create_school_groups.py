import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')
django.setup()

from django.contrib.auth.models import User
from authentication.models import UserGroup, GroupMembership

def create_school_groups():
    """Crear grupos académicos para el colegio"""
    print("=== Creando grupos académicos del colegio ===")
    
    # Obtener usuario administrador como creador
    try:
        admin_user = User.objects.get(username='admin')
    except User.DoesNotExist:
        print("❌ Error: Usuario administrador no encontrado")
        return
    
    # Datos de los grupos a crear
    groups_data = [
        {
            'name': 'Primaria',
            'description': 'Grupo de estudiantes y profesores de educación primaria (grados 1° a 5°)',
            'group_type': 'academic'
        },
        {
            'name': 'Bachillerato A',
            'description': 'Grupo de estudiantes y profesores de bachillerato - Sección A (grados 6° a 11°)',
            'group_type': 'academic'
        },
        {
            'name': 'Bachillerato B',
            'description': 'Grupo de estudiantes y profesores de bachillerato - Sección B (grados 6° a 11°)',
            'group_type': 'academic'
        }
    ]
    
    # Crear los grupos
    created_groups = []
    for group_data in groups_data:
        try:
            # Verificar si el grupo ya existe
            if UserGroup.objects.filter(name=group_data['name']).exists():
                print(f"⚠️  El grupo '{group_data['name']}' ya existe")
                group = UserGroup.objects.get(name=group_data['name'])
            else:
                # Crear el grupo
                group = UserGroup.objects.create(
                    name=group_data['name'],
                    description=group_data['description'],
                    group_type=group_data['group_type'],
                    created_by=admin_user,
                    is_public=True,
                    allow_self_join=False
                )
                print(f"✅ Grupo '{group_data['name']}' creado exitosamente")
            
            created_groups.append(group)
            
            # Agregar al administrador como líder del grupo
            membership, created = GroupMembership.objects.get_or_create(
                user=admin_user,
                group=group,
                defaults={
                    'role': 'leader',
                    'added_by': admin_user,
                    'is_active': True
                }
            )
            
            if created:
                print(f"   👤 Administrador agregado como líder")
            else:
                print(f"   👤 Administrador ya era miembro del grupo")
                
        except Exception as e:
            print(f"❌ Error creando grupo '{group_data['name']}': {e}")
    
    print(f"\n📊 Resumen:")
    print(f"   🏫 Grupos creados: {len(created_groups)}")
    
    # Agregar otros usuarios a los grupos si existen
    print(f"\n👥 Asignando miembros a los grupos...")
    
    # Obtener otros usuarios
    users_to_assign = [
        {'username': 'profesor', 'groups': ['Primaria', 'Bachillerato A'], 'role': 'moderator'},
        {'username': 'secretario', 'groups': ['Primaria', 'Bachillerato A', 'Bachillerato B'], 'role': 'member'},
        {'username': 'ana', 'groups': ['Bachillerato B'], 'role': 'member'},
    ]
    
    for user_info in users_to_assign:
        try:
            user = User.objects.get(username=user_info['username'])
            
            for group_name in user_info['groups']:
                try:
                    group = UserGroup.objects.get(name=group_name)
                    
                    # Verificar si ya es miembro
                    if GroupMembership.objects.filter(user=user, group=group, is_active=True).exists():
                        print(f"   ⚠️  {user.get_full_name()} ya es miembro de '{group_name}'")
                        continue
                    
                    # Crear membresía
                    membership = GroupMembership.objects.create(
                        user=user,
                        group=group,
                        role=user_info['role'],
                        added_by=admin_user,
                        is_active=True
                    )
                    
                    print(f"   ✅ {user.get_full_name()} agregado a '{group_name}' como {membership.get_role_display()}")
                    
                except UserGroup.DoesNotExist:
                    print(f"   ❌ Grupo '{group_name}' no encontrado")
                    
        except User.DoesNotExist:
            print(f"   ❌ Usuario '{user_info['username']}' no encontrado")
    
    # Mostrar estadísticas finales
    print(f"\n📈 Estadísticas de grupos:")
    for group in created_groups:
        print(f"   🏫 {group.name}:")
        print(f"      👥 Miembros: {group.member_count}")
        print(f"      👑 Líderes: {group.leaders_count}")
        print(f"      📋 Tipo: {group.get_group_type_display()}")
        print(f"      🔄 Estado: {'Activo' if group.is_active else 'Inactivo'}")
        print()

if __name__ == "__main__":
    create_school_groups()