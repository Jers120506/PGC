"""
Vistas específicas para el dashboard docente
Sistema offline para Institución Educativa La Balsa - Córdoba
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.http import JsonResponse
from django.utils import timezone
from datetime import date, timedelta
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .models import (
    Student, Course, Subject, SubjectAssignment, GradeRecord, 
    Attendance, AcademicPeriod, BehaviorRecord
)
# from communications.models import Announcement, InternalMessage
from django import forms


class TeacherRequiredMixin(UserPassesTestMixin):
    """Mixin para verificar que el usuario es profesor o admin"""
    
    def test_func(self):
        return (hasattr(self.request.user, 'profile') and 
                self.request.user.profile.role in ['teacher', 'admin'])
    
    def handle_no_permission(self):
        messages.error(self.request, 'Solo los profesores pueden acceder a esta página.')
        return redirect('/dashboard/')


class TeacherDashboardView(LoginRequiredMixin, TeacherRequiredMixin, TemplateView):
    """Dashboard principal del docente - Institución Educativa La Balsa"""
    template_name = 'academics/teacher/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = self.request.user
        
        # Período académico actual
        try:
            current_period = AcademicPeriod.objects.get(is_current=True)
        except AcademicPeriod.DoesNotExist:
            current_period = None
        
        # Mis asignaciones de materia este año
        my_assignments = SubjectAssignment.objects.filter(
            teacher=teacher,
            academic_year__is_current=True,
            is_active=True
        ).select_related('subject', 'course', 'course__grade').order_by('course__grade__order', 'subject__name')
        
        # Cursos que tengo asignados
        my_courses = Course.objects.filter(
            subjectassignment__teacher=teacher,
            subjectassignment__is_active=True,
            academic_year__is_current=True
        ).distinct().select_related('grade').prefetch_related('students')
        
        # Estudiantes bajo mi supervisión
        my_students = Student.objects.filter(
            course__in=my_courses,
            is_active=True
        ).select_related('user', 'course').order_by('user__last_name', 'user__first_name')
        
        # Estadísticas del día
        today = timezone.now().date()
        
        # Asistencia de hoy
        today_attendance = Attendance.objects.filter(
            teacher=teacher,
            date=today
        ).count()
        
        # Calificaciones registradas esta semana
        week_start = today - timedelta(days=7)
        week_grades = GradeRecord.objects.filter(
            teacher=teacher,
            date_recorded__gte=week_start
        ).count()
        
        # Observaciones de comportamiento esta semana
        week_behaviors = BehaviorRecord.objects.filter(
            teacher=teacher,
            date__gte=week_start
        ).count()
        
        # Mensajes sin leer
        # unread_messages = InternalMessage.objects.filter(
        #     recipient=teacher,
        #     is_read=False
        # ).count()
        unread_messages = 0
        
        # Próximas clases de hoy (simplificado)
        today_assignments = my_assignments.filter(
            course__is_active=True
        )[:5]
        
        # Estudiantes con calificaciones bajas (< 3.0) en mis materias
        if current_period:
            low_grades = GradeRecord.objects.filter(
                teacher=teacher,
                period=current_period,
                grade_value__lt=3.0,
                student__is_active=True
            ).values('student').distinct().count()
        else:
            low_grades = 0
        
        # Estudiantes con inasistencias frecuentes (más de 3 faltas en 2 semanas)
        two_weeks_ago = today - timedelta(days=14)
        frequent_absences = Attendance.objects.filter(
            teacher=teacher,
            date__gte=two_weeks_ago,
            status__in=['absent', 'justified']
        ).values('student').annotate(
            absence_count=Count('id')
        ).filter(absence_count__gt=3).count()
        
        # Anuncios importantes para profesores
        # important_announcements = Announcement.objects.filter(
        #     target_audience__in=['all', 'teachers'],
        #     is_active=True,
        #     active_from__lte=timezone.now(),
        #     active_until__gte=timezone.now()
        # ).order_by('-priority', '-created_at')[:3]
        important_announcements = []
        
        # Resumen rápido para cards del dashboard
        stats = {
            'total_assignments': my_assignments.count(),
            'total_courses': my_courses.count(),
            'total_students': my_students.count(),
            'today_attendance': today_attendance,
            'week_grades': week_grades,
            'week_behaviors': week_behaviors,
            'unread_messages': unread_messages,
            'low_grades_count': low_grades,
            'frequent_absences': frequent_absences,
        }
        
        context.update({
            'teacher': teacher,
            'current_period': current_period,
            'my_assignments': my_assignments,
            'my_courses': my_courses,
            'my_students': my_students[:10],  # Mostrar solo los primeros 10
            'today_assignments': today_assignments,
            'stats': stats,
            'important_announcements': important_announcements,
            'today': today,
        })
        
        return context


class QuickAttendanceForm(forms.Form):
    """Formulario para toma rápida de asistencia"""
    course = forms.ModelChoiceField(
        queryset=Course.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date = forms.DateField(
        initial=date.today,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    def __init__(self, teacher, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Solo cursos asignados al profesor
        teacher_courses = Course.objects.filter(
            subjectassignment__teacher=teacher,
            subjectassignment__is_active=True,
            academic_year__is_current=True
        ).distinct()
        
        self.fields['course'].queryset = teacher_courses
        
        # Solo materias que enseña el profesor
        teacher_subjects = Subject.objects.filter(
            subjectassignment__teacher=teacher,
            subjectassignment__is_active=True
        ).distinct()
        
        self.fields['subject'].queryset = teacher_subjects


class QuickAttendanceView(LoginRequiredMixin, TeacherRequiredMixin, FormView):
    """Vista para toma rápida de asistencia"""
    template_name = 'academics/teacher/quick_attendance.html'
    form_class = QuickAttendanceForm
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['teacher'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        course = form.cleaned_data['course']
        subject = form.cleaned_data['subject']
        date_selected = form.cleaned_data['date']
        
        # Obtener estudiantes del curso
        students = Student.objects.filter(
            course=course,
            is_active=True
        ).select_related('user').order_by('user__last_name', 'user__first_name')
        
        context = {
            'course': course,
            'subject': subject,
            'date_selected': date_selected,
            'students': students,
            'teacher': self.request.user,
        }
        
        return render(self.request, 'academics/teacher/attendance_form.html', context)


def save_attendance(request):
    """Vista para guardar la asistencia"""
    if request.method == 'POST' and request.user.is_authenticated:
        teacher = request.user
        course_id = request.POST.get('course_id')
        subject_id = request.POST.get('subject_id')
        date_str = request.POST.get('date')
        
        try:
            course = Course.objects.get(id=course_id)
            subject = Subject.objects.get(id=subject_id)
            attendance_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
            
            saved_count = 0
            
            # Procesar cada estudiante
            for key, value in request.POST.items():
                if key.startswith('attendance_') and value:
                    student_id = key.replace('attendance_', '')
                    try:
                        student = Student.objects.get(id=student_id)
                        
                        # Crear o actualizar registro de asistencia
                        attendance, created = Attendance.objects.update_or_create(
                            student=student,
                            course=course,
                            subject=subject,
                            teacher=teacher,
                            date=attendance_date,
                            defaults={'status': value}
                        )
                        saved_count += 1
                        
                    except Student.DoesNotExist:
                        continue
            
            messages.success(request, f'Asistencia guardada exitosamente para {saved_count} estudiantes.')
            return redirect('academics:teacher_dashboard')
            
        except Exception as e:
            messages.error(request, f'Error al guardar la asistencia: {str(e)}')
            return redirect('academics:quick_attendance')
    
    return redirect('academics:quick_attendance')


class QuickGradeForm(forms.Form):
    """Formulario para registro rápido de calificaciones"""
    course = forms.ModelChoiceField(
        queryset=Course.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    activity_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Quiz Capítulo 1'})
    )
    activity_type = forms.ChoiceField(
        choices=GradeRecord.ACTIVITY_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date_recorded = forms.DateField(
        initial=date.today,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    def __init__(self, teacher, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Solo cursos asignados al profesor
        teacher_courses = Course.objects.filter(
            subjectassignment__teacher=teacher,
            subjectassignment__is_active=True,
            academic_year__is_current=True
        ).distinct()
        
        self.fields['course'].queryset = teacher_courses
        
        # Solo materias que enseña el profesor
        teacher_subjects = Subject.objects.filter(
            subjectassignment__teacher=teacher,
            subjectassignment__is_active=True
        ).distinct()
        
        self.fields['subject'].queryset = teacher_subjects


class QuickGradeView(LoginRequiredMixin, TeacherRequiredMixin, FormView):
    """Vista para registro rápido de calificaciones"""
    template_name = 'academics/teacher/quick_grades.html'
    form_class = QuickGradeForm
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['teacher'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        course = form.cleaned_data['course']
        subject = form.cleaned_data['subject']
        activity_name = form.cleaned_data['activity_name']
        activity_type = form.cleaned_data['activity_type']
        date_recorded = form.cleaned_data['date_recorded']
        
        # Obtener período actual
        try:
            current_period = AcademicPeriod.objects.get(is_current=True)
        except AcademicPeriod.DoesNotExist:
            messages.error(self.request, 'No hay un período académico activo.')
            return self.form_invalid(form)
        
        # Obtener estudiantes del curso
        students = Student.objects.filter(
            course=course,
            is_active=True
        ).select_related('user').order_by('user__last_name', 'user__first_name')
        
        context = {
            'course': course,
            'subject': subject,
            'activity_name': activity_name,
            'activity_type': activity_type,
            'date_recorded': date_recorded,
            'current_period': current_period,
            'students': students,
            'teacher': self.request.user,
        }
        
        return render(self.request, 'academics/teacher/grades_form.html', context)


def save_grades(request):
    """Vista para guardar las calificaciones"""
    if request.method == 'POST' and request.user.is_authenticated:
        teacher = request.user
        course_id = request.POST.get('course_id')
        subject_id = request.POST.get('subject_id')
        activity_name = request.POST.get('activity_name')
        activity_type = request.POST.get('activity_type')
        date_str = request.POST.get('date_recorded')
        period_id = request.POST.get('period_id')
        
        try:
            course = Course.objects.get(id=course_id)
            subject = Subject.objects.get(id=subject_id)
            period = AcademicPeriod.objects.get(id=period_id)
            grade_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
            
            saved_count = 0
            
            # Procesar cada estudiante
            for key, value in request.POST.items():
                if key.startswith('grade_') and value:
                    student_id = key.replace('grade_', '')
                    try:
                        student = Student.objects.get(id=student_id)
                        grade_value = float(value)
                        
                        # Validar rango de calificación (1-5)
                        if 1.0 <= grade_value <= 5.0:
                            # Crear registro de calificación
                            grade_record = GradeRecord.objects.create(
                                student=student,
                                subject=subject,
                                course=course,
                                teacher=teacher,
                                period=period,
                                grade_value=grade_value,
                                activity_name=activity_name,
                                activity_type=activity_type,
                                date_recorded=grade_date
                            )
                            saved_count += 1
                        
                    except (Student.DoesNotExist, ValueError):
                        continue
            
            messages.success(request, f'Calificaciones guardadas exitosamente para {saved_count} estudiantes.')
            return redirect('academics:teacher_dashboard')
            
        except Exception as e:
            messages.error(request, f'Error al guardar las calificaciones: {str(e)}')
            return redirect('academics:quick_grades')
    
    return redirect('academics:quick_grades')


class MyStudentsView(LoginRequiredMixin, TeacherRequiredMixin, ListView):
    """Vista de mis estudiantes"""
    template_name = 'academics/teacher/my_students.html'
    context_object_name = 'students'
    paginate_by = 20
    
    def get_queryset(self):
        teacher = self.request.user
        
        # Estudiantes de cursos donde enseño
        queryset = Student.objects.filter(
            course__subjectassignment__teacher=teacher,
            course__subjectassignment__is_active=True,
            course__academic_year__is_current=True,
            is_active=True
        ).distinct().select_related('user', 'course', 'course__grade').order_by('user__last_name', 'user__first_name')
        
        # Filtro por curso
        course_filter = self.request.GET.get('course')
        if course_filter:
            queryset = queryset.filter(course_id=course_filter)
        
        # Búsqueda por nombre
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(student_id__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = self.request.user
        
        # Cursos para filtro
        my_courses = Course.objects.filter(
            subjectassignment__teacher=teacher,
            subjectassignment__is_active=True,
            academic_year__is_current=True
        ).distinct().select_related('grade').order_by('grade__order')
        
        context.update({
            'my_courses': my_courses,
            'teacher': teacher,
        })
        
        return context


class MyCoursesView(LoginRequiredMixin, TeacherRequiredMixin, ListView):
    """Vista de mis cursos asignados"""
    template_name = 'academics/teacher/my_courses.html'
    context_object_name = 'courses'
    
    def get_queryset(self):
        teacher = self.request.user
        
        return Course.objects.filter(
            subjectassignment__teacher=teacher,
            subjectassignment__is_active=True,
            academic_year__is_current=True
        ).distinct().select_related('grade', 'homeroom_teacher').prefetch_related('students').order_by('grade__order', 'section')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = self.request.user
        
        # Mis asignaciones por curso
        assignments_by_course = {}
        for course in context['courses']:
            assignments = SubjectAssignment.objects.filter(
                teacher=teacher,
                course=course,
                is_active=True
            ).select_related('subject')
            assignments_by_course[course.id] = assignments
        
        context.update({
            'assignments_by_course': assignments_by_course,
            'teacher': teacher,
        })
        
        return context
