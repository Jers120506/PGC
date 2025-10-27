"""
URLs específicas para el dashboard docente
Sistema offline para Institución Educativa La Balsa - Córdoba
"""
from django.urls import path
from .views import (
    TeacherDashboardView, QuickAttendanceView, QuickGradeView,
    MyStudentsView, MyCoursesView, save_attendance, save_grades
)

app_name = 'academics'

urlpatterns = [
    # Dashboard principal del docente
    path('teacher/dashboard/', TeacherDashboardView.as_view(), name='teacher_dashboard'),
    
    # Funcionalidades rápidas
    path('teacher/attendance/', QuickAttendanceView.as_view(), name='quick_attendance'),
    path('teacher/attendance/save/', save_attendance, name='save_attendance'),
    path('teacher/grades/', QuickGradeView.as_view(), name='quick_grades'),
    path('teacher/grades/save/', save_grades, name='save_grades'),
    
    # Gestión de estudiantes y cursos
    path('teacher/students/', MyStudentsView.as_view(), name='my_students'),
    path('teacher/courses/', MyCoursesView.as_view(), name='my_courses'),
]