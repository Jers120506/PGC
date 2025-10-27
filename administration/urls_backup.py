from django.urls import path
from . import views

app_name = 'administration'

urlpatterns = [
    # Dashboard principal (admin y secretaría)
    path('', views.SecretaryDashboardView.as_view(), name='dashboard'),
    
    # Funciones específicas del administrador
    path('admin/users/', views.AdminUserManagementView.as_view(), name='admin_users'),
    path('admin/system-config/', views.SystemConfigView.as_view(), name='system_config'),
    path('admin/backup/', views.BackupManagementView.as_view(), name='backup_management'),
    
    # Panel para profesores - entrada de calificaciones
    path('teacher/grades/', views.TeacherGradeEntryView.as_view(), name='teacher_grades'),
    
    # Control de asistencia para profesores
    path('teacher/attendance/', views.AttendanceControlView.as_view(), name='teacher_attendance'),
    
    # Gestión de estudiantes para secretaría
    path('students/', views.StudentManagementView.as_view(), name='student_management'),
    path('students/<int:student_id>/', views.StudentDetailView.as_view(), name='student_detail'),
    
    # Generación de reportes PDF
    path('reports/', views.ReportGeneratorView.as_view(), name='report_generator'),
    path('reports/bulletin/<int:student_id>/', views.generate_bulletin_pdf, name='generate_bulletin'),
    path('reports/course-list/<int:course_id>/', views.generate_course_list_pdf, name='generate_course_list'),
    
    # APIs para funcionalidad AJAX
    path('api/save-grade/', views.save_grade_api, name='save_grade_api'),
    path('api/save-attendance/', views.save_attendance_api, name='save_attendance_api'),
    path('api/search-students/', views.quick_student_search_api, name='quick_student_search'),
    path('api/create-student/', views.create_student_api, name='create_student_api'),
    
    # APIs para gestión de usuarios (solo administradores)
    path('api/users/toggle-status/', views.toggle_user_status_api, name='toggle_user_status_api'),
    path('api/users/delete/', views.delete_user_api, name='delete_user_api'),
    path('api/users/create/', views.create_user_api, name='create_user_api'),
    path('api/users/reset-password/', views.reset_password_api, name='reset_password_api'),
]