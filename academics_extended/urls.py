from django.urls import path
from . import views
from . import schedule_views

app_name = 'academics_extended'

urlpatterns = [
    # Dashboard principal - TEMPORALMENTE SIMPLIFICADO
    path('', views.AcademicDashboardView.as_view(), name='dashboard'),
    
    # APIs para Sistema de Horarios (DEBEN IR ANTES DE LA VISTA GENERAL)
    path('schedules/api/', schedule_views.schedules_list_api, name='schedules_list_api'),
    path('schedules/resources/', schedule_views.schedule_resources_api, name='schedule_resources_api'),
    path('schedules/create/', schedule_views.create_schedule_api, name='create_schedule_api'),
    path('schedules/matrix/', schedule_views.schedule_matrix_api, name='schedule_matrix_api'),
    path('schedules/validate-conflicts/', schedule_views.validate_schedule_conflicts_api, name='validate_schedule_conflicts_api'),
    path('schedules/student/<int:student_id>/', schedule_views.student_schedule_api, name='student_schedule_api'),
    path('schedules/teacher/<int:teacher_id>/', schedule_views.teacher_schedule_api, name='teacher_schedule_api'),
    path('schedules/course-statistics/', schedule_views.course_statistics_api, name='course_statistics_api'),
    path('schedules/system-overview/', schedule_views.system_overview_api, name='system_overview_api'),
    path('schedules/<int:schedule_id>/', schedule_views.schedule_detail_api, name='schedule_detail_api'),
    
    # Vista de gestión de horarios (DEBE IR DESPUÉS DE LAS APIs)
    path('schedules/', views.ScheduleManagementView.as_view(), name='schedule_management'),
    
    # APIs básicas
    path('api/academic-years/', views.academic_year_list_api, name='academic_year_list_api'),
    path('api/grades/', views.grade_list_api, name='grade_list_api'),
    path('api/subjects/', views.subject_list_api, name='subject_list_api'),
    
    # APIs CRUD para Grados
    path('api/grades/create/', views.create_grade_api, name='create_grade_api'),
    path('api/grades/<int:grade_id>/', views.grade_detail_api, name='grade_detail_api'),
    path('api/grades/<int:grade_id>/update/', views.update_grade_api, name='update_grade_api'),
    path('api/grades/<int:grade_id>/delete/', views.delete_grade_api, name='delete_grade_api'),
    
    # APIs CRUD para Materias
    path('api/subjects/create/', views.create_subject_api, name='create_subject_api'),
    path('api/subjects/<int:subject_id>/', views.subject_detail_api, name='subject_detail_api'),
    path('api/subjects/<int:subject_id>/update/', views.update_subject_api, name='update_subject_api'),
    path('api/subjects/<int:subject_id>/delete/', views.delete_subject_api, name='delete_subject_api'),
    
    # APIs para Asignaciones de Materias a Grados
    path('api/grades/<int:grade_id>/assignments/', views.grade_subject_assignments_api, name='grade_subject_assignments_api'),
    path('api/grades/<int:grade_id>/available-subjects/', views.available_subjects_for_grade_api, name='available_subjects_for_grade_api'),
    path('api/assignments/create/', views.create_grade_subject_assignment_api, name='create_grade_subject_assignment_api'),
    path('api/assignments/<int:assignment_id>/update/', views.update_grade_subject_assignment_api, name='update_grade_subject_assignment_api'),
    path('api/assignments/<int:assignment_id>/delete/', views.delete_grade_subject_assignment_api, name='delete_grade_subject_assignment_api'),
    
    # APIs para Sistema de Inscripciones
    path('api/students/', views.students_list_api, name='students_list_api'),
    path('api/students/create/', views.create_student_api, name='create_student_api'),
    path('api/students/<int:student_id>/', views.student_detail_api, name='student_detail_api'),
    path('api/courses/availability/', views.courses_with_availability_api, name='courses_with_availability_api'),
    path('api/enrollments/enroll/', views.enroll_student_api, name='enroll_student_api'),
    path('api/enrollments/unenroll/', views.unenroll_student_api, name='unenroll_student_api'),
    path('api/enrollments/statistics/', views.enrollment_statistics_api, name='enrollment_statistics_api'),
    
    # APIs CRUD para Cursos
    path('api/courses/', views.course_list_api, name='course_list_api'),
    path('api/courses/create/', views.create_course_api, name='create_course_api'),
    path('api/courses/<int:course_id>/update/', views.update_course_api, name='update_course_api'),
    path('api/courses/<int:course_id>/delete/', views.delete_course_api, name='delete_course_api'),
]