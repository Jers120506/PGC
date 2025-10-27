from django.urls import path
from . import views

app_name = 'academics_extended'

urlpatterns = [
    # Dashboard principal - TEMPORALMENTE SIMPLIFICADO
    path('', views.AcademicDashboardView.as_view(), name='dashboard'),
    
    # APIs básicas
    path('api/academic-years/', views.academic_year_list_api, name='academic_year_list_api'),
    path('api/grades/', views.grade_list_api, name='grade_list_api'),
    path('api/subjects/', views.subject_list_api, name='subject_list_api'),
]