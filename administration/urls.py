from django.urls import path
from . import views

app_name = 'administration'

urlpatterns = [
    # Dashboard principal de administración
    path('', views.AdminDashboardView.as_view(), name='dashboard'),
    
    # Vista de test para botones
    path('test-users/', views.TestUsersView.as_view(), name='test_users'),
    
    # Funciones específicas del administrador
    path('admin/users/', views.AdminUserManagementView.as_view(), name='admin_users'),
    path('admin/profiles/', views.ProfileManagementView.as_view(), name='profile_management'),
    path('admin/profiles/<int:user_id>/', views.ProfileDetailView.as_view(), name='profile_detail'),
    path('admin/groups/', views.GroupManagementView.as_view(), name='group_management'),
    path('admin/groups/<int:group_id>/', views.GroupDetailView.as_view(), name='group_detail'),
    path('admin/students/', views.StudentManagementView.as_view(), name='student_management'),
    path('admin/system-config/', views.SystemConfigView.as_view(), name='system_config'),
    path('admin/backup/', views.BackupManagementView.as_view(), name='backup_management'),
    
    # APIs para gestión de usuarios (solo administradores)
    path('api/users/toggle-status/', views.toggle_user_status_api, name='toggle_user_status_api'),
    path('api/users/delete/', views.delete_user_api, name='delete_user_api'),
    path('api/users/create/', views.create_user_api, name='create_user_api'),
    path('api/users/update/', views.update_user_api, name='update_user_api'),
    path('api/users/reset-password/', views.reset_password_api, name='reset_password_api'),
    path('api/users/<int:user_id>/', views.get_user_details_api, name='get_user_details_api'),
    
    # APIs para gestión de perfiles
    path('api/profiles/update/', views.update_profile_api, name='update_profile_api'),
    path('api/profiles/upload-avatar/', views.upload_avatar_api, name='upload_avatar_api'),
    path('api/profiles/stats/', views.profile_stats_api, name='profile_stats_api'),
    path('api/profiles/export/', views.export_profiles_api, name='export_profiles_api'),
    
    # APIs para gestión de grupos
    path('api/groups/create/', views.create_group_api, name='create_group_api'),
    path('api/groups/update/', views.update_group_api, name='update_group_api'),
    path('api/groups/delete/', views.delete_group_api, name='delete_group_api'),
    path('api/groups/add-member/', views.add_group_member_api, name='add_group_member_api'),
    path('api/groups/remove-member/', views.remove_group_member_api, name='remove_group_member_api'),
    
    # APIs para gestión de directores de grupo/cursos
    path('api/assign-teacher/', views.assign_teacher_to_course_api, name='assign_teacher_api'),
    path('api/remove-teacher/', views.remove_teacher_from_course_api, name='remove_teacher_api'),
    
    # APIs para gestión de estudiantes
    path('api/students/create/', views.create_student_enrollment_api, name='create_student_enrollment_api'),
    path('api/students/update/', views.update_student_enrollment_api, name='update_student_enrollment_api'),
    
    # APIs para gestión académica
    path('api/academic-years/create/', views.create_academic_year_api, name='create_academic_year_api'),
    path('api/academic-years/update/', views.update_academic_year_api, name='update_academic_year_api'),
    path('api/academic-years/delete/', views.delete_academic_year_api, name='delete_academic_year_api'),
    path('api/academic-years/set-current/', views.set_current_academic_year_api, name='set_current_academic_year_api'),
    
    path('api/grades/create/', views.create_grade_api, name='create_grade_api'),
    path('api/grades/update/', views.update_grade_api, name='update_grade_api'),
    path('api/grades/delete/', views.delete_grade_api, name='delete_grade_api'),
    
    path('api/subjects/create/', views.create_subject_api, name='create_subject_api'),
    path('api/subjects/update/', views.update_subject_api, name='update_subject_api'),
    path('api/subjects/delete/', views.delete_subject_api, name='delete_subject_api'),
    
    path('api/courses/create/', views.create_course_api, name='create_course_api'),
    path('api/courses/update/', views.update_course_api, name='update_course_api'),
    path('api/courses/delete/', views.delete_course_api, name='delete_course_api'),
    path('api/students/change-status/', views.change_student_status_api, name='change_student_status_api'),
    path('api/students/enroll/', views.enroll_student_api, name='enroll_student_api'),
    path('api/students/export/', views.export_students_excel_api, name='export_students_excel_api'),
]