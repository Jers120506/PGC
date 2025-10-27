from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import TemplateView

# Importar modelos básicos (temporalmente limpio)
from .models import AcademicYear, Grade, Subject, Course
from authentication.models import User


class AcademicDashboardView(TemplateView):
    """Vista simplificada del dashboard académico"""
    template_name = 'academics_extended/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Solo datos básicos por ahora
        context.update({
            'total_academic_years': AcademicYear.objects.count(),
            'total_grades': Grade.objects.count(),
            'total_subjects': Subject.objects.count(),
            'total_courses': Course.objects.count(),
        })
        
        return context


def academic_year_list_api(request):
    """API para listar años académicos"""
    academic_years = AcademicYear.objects.all().order_by('-start_date')
    data = []
    
    for year in academic_years:
        data.append({
            'id': year.id,
            'name': year.name,
            'start_date': year.start_date.isoformat(),
            'end_date': year.end_date.isoformat(),
            'is_current': year.is_current,
        })
    
    return JsonResponse({
        'status': 'success',
        'data': data
    })


def grade_list_api(request):
    """API para listar grados"""
    grades = Grade.objects.all().order_by('order')
    data = []
    
    for grade in grades:
        data.append({
            'id': grade.id,
            'name': grade.name,
            'level': grade.level,
            'order': grade.order,
        })
    
    return JsonResponse({
        'status': 'success',
        'data': data
    })


def subject_list_api(request):
    """API para listar materias"""
    subjects = Subject.objects.all().order_by('area', 'name')
    data = []
    
    for subject in subjects:
        data.append({
            'id': subject.id,
            'name': subject.name,
            'code': subject.code,
            'area': subject.area,
            'hours_per_week': subject.hours_per_week,
        })
    
    return JsonResponse({
        'status': 'success',
        'data': data
    })