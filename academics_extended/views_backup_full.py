from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, CreateView, DetailView
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Avg, Count, Sum, Q
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP
import json

# Importar modelos existentes
from .models import (
    AcademicYear, Grade, Subject, Course, SubjectAssignment,
    Student
    # GradeRecord, Attendance, EvaluationCriteria, GradingScale, StudentGradeSummary - TEMPORALMENTE DESHABILITADO
)
from authentication.models import User


class AcademicDashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard principal del sistema académico"""
    template_name = 'academics_extended/dashboard.html'
    
    def get_template_names(self):
        """Usar siempre el template principal que maneja todos los roles"""
        return ['academics_extended/dashboard.html']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['current_academic_year'] = AcademicYear.objects.filter(is_current=True).first()
        
        if user.profile.role == 'admin':
            context.update(self.get_admin_context())
        elif user.profile.role == 'teacher':
            context.update(self.get_teacher_context())
        elif user.profile.role == 'student':
            context.update(self.get_student_context())
        elif user.profile.role == 'secretary':
            context.update(self.get_secretary_context())
            
        return context
    
    def get_admin_context(self):
        """Contexto para administradores"""
        current_year = AcademicYear.objects.filter(is_current=True).first()
        
        return {
            'total_students': Student.objects.filter(status='active').count(),
            'total_teachers': User.objects.filter(profile__role='teacher').count(),
            'total_courses': Course.objects.filter(academic_year=current_year).count() if current_year else 0,
            'total_subjects': Subject.objects.count(),
            'recent_enrollments': Student.objects.filter(
                status='active'
            ).order_by('-enrollment_date')[:5],
            'courses_with_low_enrollment': Course.objects.filter(
                academic_year=current_year
            ).annotate(
                student_count=Count('students')
            ).filter(student_count__lt=20) if current_year else [],
        }
    
    def get_teacher_context(self):
        """Contexto para profesores"""
        current_year = AcademicYear.objects.filter(is_current=True).first()
        teacher = self.request.user
        
        if current_year:
            my_assignments = SubjectAssignment.objects.filter(
                teacher=teacher,
                academic_year=current_year
            ).select_related('subject', 'course', 'course__grade')
            
            my_courses = Course.objects.filter(
                subjectassignment__teacher=teacher,
                academic_year=current_year
            ).distinct()
            
            my_students = Student.objects.filter(
                course__in=my_courses,
                status='active'
            )
            
            total_students = my_students.count()
            pending_attendance = my_courses.count()
            recent_grades = GradeRecord.objects.filter(
                teacher=teacher
            ).order_by('-date_recorded')[:5]
        else:
            my_assignments = []
            my_courses = []
            total_students = 0
            pending_attendance = 0
            recent_grades = []
        
        return {
            'my_assignments': my_assignments,
            'my_courses': my_courses,
            'total_my_students': total_students,
            'recent_grades': recent_grades,
            'pending_attendance': pending_attendance,
        }
    
    def get_student_context(self):
        """Contexto para estudiantes"""
        try:
            student = Student.objects.get(user=self.request.user)
            current_year = AcademicYear.objects.filter(is_current=True).first()
            
            # Obtener las asignaciones (materias con profesores)
            my_assignments = SubjectAssignment.objects.filter(
                course=student.course,
                academic_year__is_current=True
            ).select_related('subject', 'teacher') if student.course else []
            
            # Obtener solo las materias (para compatibilidad)
            my_subjects = Subject.objects.filter(
                subjectassignment__course=student.course,
                subjectassignment__academic_year__is_current=True
            ) if student.course else []
            
            # Calificaciones recientes y estadísticas
            all_grades = GradeRecord.objects.filter(student=student)
            recent_grades = all_grades.order_by('-date_recorded')[:5]
            
            # Calcular promedio general
            total_percentage = sum(grade.percentage for grade in all_grades)
            grade_count = all_grades.count()
            general_average = round(total_percentage / grade_count, 1) if grade_count > 0 else 0
            
            # Estadísticas de asistencia
            all_attendance = Attendance.objects.filter(student=student)
            my_attendance = all_attendance.order_by('-date')[:10]
            
            attendance_stats = {
                'total': all_attendance.count(),
                'present': all_attendance.filter(status='present').count(),
                'late': all_attendance.filter(status='late').count(),
                'absent': all_attendance.filter(status='absent').count(),
            }
            
            if attendance_stats['total'] > 0:
                attendance_percentage = round((attendance_stats['present'] / attendance_stats['total']) * 100, 1)
            else:
                attendance_percentage = 100
            
            # Materias con mejor y peor rendimiento
            subject_averages = {}
            for grade in all_grades:
                subject_name = grade.subject.name
                if subject_name not in subject_averages:
                    subject_averages[subject_name] = []
                subject_averages[subject_name].append(grade.percentage)
            
            for subject in subject_averages:
                subject_averages[subject] = round(sum(subject_averages[subject]) / len(subject_averages[subject]), 1)
            
            best_subject = max(subject_averages.items(), key=lambda x: x[1]) if subject_averages else None
            worst_subject = min(subject_averages.items(), key=lambda x: x[1]) if subject_averages else None
            
            return {
                'student_profile': student,
                'my_course': student.course,
                'my_subjects': my_subjects,
                'my_assignments': my_assignments,
                'recent_grades': recent_grades,
                'my_attendance': my_attendance,
                'current_academic_year': current_year,
                'general_average': general_average,
                'grade_count': grade_count,
                'attendance_stats': attendance_stats,
                'attendance_percentage': attendance_percentage,
                'best_subject': best_subject,
                'worst_subject': worst_subject,
                'subject_averages': subject_averages,
            }
        except Student.DoesNotExist:
            return {'error': 'Perfil de estudiante no encontrado'}
    
    def get_secretary_context(self):
        """Contexto mejorado para secretaría"""
        current_year = AcademicYear.objects.filter(is_current=True).first()
        
        # Estadísticas básicas
        total_students = Student.objects.filter(status='active').count()
        pending_enrollments = Student.objects.filter(status='inactive').count()
        total_courses = Course.objects.filter(academic_year=current_year).count() if current_year else 0
        total_subjects = Subject.objects.count()
        
        # Estudiantes recientes
        recent_students = Student.objects.filter(
            status='active'
        ).select_related('user', 'course').order_by('-enrollment_date')[:8]
        
        # Estadísticas por grado
        students_by_grade = Student.objects.filter(
            status='active'
        ).values(
            'course__grade__name'
        ).annotate(
            count=Count('id')
        ).order_by('course__grade__order') if current_year else []
        
        # Materias por área
        subjects_by_area = Subject.objects.values(
            'area'
        ).annotate(
            count=Count('id')
        ).order_by('area')
        
        # Cursos con más estudiantes
        top_courses = Course.objects.filter(
            academic_year=current_year
        ).annotate(
            student_count=Count('students')
        ).order_by('-student_count')[:5] if current_year else []
        
        return {
            'total_students': total_students,
            'pending_enrollments': pending_enrollments,
            'total_courses': total_courses,
            'total_subjects': total_subjects,
            'recent_students': recent_students,
            'students_by_grade': students_by_grade,
            'subjects_by_area': subjects_by_area,
            'top_courses': top_courses,
            'current_academic_year': current_year,
            'user_role': 'secretary',
        }


class CourseListView(LoginRequiredMixin, ListView):
    """Lista de cursos - Accesible para secretario y admin"""
    model = Course
    template_name = 'academics_extended/course_list.html'
    context_object_name = 'courses'
    paginate_by = 20
    
    def get_queryset(self):
        # Permitir acceso a secretario y admin
        if self.request.user.profile.role in ['secretary', 'admin'] or self.request.user.is_superuser:
            current_year = AcademicYear.objects.filter(is_current=True).first()
            if current_year:
                return Course.objects.filter(
                    academic_year=current_year
                ).select_related('grade', 'homeroom_teacher').annotate(
                    student_count=Count('students')
                ).order_by('grade__order', 'section')
        return Course.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Información adicional para secretario
        if self.request.user.profile.role == 'secretary':
            current_year = AcademicYear.objects.filter(is_current=True).first()
            context.update({
                'current_academic_year': current_year,
                'total_courses': self.get_queryset().count(),
                'can_manage_courses': True,
            })
        
        return context


class StudentListView(LoginRequiredMixin, ListView):
    """Lista de estudiantes - Accesible para secretario y admin"""
    model = Student
    template_name = 'academics_extended/student_list.html'
    context_object_name = 'students'
    paginate_by = 50
    
    def get_queryset(self):
        # Permitir acceso a secretario y admin
        if self.request.user.profile.role in ['secretary', 'admin'] or self.request.user.is_superuser:
            return Student.objects.filter(
                status='active'
            ).select_related('user', 'course', 'course__grade').order_by(
                'course__grade__order', 'course__section', 'user__last_name'
            )
        else:
            return Student.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estadísticas adicionales para secretario
        if self.request.user.profile.role == 'secretary':
            context.update({
                'total_students': Student.objects.filter(status='active').count(),
                'pending_enrollments': Student.objects.filter(status='inactive').count(),
                'students_by_grade': Student.objects.filter(status='active').values(
                    'course__grade__name'
                ).annotate(count=Count('id')).order_by('course__grade__order'),
                'can_manage_students': True,
            })
        
        return context


class SubjectListView(LoginRequiredMixin, ListView):
    """Lista de materias - Accesible para secretario y admin"""
    model = Subject
    template_name = 'academics_extended/subject_list.html'
    context_object_name = 'subjects'
    
    def get_queryset(self):
        # Permitir acceso a secretario y admin
        if self.request.user.profile.role in ['secretary', 'admin'] or self.request.user.is_superuser:
            return Subject.objects.all().order_by('area', 'name')
        return Subject.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Información adicional para secretario
        if self.request.user.profile.role == 'secretary':
            subjects_by_area = Subject.objects.values('area').annotate(
                count=Count('id')
            ).order_by('area')
            
            context.update({
                'subjects_by_area': subjects_by_area,
                'total_subjects': self.get_queryset().count(),
                'can_manage_subjects': True,
            })
        
        return context


@login_required
def quick_grade_entry(request, course_id, subject_id):
    """Vista rápida para entrada de calificaciones"""
    course = get_object_or_404(Course, id=course_id)
    subject = get_object_or_404(Subject, id=subject_id)
    
    # Verificar que el profesor tenga asignada esta materia
    if not request.user.profile.is_admin:
        assignment = SubjectAssignment.objects.filter(
            teacher=request.user,
            subject=subject,
            course=course
        ).first()
        
        if not assignment:
            messages.error(request, 'No tienes permisos para calificar esta materia en este curso.')
            return redirect('academics_extended:dashboard')
    
    students = Student.objects.filter(course=course, status='active').order_by('user__last_name')
    
    if request.method == 'POST':
        activity_name = request.POST.get('activity_name')
        activity_type = request.POST.get('activity_type')
        period = request.POST.get('period')
        max_value = request.POST.get('max_value', '5.0')
        
        if not all([activity_name, activity_type, period]):
            messages.error(request, 'Todos los campos son obligatorios.')
        else:
            grades_saved = 0
            for student in students:
                grade_value = request.POST.get(f'grade_{student.id}')
                if grade_value:
                    try:
                        grade_record = GradeRecord.objects.create(
                            student=student,
                            subject=subject,
                            teacher=request.user,
                            activity_name=activity_name,
                            grade_value=float(grade_value),
                            max_value=float(max_value),
                            period=period,
                            activity_type=activity_type,
                            date_recorded=timezone.now().date()
                        )
                        grades_saved += 1
                    except ValueError:
                        continue
            
            messages.success(request, f'Se guardaron {grades_saved} calificaciones exitosamente.')
            return redirect('academics_extended:dashboard')
    
    context = {
        'course': course,
        'subject': subject,
        'students': students,
        'activity_types': GradeRecord.ACTIVITY_TYPE_CHOICES,
        'periods': GradeRecord.PERIOD_CHOICES,
    }
    
    return render(request, 'academics_extended/quick_grade_entry.html', context)


# =====================================
# VISTAS ESPECÍFICAS PARA ESTUDIANTES
# =====================================

class StudentSubjectsView(LoginRequiredMixin, TemplateView):
    """Vista para que los estudiantes vean sus materias"""
    template_name = 'academics_extended/student_subjects.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Verificar que el usuario sea estudiante
        if user.profile.role != 'student':
            messages.error(self.request, 'No tienes permisos para acceder a esta página.')
            return context
            
        try:
            student = Student.objects.get(user=user)
            # Obtener asignaciones de materias del curso con profesores
            my_assignments = SubjectAssignment.objects.filter(
                course=student.course,
                academic_year__is_current=True
            ).select_related('subject', 'teacher') if student.course else []
            
            # Obtener solo las materias (para compatibilidad)
            my_subjects = [assignment.subject for assignment in my_assignments]
            
            context.update({
                'student_profile': student,
                'my_course': student.course,
                'my_subjects': my_subjects,
                'my_assignments': my_assignments,
                'current_academic_year': AcademicYear.objects.filter(is_current=True).first(),
            })
        except Student.DoesNotExist:
            context.update({
                'student_profile': None,
                'my_course': None,
                'my_subjects': [],
                'my_assignments': [],
            })
            
        return context


class StudentGradesView(LoginRequiredMixin, TemplateView):
    """Vista para que los estudiantes vean sus calificaciones"""
    template_name = 'academics_extended/student_grades.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Verificar que el usuario sea estudiante
        if user.profile.role != 'student':
            messages.error(self.request, 'No tienes permisos para acceder a esta página.')
            return context
            
        try:
            student = Student.objects.get(user=user)
            grades = GradeRecord.objects.filter(student=student).order_by('-date_recorded')
            
            context.update({
                'student_profile': student,
                'my_grades': grades,
                'recent_grades': grades[:10],  # Últimas 10 calificaciones
                'grade_summary': self.get_grade_summary(grades),
            })
        except Student.DoesNotExist:
            context.update({
                'student_profile': None,
                'my_grades': [],
                'recent_grades': [],
                'grade_summary': {},
            })
            
        return context
    
    def get_grade_summary(self, grades):
        """Calcular resumen de calificaciones por materia"""
        summary = {}
        for grade in grades:
            subject = grade.subject.name
            if subject not in summary:
                summary[subject] = {
                    'total_grades': 0,
                    'total_points': 0,
                    'average': 0,
                    'last_grade': None
                }
            
            summary[subject]['total_grades'] += 1
            summary[subject]['total_points'] += grade.percentage
            summary[subject]['average'] = summary[subject]['total_points'] / summary[subject]['total_grades']
            if not summary[subject]['last_grade'] or grade.date_recorded > summary[subject]['last_grade'].date_recorded:
                summary[subject]['last_grade'] = grade
                
        return summary


class StudentScheduleView(LoginRequiredMixin, TemplateView):
    """Vista para que los estudiantes vean su horario"""
    template_name = 'academics_extended/student_schedule.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Verificar que el usuario sea estudiante
        if user.profile.role != 'student':
            messages.error(self.request, 'No tienes permisos para acceder a esta página.')
            return context
            
        try:
            student = Student.objects.get(user=user)
            # Obtener asignaciones de materias del curso con profesores
            my_assignments = SubjectAssignment.objects.filter(
                course=student.course,
                academic_year__is_current=True
            ).select_related('subject', 'teacher') if student.course else []
            
            # Obtener solo las materias (para compatibilidad)
            my_subjects = [assignment.subject for assignment in my_assignments]
            
            context.update({
                'student_profile': student,
                'my_course': student.course,
                'my_subjects': my_subjects,
                'my_assignments': my_assignments,
                'current_academic_year': AcademicYear.objects.filter(is_current=True).first(),
                'schedule_info': 'Horario académico próximamente disponible',  # Placeholder para futuro desarrollo
            })
        except Student.DoesNotExist:
            context.update({
                'student_profile': None,
                'my_course': None,
                'my_subjects': [],
                'my_assignments': [],
                'subject_assignments': [],
                'schedule_info': None,
            })
            
        return context


# =====================================
# VISTAS ESPECÍFICAS PARA PROFESORES
# =====================================

class TeacherCoursesView(LoginRequiredMixin, ListView):
    """Lista de cursos específicos del profesor"""
    model = Course
    template_name = 'academics_extended/teacher_courses.html'
    context_object_name = 'courses'
    
    def get_queryset(self):
        if not self.request.user.profile.is_teacher:
            return Course.objects.none()
        
        current_year = AcademicYear.objects.filter(is_current=True).first()
        if current_year:
            return Course.objects.filter(
                subjectassignment__teacher=self.request.user,
                academic_year=current_year
            ).distinct().select_related('grade', 'homeroom_teacher').annotate(
                student_count=Count('students')
            ).order_by('grade__order', 'section')
        return Course.objects.none()


class TeacherStudentsView(LoginRequiredMixin, ListView):
    """Lista de estudiantes específicos del profesor"""
    model = Student
    template_name = 'academics_extended/teacher_students.html'
    context_object_name = 'students'
    
    def get_queryset(self):
        if not self.request.user.profile.is_teacher:
            return Student.objects.none()
        
        current_year = AcademicYear.objects.filter(is_current=True).first()
        if current_year:
            # Obtener estudiantes de cursos donde el profesor tiene asignaciones
            teacher_courses = Course.objects.filter(
                subjectassignment__teacher=self.request.user,
                academic_year=current_year
            ).distinct()
            
            return Student.objects.filter(
                course__in=teacher_courses,
                status='active'
            ).select_related('user', 'course', 'course__grade').order_by(
                'course__grade__order', 'course__section', 'user__last_name'
            )
        return Student.objects.none()


class TeacherSubjectsView(LoginRequiredMixin, ListView):
    """Lista de materias específicas del profesor"""
    model = SubjectAssignment
    template_name = 'academics_extended/teacher_subjects.html'
    context_object_name = 'assignments'
    
    def get_queryset(self):
        if not self.request.user.profile.is_teacher:
            return SubjectAssignment.objects.none()
        
        current_year = AcademicYear.objects.filter(is_current=True).first()
        if current_year:
            return SubjectAssignment.objects.filter(
                teacher=self.request.user,
                academic_year=current_year
            ).select_related('subject', 'course', 'course__grade').order_by(
                'course__grade__order', 'course__section', 'subject__area', 'subject__name'
            )
        return SubjectAssignment.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        assignments = self.get_queryset()
        
        # Calcular conteos únicos
        unique_subjects = assignments.values_list('subject', flat=True).distinct()
        unique_courses = assignments.values_list('course', flat=True).distinct()
        
        context.update({
            'unique_subjects_count': unique_subjects.count(),
            'unique_courses_count': unique_courses.count(),
        })
        
        return context


class TeacherScheduleView(LoginRequiredMixin, TemplateView):
    """Horario del profesor"""
    template_name = 'academics_extended/teacher_schedule.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if not self.request.user.profile.is_teacher:
            return context
        
        current_year = AcademicYear.objects.filter(is_current=True).first()
        if not current_year:
            return context
        
        # Obtener horarios del profesor
        from .models import Schedule
        teacher_schedules = Schedule.objects.filter(
            subject_assignment__teacher=self.request.user,
            academic_year=current_year,
            is_active=True
        ).select_related(
            'subject_assignment__subject',
            'subject_assignment__course__grade',
            'classroom',
            'time_slot'
        ).order_by('weekday', 'time_slot__order')
        
        # Organizar horarios por día y hora
        schedule_matrix = {}
        weekdays = {1: 'Lunes', 2: 'Martes', 3: 'Miércoles', 4: 'Jueves', 5: 'Viernes'}
        
        # Obtener todas las franjas horarias activas
        from .models import TimeSlot
        time_slots = TimeSlot.objects.filter(is_active=True).order_by('order')
        
        # Inicializar matriz
        for day_num, day_name in weekdays.items():
            schedule_matrix[day_num] = {
                'name': day_name,
                'slots': {}
            }
            for slot in time_slots:
                schedule_matrix[day_num]['slots'][slot.id] = None
        
        # Llenar matriz con horarios
        for schedule in teacher_schedules:
            day = schedule.weekday
            slot_id = schedule.time_slot.id
            if day in schedule_matrix and slot_id in schedule_matrix[day]['slots']:
                schedule_matrix[day]['slots'][slot_id] = schedule
        
        # Convertir la matriz a JSON para JavaScript
        import json
        schedule_matrix_json = {}
        for day_num, day_data in schedule_matrix.items():
            schedule_matrix_json[day_num] = {
                'name': day_data['name'],
                'slots': {}
            }
            for slot_id, schedule in day_data['slots'].items():
                if schedule:
                    schedule_matrix_json[day_num]['slots'][slot_id] = {
                        'subject': schedule.subject_assignment.subject.name,
                        'course': f"{schedule.subject_assignment.course.grade.name} {schedule.subject_assignment.course.section}",
                        'classroom': schedule.classroom.name
                    }
                else:
                    schedule_matrix_json[day_num]['slots'][slot_id] = None
        
        context.update({
            'schedule_matrix': schedule_matrix,
            'schedule_matrix_json': json.dumps(schedule_matrix_json),
            'time_slots': time_slots,
            'weekdays': weekdays,
            'teacher_schedules': teacher_schedules,
        })
        
        return context


class TeacherAttendanceView(LoginRequiredMixin, TemplateView):
    """Vista para que el profesor tome asistencia"""
    template_name = 'academics_extended/teacher_attendance.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if not self.request.user.profile.is_teacher:
            return context
        
        current_year = AcademicYear.objects.filter(is_current=True).first()
        if not current_year:
            return context
        
        # Obtener cursos asignados al profesor
        teacher_assignments = SubjectAssignment.objects.filter(
            teacher=self.request.user,
            academic_year=current_year
        ).select_related('course__grade', 'subject').distinct()
        
        # Obtener estudiantes por curso
        courses_with_students = {}
        for assignment in teacher_assignments:
            course = assignment.course
            if course not in courses_with_students:
                students = Student.objects.filter(
                    course=course,
                    status='active'
                ).order_by('user__last_name', 'user__first_name')
                courses_with_students[course] = students
        
        # Obtener asistencias recientes
        recent_attendance = Attendance.objects.filter(
            student__course__in=[course for course in courses_with_students.keys()]
        ).select_related('student__user', 'student__course').order_by('-date')[:20]
        
        context.update({
            'teacher_assignments': teacher_assignments,
            'courses_with_students': courses_with_students,
            'recent_attendance': recent_attendance,
        })
        
        return context


class TeacherGradesView(LoginRequiredMixin, TemplateView):
    """Vista simplificada para calificación individual de estudiantes"""
    template_name = 'academics_extended/teacher_grades.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if not self.request.user.profile.is_teacher:
            return context
        
        current_year = AcademicYear.objects.filter(is_current=True).first()
        if not current_year:
            return context
        
        # Obtener asignaciones del profesor organizadas por curso
        teacher_assignments = SubjectAssignment.objects.filter(
            teacher=self.request.user,
            academic_year=current_year
        ).select_related('course__grade', 'subject').order_by('course__grade__order', 'course__section', 'subject__name')
        
        # Organizar datos por curso para calificación práctica
        courses_data = {}
        
        for assignment in teacher_assignments:
            course_name = f"{assignment.course.grade.name} {assignment.course.section}"
            
            if course_name not in courses_data:
                courses_data[course_name] = {
                    'course': assignment.course,
                    'subjects': [],
                    'students': [],
                    'students_data': {}
                }
            
            # Agregar materia
            courses_data[course_name]['subjects'].append(assignment)
        
        # Obtener estudiantes y sus datos de calificaciones
        for course_name, course_data in courses_data.items():
            course = course_data['course']
            
            # Estudiantes del curso ordenados alfabéticamente
            students = Student.objects.filter(
                course=course,
                status='active'
            ).select_related('user').order_by('user__last_name', 'user__first_name')
            
            course_data['students'] = students
            
            # Datos simplificados de calificaciones por estudiante
            for student in students:
                student_data = {
                    'subject_grades': {}
                }
                
                # Calificaciones por materia para cada estudiante
                for assignment in course_data['subjects']:
                    grades = GradeRecord.objects.filter(
                        student=student,
                        subject=assignment.subject,
                        teacher=self.request.user
                    ).order_by('-date_recorded')
                    
                    # Calcular promedio simple
                    if grades.exists():
                        grade_values = [float(g.grade_value) for g in grades]
                        average = round(sum(grade_values) / len(grade_values), 1)
                    else:
                        average = 0.0
                    
                    student_data['subject_grades'][assignment.subject.id] = {
                        'grades': list(grades[:5]),  # Últimas 5 calificaciones para historial
                        'average': average,
                        'count': grades.count()
                    }
                
                course_data['students_data'][student.id] = student_data
        
        # Calificaciones recientes para el panel lateral
        recent_grades = GradeRecord.objects.filter(
            teacher=self.request.user
        ).select_related(
            'student__user',
            'subject',
            'student__course__grade'
        ).order_by('-date_recorded')[:8]
        
        # Estadísticas básicas
        total_students = sum(len(course['students']) for course in courses_data.values())
        total_grades_count = GradeRecord.objects.filter(teacher=self.request.user).count()
        
        # Estadísticas por materia
        subject_stats = {}
        for assignment in teacher_assignments:
            grades = GradeRecord.objects.filter(
                subject=assignment.subject,
                teacher=self.request.user
            )
            if grades.exists():
                grade_values = [float(g.grade_value) for g in grades]
                subject_stats[assignment.subject.name] = {
                    'course': f"{assignment.course.grade.name} {assignment.course.section}",
                    'average': round(sum(grade_values) / len(grade_values), 1),
                    'total_grades': grades.count()
                }
        
        context.update({
            'courses_data': courses_data,
            'recent_grades': recent_grades,
            'subject_stats': subject_stats,
            'total_students': total_students,
            'total_grades_count': total_grades_count,
        })
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Manejar guardado de calificación individual via AJAX"""
        if request.headers.get('Content-Type') == 'application/json':
            import json
            try:
                data = json.loads(request.body)
                
                # Validar profesor
                if not request.user.profile.is_teacher:
                    return JsonResponse({
                        'success': False,
                        'message': 'No tienes permisos para calificar.'
                    })
                
                # Obtener datos necesarios
                student = Student.objects.get(id=data['student_id'])
                subject = Subject.objects.get(id=data['subject_id'])
                activity_name = data.get('activity_name', '').strip()
                activity_type = data.get('activity_type', 'quiz')
                grade_value = float(data['grade_value'])
                
                # Validaciones
                if not activity_name:
                    return JsonResponse({
                        'success': False,
                        'message': 'El nombre de la actividad es obligatorio.'
                    })
                
                if not (1.0 <= grade_value <= 5.0):
                    return JsonResponse({
                        'success': False,
                        'message': 'La calificación debe estar entre 1.0 y 5.0.'
                    })
                
                # Verificar que el profesor tiene asignada esta materia
                assignment_exists = SubjectAssignment.objects.filter(
                    teacher=request.user,
                    subject=subject,
                    course=student.course
                ).exists()
                
                if not assignment_exists:
                    return JsonResponse({
                        'success': False,
                        'message': 'No tienes permiso para calificar esta materia en este curso.'
                    })
                
                # Crear la calificación
                grade_record = GradeRecord.objects.create(
                    student=student,
                    subject=subject,
                    teacher=request.user,
                    activity_name=activity_name,
                    activity_type=activity_type,
                    grade_value=grade_value,
                    date_recorded=timezone.now()
                )
                
                # Calcular nuevo promedio del estudiante en esta materia
                all_grades = GradeRecord.objects.filter(
                    student=student,
                    subject=subject,
                    teacher=request.user
                )
                new_average = round(sum(float(g.grade_value) for g in all_grades) / all_grades.count(), 1)
                
                return JsonResponse({
                    'success': True,
                    'message': f'Calificación guardada: {activity_name} - {grade_value}',
                    'grade_id': grade_record.id,
                    'new_average': new_average,
                    'grade_count': all_grades.count()
                })
                
            except (Student.DoesNotExist, Subject.DoesNotExist):
                return JsonResponse({
                    'success': False,
                    'message': 'Estudiante o materia no encontrada.'
                })
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'Valor de calificación inválido.'
                })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': f'Error al guardar: {str(e)}'
                })
        
        return JsonResponse({
            'success': False,
            'message': 'Método no permitido.'
        })


class CommunicationsView(TemplateView):
    """Vista para el sistema de comunicaciones del secretario"""
    template_name = 'academics_extended/communications.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Solo secretarios pueden acceder
        if not hasattr(self.request.user, 'userprofile') or self.request.user.userprofile.role != 'secretary':
            return context
        
        # Estadísticas simuladas (en un proyecto real vendrían de un modelo)
        context.update({
            'sent_messages': 15,
            'pending_messages': 3,
            'draft_messages': 2,
            'total_recipients': 450,
        })
        
        return context


# ==================== NUEVAS VISTAS AVANZADAS ====================

class AdvancedGradingDashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard avanzado de calificaciones para profesores"""
    template_name = 'academics_extended/advanced_grading_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Solo profesores pueden acceder
        if not hasattr(user, 'profile') or user.profile.role != 'teacher':
            context['error'] = 'Acceso denegado. Solo profesores pueden acceder.'
            return context
        
        current_year = AcademicYear.objects.filter(is_current=True).first()
        if not current_year:
            context['error'] = 'No hay año académico activo'
            return context
        
        # Obtener asignaciones del profesor
        teacher_assignments = SubjectAssignment.objects.filter(
            teacher=user,
            academic_year=current_year
        ).select_related('subject', 'course')
        
        # Estadísticas generales
        total_students = User.objects.filter(
            profile__role='student',
            student__status='active'
        ).count()
        
        graded_students = StudentGradeSummary.objects.filter(
            academic_year=current_year
        ).values('student').distinct().count()
        
        # Escalas de calificación disponibles
        grading_scales = GradingScale.objects.all().order_by('min_value')
        
        # Criterios de evaluación por materia
        evaluation_criteria = {}
        for assignment in teacher_assignments:
            criteria = EvaluationCriteria.objects.filter(
                subject=assignment.subject,
                academic_year=current_year
            ).order_by('period')
            evaluation_criteria[assignment.subject.id] = criteria
        
        # Resúmenes recientes
        recent_summaries = StudentGradeSummary.objects.filter(
            academic_year=current_year,
            last_updated__gte=timezone.now() - timezone.timedelta(days=7)
        ).select_related('student__user', 'subject').order_by('-last_updated')[:10]
        
        context.update({
            'current_year': current_year,
            'teacher_assignments': teacher_assignments,
            'total_students': total_students,
            'graded_students': graded_students,
            'grading_scales': grading_scales,
            'evaluation_criteria': evaluation_criteria,
            'recent_summaries': recent_summaries,
        })
        
        return context

class SubjectGradingDetailView(LoginRequiredMixin, DetailView):
    """Vista detallada de calificaciones por materia"""
    template_name = 'academics_extended/subject_grading_detail.html'
    context_object_name = 'subject'
    model = Subject
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subject = self.object
        user = self.request.user
        
        # Verificar permisos
        if not hasattr(user, 'profile') or user.profile.role != 'teacher':
            context['error'] = 'Acceso denegado'
            return context
        
        current_year = AcademicYear.objects.filter(is_current=True).first()
        period = self.request.GET.get('period', 'period_1')
        
        # Verificar que el profesor tenga asignada esta materia
        assignment = SubjectAssignment.objects.filter(
            teacher=user,
            subject=subject,
            academic_year=current_year
        ).first()
        
        if not assignment:
            context['error'] = 'No tienes asignada esta materia'
            return context
        
        # Obtener criterios de evaluación para esta materia y período
        evaluation_criteria = EvaluationCriteria.objects.filter(
            subject=subject,
            period=period,
            academic_year=current_year
        ).order_by('activity_type')
        
        # Obtener estudiantes del curso
        students = Student.objects.filter(
            course=assignment.course,
            status='active'
        ).select_related('user').order_by('user__last_name')
        
        # Calificaciones existentes
        grade_records = GradeRecord.objects.filter(
            subject=subject,
            student__in=students
        ).select_related('student__user')
        
        # Organizar calificaciones por estudiante y tipo de actividad
        student_grades = {}
        for student in students:
            student_grades[student.id] = {
                'student': student,
                'grades': {},
                'summary': None
            }
            
            # Obtener resumen de calificaciones del estudiante
            summary = StudentGradeSummary.objects.filter(
                student=student,
                subject=subject,
                period=period,
                academic_year=current_year
            ).first()
            
            student_grades[student.id]['summary'] = summary
        
        # Organizar calificaciones por tipo de actividad
        for grade in grade_records:
            student_id = grade.student.id
            activity_type = grade.activity_type
            
            if activity_type not in student_grades[student_id]['grades']:
                student_grades[student_id]['grades'][activity_type] = []
            
            student_grades[student_id]['grades'][activity_type].append(grade)
        
        # Escala de calificaciones
        grading_scales = GradingScale.objects.all().order_by('min_value')
        
        context.update({
            'assignment': assignment,
            'current_year': current_year,
            'period': period,
            'evaluation_criteria': evaluation_criteria,
            'student_grades': student_grades,
            'grading_scales': grading_scales,
            'available_periods': [
                ('period_1', 'Período 1'),
                ('period_2', 'Período 2'),
                ('period_3', 'Período 3'),
                ('period_4', 'Período 4'),
            ]
        })
        
        return context

@login_required
def quick_grade_entry(request, subject_id):
    """Entrada rápida de calificaciones"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            subject = get_object_or_404(Subject, id=subject_id)
            current_year = AcademicYear.objects.filter(is_current=True).first()
            
            # Verificar permisos del profesor
            assignment = SubjectAssignment.objects.filter(
                teacher=request.user,
                subject=subject,
                academic_year=current_year
            ).first()
            
            if not assignment:
                return JsonResponse({'error': 'No autorizado'}, status=403)
            
            student_id = data.get('student_id')
            activity_type = data.get('activity_type')
            activity_name = data.get('activity_name')
            score = Decimal(str(data.get('score', 0)))
            period = data.get('period', 'period_1')
            
            student = get_object_or_404(Student, id=student_id)
            
            # Crear o actualizar calificación usando el modelo existente
            grade_record, created = GradeRecord.objects.update_or_create(
                student=student,
                subject=subject,
                activity_type=activity_type,
                academic_year=current_year,
                defaults={
                    'score': score,
                    'teacher': request.user,
                    'date_recorded': timezone.now().date(),
                    'notes': activity_name
                }
            )
            
            # Recalcular resumen del estudiante
            _recalculate_student_summary(student, subject, period, current_year)
            
            # Obtener letra de calificación
            letter_grade = _get_letter_grade(score)
            
            return JsonResponse({
                'success': True,
                'message': f'Calificación {"creada" if created else "actualizada"} exitosamente',
                'grade_id': grade_record.id,
                'letter_grade': letter_grade
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required
def student_grade_analytics(request, student_id, subject_id):
    """Análisis detallado de calificaciones de un estudiante"""
    student = get_object_or_404(Student, id=student_id)
    subject = get_object_or_404(Subject, id=subject_id)
    current_year = AcademicYear.objects.filter(is_current=True).first()
    
    # Verificar permisos
    if request.user.profile.role == 'student' and request.user != student.user:
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    # Obtener todas las calificaciones del estudiante en esta materia
    grade_records = GradeRecord.objects.filter(
        student=student,
        subject=subject,
        academic_year=current_year
    ).order_by('date_recorded')
    
    # Organizar por período (simplificado para modelo existente)
    periods_data = {}
    for period in ['period_1', 'period_2', 'period_3', 'period_4']:
        period_grades = grade_records  # Usar todas las calificaciones por ahora
        
        # Obtener criterios de evaluación para este período
        criteria = EvaluationCriteria.objects.filter(
            subject=subject,
            period=period,
            academic_year=current_year
        )
        
        # Calcular estadísticas básicas
        if period_grades.exists():
            avg_score = period_grades.aggregate(Avg('score'))['score__avg']
            periods_data[period] = {
                'average': float(avg_score) if avg_score else 0,
                'count': period_grades.count(),
                'grades': [
                    {
                        'name': g.activity_type or 'Evaluación',
                        'score': float(g.score),
                        'date': g.date_recorded.isoformat()
                    }
                    for g in period_grades[:10]  # Limitar a 10 calificaciones
                ]
            }
        else:
            periods_data[period] = {
                'average': 0,
                'count': 0,
                'grades': []
            }
    
    # Calcular progreso general
    all_summaries = StudentGradeSummary.objects.filter(
        student=student,
        subject=subject,
        academic_year=current_year
    )
    
    overall_average = all_summaries.aggregate(
        avg=Avg('final_average')
    )['avg'] or 0
    
    response_data = {
        'student': {
            'id': student.id,
            'name': f"{student.user.first_name} {student.user.last_name}",
            'username': student.user.username
        },
        'subject': {
            'id': subject.id,
            'name': subject.name
        },
        'periods': periods_data,
        'overall': {
            'average': float(overall_average),
            'letter_grade': _get_letter_grade(Decimal(str(overall_average))),
            'total_periods': all_summaries.count()
        }
    }
    
    return JsonResponse(response_data)

def _recalculate_student_summary(student, subject, period, academic_year):
    """Recalcular resumen de calificaciones del estudiante (versión simplificada)"""
    # Obtener calificaciones del estudiante para esta materia
    grade_records = GradeRecord.objects.filter(
        student=student,
        subject=subject,
        academic_year=academic_year
    )
    
    if not grade_records.exists():
        return
    
    # Calcular promedio simple
    avg_score = grade_records.aggregate(Avg('score'))['score__avg']
    final_average = Decimal(str(avg_score)) if avg_score else Decimal('0')
    
    # Obtener letra de calificación
    letter_grade = _get_letter_grade(final_average)
    
    # Crear o actualizar resumen
    summary, created = StudentGradeSummary.objects.update_or_create(
        student=student,
        subject=subject,
        period=period,
        academic_year=academic_year,
        defaults={
            'final_average': final_average,
            'letter_grade': letter_grade,
            'total_activities': grade_records.count(),
            'last_updated': timezone.now()
        }
    )
    
    return summary

def _get_letter_grade(score):
    """Obtener letra de calificación según el puntaje"""
    try:
        grading_scale = GradingScale.objects.filter(
            min_value__lte=score,
            max_value__gte=score
        ).first()
        
        return grading_scale.letter_grade if grading_scale else 'F'
    except:
        return 'F'

class GradingReportsView(LoginRequiredMixin, TemplateView):
    """Vista de reportes de calificaciones"""
    template_name = 'academics_extended/grading_reports.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        current_year = AcademicYear.objects.filter(is_current=True).first()
        
        if user.profile.role == 'teacher':
            # Reportes para profesores
            teacher_subjects = SubjectAssignment.objects.filter(
                teacher=user,
                academic_year=current_year
            ).values_list('subject', flat=True)
            
            # Estadísticas por materia
            subject_stats = []
            for subject_id in teacher_subjects:
                subject = Subject.objects.get(id=subject_id)
                summaries = StudentGradeSummary.objects.filter(
                    subject=subject,
                    academic_year=current_year
                )
                
                if summaries.exists():
                    avg_score = summaries.aggregate(Avg('final_average'))['final_average__avg']
                    subject_stats.append({
                        'subject': subject,
                        'average_score': round(float(avg_score), 2) if avg_score else 0,
                        'total_students': summaries.values('student').distinct().count(),
                        'graded_activities': summaries.aggregate(Sum('total_activities'))['total_activities__sum'] or 0
                    })
            
            context['subject_stats'] = subject_stats
            
        elif user.profile.role in ['admin', 'secretary']:
            # Reportes administrativos
            all_summaries = StudentGradeSummary.objects.filter(academic_year=current_year)
            
            # Estadísticas generales
            context['general_stats'] = {
                'total_students_graded': all_summaries.values('student').distinct().count(),
                'total_subjects': all_summaries.values('subject').distinct().count(),
                'average_grade': round(float(all_summaries.aggregate(Avg('final_average'))['final_average__avg'] or 0), 2),
                'total_activities': all_summaries.aggregate(Sum('total_activities'))['total_activities__sum'] or 0
            }
            
            # Distribución por letra de calificación
            grade_distribution = all_summaries.values('letter_grade').annotate(
                count=Count('id')
            ).order_by('letter_grade')
            
            context['grade_distribution'] = grade_distribution
        
        context['current_year'] = current_year
        return context
