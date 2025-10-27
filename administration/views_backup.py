from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, Count, Avg, Sum
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import date, timedelta
from decimal import Decimal
import json

from academics_extended.models import *
from authentication.models import UserProfile


class SecretaryDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Dashboard principal para secretaría académica y administradores"""
    template_name = 'administration/secretary_dashboard.html'
    
    def test_func(self):
        return hasattr(self.request.user, 'profile') and self.request.user.profile.role in ['admin', 'secretary']
    
    def get_template_names(self):
        """Devolver template específico según el rol"""
        if hasattr(self.request.user, 'profile') and self.request.user.profile.role == 'admin':
            return ['administration/admin_dashboard.html']
        return ['administration/secretary_dashboard.html']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Información del usuario actual
        context['user_role'] = self.request.user.profile.role if hasattr(self.request.user, 'profile') else 'unknown'
        context['is_admin'] = context['user_role'] == 'admin'
        
        # Estadísticas generales del colegio
        context['total_students'] = Student.objects.count()
        context['total_teachers'] = UserProfile.objects.filter(role='teacher').count()
        context['total_courses'] = Course.objects.count()
        context['total_subjects'] = Subject.objects.count()
        
        # Si es administrador, agregar estadísticas adicionales
        if context['is_admin']:
            # Estadísticas de usuarios del sistema
            context['total_users'] = User.objects.count()
            context['total_admins'] = UserProfile.objects.filter(role='admin').count()
            context['total_secretaries'] = UserProfile.objects.filter(role='secretary').count()
            
            # Estadísticas académicas avanzadas
            context['total_academic_years'] = AcademicYear.objects.count()
            context['current_academic_year'] = AcademicYear.objects.filter(is_current=True).first()
            context['total_grades'] = Grade.objects.count()
            
            # Actividad reciente del sistema
            context['recent_logins'] = User.objects.filter(
                last_login__gte=timezone.now() - timedelta(days=7)
            ).count()
        
        # Estudiantes por grado
        students_by_grade = (
            Student.objects
            .select_related('course__grade')
            .values('course__grade__name')
            .annotate(count=Count('id'))
            .order_by('course__grade__order')
        )
        context['students_by_grade'] = students_by_grade
        
        # Asistencia del mes actual
        current_month = timezone.now().month
        attendance_stats = Attendance.objects.filter(
            date__month=current_month
        ).values('status').annotate(count=Count('id'))
        
        context['attendance_stats'] = {
            stat['status']: stat['count'] for stat in attendance_stats
        }
        
        # Calificaciones recientes (últimas 7 días)
        recent_grades = GradeRecord.objects.filter(
            date_recorded__gte=timezone.now().date() - timedelta(days=7)
        ).count()
        context['recent_grades'] = recent_grades
        
        # Estudiantes con bajo rendimiento (promedio < 3.0)
        low_performance_students = (
            StudentGradeSummary.objects
            .filter(final_average__lt=3.0)
            .select_related('student__user')
            .count()
        )
        context['low_performance_students'] = low_performance_students
        
        # Próximos eventos importantes
        context['upcoming_events'] = self._get_upcoming_events()
        
        return context
    
    def _get_upcoming_events(self):
        """Eventos importantes próximos"""
        events = []
        
        # Fin de períodos académicos (simulado)
        from datetime import datetime
        today = datetime.now().date()
        
        # Agregar eventos importantes para secretaría
        events.append({
            'title': 'Cierre Período 1',
            'date': today + timedelta(days=15),
            'type': 'academic',
            'description': 'Fecha límite para ingreso de calificaciones'
        })
        
        events.append({
            'title': 'Reunión de Padres',
            'date': today + timedelta(days=20),
            'type': 'meeting',
            'description': 'Entrega de boletines académicos'
        })
        
        return events


class TeacherGradeEntryView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Panel para profesores: entrada rápida de calificaciones"""
    template_name = 'administration/teacher_grade_entry.html'
    
    def test_func(self):
        return hasattr(self.request.user, 'profile') and self.request.user.profile.role == 'teacher'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = self.request.user
        
        # Mis asignaciones de materias
        my_assignments = SubjectAssignment.objects.filter(
            teacher=teacher
        ).select_related('subject', 'course', 'course__grade')
        
        context['my_assignments'] = my_assignments
        
        # Si se selecciona una asignación específica
        assignment_id = self.request.GET.get('assignment')
        if assignment_id:
            try:
                assignment = SubjectAssignment.objects.get(
                    id=assignment_id, teacher=teacher
                )
                context['selected_assignment'] = assignment
                
                # Estudiantes del curso
                students = Student.objects.filter(
                    course=assignment.course
                ).select_related('user').order_by('user__last_name')
                
                context['students'] = students
                
                # Calificaciones existentes para este período
                period = self.request.GET.get('period', 'Período 1')
                context['selected_period'] = period
                
                # Obtener calificaciones existentes
                existing_grades = {}
                grades = GradeRecord.objects.filter(
                    subject=assignment.subject,
                    teacher=teacher,
                    period=period,
                    student__in=students
                )
                
                for grade in grades:
                    if grade.student_id not in existing_grades:
                        existing_grades[grade.student_id] = []
                    existing_grades[grade.student_id].append(grade)
                
                context['existing_grades'] = existing_grades
                
            except SubjectAssignment.DoesNotExist:
                messages.error(self.request, 'Asignación no encontrada.')
        
        context['periods'] = ['Período 1', 'Período 2', 'Período 3', 'Período 4']
        
        return context


# === API VIEWS PARA FUNCIONALIDAD AJAX ===

@login_required
def save_grade_api(request):
    """API para guardar calificaciones rápidamente"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            student_id = data.get('student_id')
            subject_id = data.get('subject_id')
            activity_name = data.get('activity_name')
            grade_value = data.get('grade_value')
            period = data.get('period')
            activity_type = data.get('activity_type', 'Evaluación')
            
            # Validaciones
            student = Student.objects.get(id=student_id)
            subject = Subject.objects.get(id=subject_id)
            
            # Crear o actualizar calificación
            grade_record, created = GradeRecord.objects.get_or_create(
                student=student,
                subject=subject,
                teacher=request.user,
                activity_name=activity_name,
                period=period,
                defaults={
                    'grade_value': Decimal(str(grade_value)),
                    'activity_type': activity_type,
                    'date_recorded': timezone.now().date()
                }
            )
            
            if not created:
                grade_record.grade_value = Decimal(str(grade_value))
                grade_record.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Calificación guardada exitosamente'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al guardar: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})


# === CONTROL DE ASISTENCIA ===

class AttendanceControlView(LoginRequiredMixin, TemplateView):
    """Control de asistencia diaria para profesores"""
    template_name = 'administration/attendance_control.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Solo profesores pueden acceder
        if not hasattr(self.request.user, 'userprofile') or self.request.user.userprofile.role != 'teacher':
            context['error'] = 'Solo los profesores pueden acceder al control de asistencia'
            return context
        
        # Obtener asignaciones del profesor
        from academics_extended.models import TeacherSubjectAssignment, Student, AttendanceRecord
        from django.utils import timezone
        
        teacher_assignments = TeacherSubjectAssignment.objects.filter(
            teacher=self.request.user
        ).select_related('subject', 'course', 'course__grade')
        
        # Filtrar por asignación seleccionada
        selected_assignment_id = self.request.GET.get('assignment')
        selected_assignment = None
        students = []
        today_attendance = {}
        
        if selected_assignment_id:
            try:
                selected_assignment = teacher_assignments.get(id=selected_assignment_id)
                students = Student.objects.filter(
                    course=selected_assignment.course
                ).select_related('user').order_by('user__last_name', 'user__first_name')
                
                # Obtener asistencia de hoy
                today = timezone.now().date()
                today_records = AttendanceRecord.objects.filter(
                    student__in=students,
                    date=today,
                    subject=selected_assignment.subject
                )
                
                today_attendance = {
                    record.student.id: record.status 
                    for record in today_records
                }
                
            except TeacherSubjectAssignment.DoesNotExist:
                pass
        
        context.update({
            'teacher_assignments': teacher_assignments,
            'selected_assignment': selected_assignment,
            'students': students,
            'today_attendance': today_attendance,
            'today_date': timezone.now().date(),
        })
        
        return context


@csrf_exempt
def save_attendance_api(request):
    """API para guardar asistencia vía AJAX"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'})
    
    try:
        import json
        data = json.loads(request.body)
        
        student_id = data.get('student_id')
        subject_id = data.get('subject_id')
        status = data.get('status')
        date_str = data.get('date')
        notes = data.get('notes', '')
        
        # Validaciones
        if not all([student_id, subject_id, status, date_str]):
            return JsonResponse({'success': False, 'message': 'Datos incompletos'})
        
        if status not in ['present', 'absent', 'late', 'justified']:
            return JsonResponse({'success': False, 'message': 'Estado de asistencia inválido'})
        
        # Importar modelos
        from academics_extended.models import Student, Subject, AttendanceRecord
        from datetime import datetime
        
        # Obtener objetos
        student = Student.objects.get(id=student_id)
        subject = Subject.objects.get(id=subject_id)
        attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Crear o actualizar registro
        attendance, created = AttendanceRecord.objects.update_or_create(
            student=student,
            subject=subject,
            date=attendance_date,
            defaults={
                'status': status,
                'teacher': request.user,
                'notes': notes,
            }
        )
        
        # Traducir estado para respuesta
        status_labels = {
            'present': 'Presente',
            'absent': 'Ausente', 
            'late': 'Tardanza',
            'justified': 'Justificado'
        }
        
        return JsonResponse({
            'success': True,
            'message': f'Asistencia guardada: {status_labels.get(status, status)}',
            'student': student.user.get_full_name(),
            'status': status_labels.get(status, status)
        })
        
    except Student.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Estudiante no encontrado'})
    except Subject.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Materia no encontrada'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})


# === GESTIÓN DE ESTUDIANTES ===

class StudentManagementView(LoginRequiredMixin, TemplateView):
    """Gestión completa de estudiantes para secretaría"""
    template_name = 'administration/student_management.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Solo secretarios y admins pueden acceder
        if not hasattr(self.request.user, 'profile') or \
           self.request.user.profile.role not in ['secretary', 'admin']:
            context['error'] = 'Solo la secretaría puede acceder a la gestión de estudiantes'
            return context
        
        # Obtener parámetros de búsqueda y filtros
        search = self.request.GET.get('search', '')
        course_filter = self.request.GET.get('course', '')
        status_filter = self.request.GET.get('status', 'all')
        
        # Base query
        students = Student.objects.select_related('user', 'course', 'course__grade').all()
        
        # Aplicar filtros
        if search:
            students = students.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(student_id__icontains=search)
            )
        
        if course_filter:
            students = students.filter(course_id=course_filter)
        
        if status_filter != 'all':
            # Filtrar por estado del estudiante directamente
            students = students.filter(status=status_filter)
        
        # Ordenar por apellido
        students = students.order_by('user__last_name', 'user__first_name')
        
        # Obtener datos para filtros
        courses = Course.objects.select_related('grade').all().order_by('grade__order', 'section')
        
        # Estadísticas rápidas
        total_students = Student.objects.count()
        active_students = Student.objects.filter(status='active').count()
        
        context.update({
            'students': students,
            'courses': courses,
            'search': search,
            'course_filter': course_filter,
            'status_filter': status_filter,
            'total_students': total_students,
            'active_students': active_students,
        })
        
        return context


class StudentDetailView(LoginRequiredMixin, TemplateView):
    """Vista detallada de un estudiante"""
    template_name = 'administration/student_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        student_id = kwargs.get('student_id')
        student = get_object_or_404(Student, id=student_id)
        
        # Obtener calificaciones del estudiante
        grades = GradeRecord.objects.filter(
            student=student
        ).select_related('subject', 'teacher').order_by('-date_recorded')[:20]
        
        # Obtener asistencia reciente
        from academics_extended.models import AttendanceRecord
        attendance = AttendanceRecord.objects.filter(
            student=student
        ).select_related('subject', 'teacher').order_by('-date')[:30]
        
        # Calcular estadísticas
        from django.db.models import Avg, Count
        avg_grade = grades.aggregate(avg=Avg('grade_value'))['avg']
        attendance_stats = attendance.aggregate(
            total=Count('id'),
            present=Count('id', filter=Q(status='present')),
            absent=Count('id', filter=Q(status='absent'))
        )
        
        # Calcular porcentaje de asistencia
        if attendance_stats['total'] > 0:
            attendance_percentage = (attendance_stats['present'] / attendance_stats['total']) * 100
        else:
            attendance_percentage = 0
        
        context.update({
            'student': student,
            'grades': grades,
            'attendance': attendance,
            'avg_grade': round(avg_grade, 2) if avg_grade else 0,
            'attendance_percentage': round(attendance_percentage, 1),
            'attendance_stats': attendance_stats,
        })
        
        return context


@csrf_exempt
def quick_student_search_api(request):
    """API para búsqueda rápida de estudiantes"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'})
    
    try:
        data = json.loads(request.body)
        query = data.get('query', '').strip()
        
        if len(query) < 2:
            return JsonResponse({'success': False, 'message': 'Mínimo 2 caracteres'})
        
        # Buscar estudiantes
        students = Student.objects.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(student_id__icontains=query)
        ).select_related('user', 'course', 'course__grade')[:10]
        
        results = []
        for student in students:
            results.append({
                'id': student.id,
                'name': student.user.get_full_name(),
                'student_id': student.student_id,
                'course': f"{student.course.grade.name} - {student.course.section}" if student.course else "Sin curso",
                'avatar': student.user.userprofile.avatar.url if hasattr(student.user, 'userprofile') and student.user.userprofile.avatar else '/static/images/default-avatar.png'
            })
        
        return JsonResponse({
            'success': True,
            'results': results,
            'count': len(results)
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})


# === SISTEMA DE REPORTES PDF ===

from django.template.loader import get_template
from django.http import HttpResponse
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch


class ReportGeneratorView(LoginRequiredMixin, TemplateView):
    """Generador de reportes PDF para secretaría"""
    template_name = 'administration/report_generator.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Solo secretarios y admins pueden generar reportes
        if not hasattr(self.request.user, 'userprofile') or \
           self.request.user.userprofile.role not in ['secretary', 'admin']:
            context['error'] = 'Solo la secretaría puede generar reportes'
            return context
        
        # Obtener datos para los formularios
        courses = Course.objects.select_related('grade').order_by('grade__order', 'section')
        students = Student.objects.select_related('user', 'course').order_by('user__last_name')
        
        context.update({
            'courses': courses,
            'students': students,
        })
        
        return context


def generate_bulletin_pdf(request, student_id):
    """Generar boletín individual en PDF"""
    # Obtener estudiante
    student = get_object_or_404(Student, id=student_id)
    
    # Crear buffer para PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch)
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1,  # Centrado
    )
    
    # Contenido del boletín
    elements = []
    
    # Encabezado
    elements.append(Paragraph("INSTITUCIÓN EDUCATIVA", title_style))
    elements.append(Paragraph("BOLETÍN ACADÉMICO", title_style))
    elements.append(Spacer(1, 20))
    
    # Información del estudiante
    student_info = [
        ['Estudiante:', student.user.get_full_name()],
        ['ID Estudiantil:', student.student_id],
        ['Curso:', f"{student.course.grade.name} - Sección {student.course.section}" if student.course else "Sin curso"],
        ['Año Académico:', '2025'],
    ]
    
    student_table = Table(student_info, colWidths=[2*inch, 4*inch])
    student_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(student_table)
    elements.append(Spacer(1, 20))
    
    # Calificaciones por materia
    grades_data = [['Materia', 'Período 1', 'Período 2', 'Período 3', 'Promedio']]
    
    # Obtener calificaciones del estudiante
    from academics_extended.models import GradeRecord, Subject
    subjects = Subject.objects.all()
    
    for subject in subjects:
        # Calcular promedios por período
        p1_grades = GradeRecord.objects.filter(
            student=student, subject=subject, period='Período 1'
        ).values_list('grade_value', flat=True)
        
        p2_grades = GradeRecord.objects.filter(
            student=student, subject=subject, period='Período 2'
        ).values_list('grade_value', flat=True)
        
        p3_grades = GradeRecord.objects.filter(
            student=student, subject=subject, period='Período 3'
        ).values_list('grade_value', flat=True)
        
        # Calcular promedios
        p1_avg = sum(p1_grades) / len(p1_grades) if p1_grades else 0
        p2_avg = sum(p2_grades) / len(p2_grades) if p2_grades else 0
        p3_avg = sum(p3_grades) / len(p3_grades) if p3_grades else 0
        
        final_avg = (p1_avg + p2_avg + p3_avg) / 3 if any([p1_avg, p2_avg, p3_avg]) else 0
        
        grades_data.append([
            subject.name,
            f"{p1_avg:.1f}" if p1_avg else "N/A",
            f"{p2_avg:.1f}" if p2_avg else "N/A", 
            f"{p3_avg:.1f}" if p3_avg else "N/A",
            f"{final_avg:.1f}" if final_avg else "N/A"
        ])
    
    # Tabla de calificaciones
    grades_table = Table(grades_data, colWidths=[2.5*inch, 1*inch, 1*inch, 1*inch, 1*inch])
    grades_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    elements.append(grades_table)
    elements.append(Spacer(1, 30))
    
    # Observaciones
    elements.append(Paragraph("Observaciones:", styles['Heading3']))
    elements.append(Paragraph("El estudiante ha mostrado un desempeño satisfactorio durante el período académico.", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Firmas
    signature_data = [
        ['_________________________', '_________________________'],
        ['Director', 'Secretario Académico'],
    ]
    
    signature_table = Table(signature_data, colWidths=[3*inch, 3*inch])
    signature_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(signature_table)
    
    # Construir PDF
    doc.build(elements)
    
    # Obtener PDF del buffer
    pdf_data = buffer.getvalue()
    buffer.close()
    
    # Crear respuesta HTTP
    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="boletin_{student.student_id}_{student.user.last_name}.pdf"'
    
    return response


def generate_course_list_pdf(request, course_id):
    """Generar lista de curso en PDF"""
    # Obtener curso
    course = get_object_or_404(Course, id=course_id)
    students = Student.objects.filter(course=course).select_related('user').order_by('user__last_name')
    
    # Crear buffer para PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch)
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1,  # Centrado
    )
    
    # Contenido
    elements = []
    
    # Encabezado
    elements.append(Paragraph("INSTITUCIÓN EDUCATIVA", title_style))
    elements.append(Paragraph(f"LISTA DE ESTUDIANTES - {course.grade.name} SECCIÓN {course.section}", title_style))
    elements.append(Spacer(1, 20))
    
    # Información del curso
    course_info = [
        ['Curso:', f"{course.grade.name} - Sección {course.section}"],
        ['Año Académico:', '2025'],
        ['Total Estudiantes:', str(students.count())],
        ['Fecha:', timezone.now().strftime('%d/%m/%Y')],
    ]
    
    course_table = Table(course_info, colWidths=[2*inch, 4*inch])
    course_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(course_table)
    elements.append(Spacer(1, 20))
    
    # Lista de estudiantes
    student_data = [['#', 'ID Estudiantil', 'Apellidos y Nombres', 'Firma']]
    
    for i, student in enumerate(students, 1):
        student_data.append([
            str(i),
            student.student_id,
            student.user.get_full_name(),
            '____________________'
        ])
    
    # Tabla de estudiantes
    student_table = Table(student_data, colWidths=[0.5*inch, 1.5*inch, 3*inch, 2*inch])
    student_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (2, 1), (2, -1), 'LEFT'),  # Nombres alineados a la izquierda
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    elements.append(student_table)
    
    # Construir PDF
    doc.build(elements)
    
    # Obtener PDF del buffer
    pdf_data = buffer.getvalue()
    buffer.close()
    
    # Crear respuesta HTTP
    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="lista_{course.grade.name}_{course.section}.pdf"'
    
    return response
from datetime import datetime

class ReportGeneratorView(LoginRequiredMixin, TemplateView):
    """Vista principal para generar reportes"""
    template_name = 'administration/report_generator.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Solo secretarios y admins pueden generar reportes
        if not hasattr(self.request.user, 'userprofile') or \
           self.request.user.userprofile.role not in ['secretary', 'admin']:
            context['error'] = 'Solo la secretaría puede generar reportes'
            return context
        
        # Obtener datos para los filtros
        from academics_extended.models import Course, Subject, Grade
        
        courses = Course.objects.select_related('grade').all().order_by('grade__order', 'section')
        subjects = Subject.objects.all().order_by('name')
        grades = Grade.objects.all().order_by('order')
        students = Student.objects.select_related('user', 'course').all().order_by('user__last_name')
        
        # Reportes disponibles
        report_types = [
            {'key': 'bulletin', 'name': 'Boletín Individual', 'icon': 'fa-file-alt'},
            {'key': 'course_summary', 'name': 'Resumen de Curso', 'icon': 'fa-chart-bar'},
            {'key': 'attendance_report', 'name': 'Reporte de Asistencia', 'icon': 'fa-calendar-check'},
            {'key': 'student_certificate', 'name': 'Certificado de Estudiante', 'icon': 'fa-certificate'},
            {'key': 'course_list', 'name': 'Lista de Curso', 'icon': 'fa-list'},
        ]
        
        context.update({
            'courses': courses,
            'subjects': subjects,
            'grades': grades,
            'students': students,
            'report_types': report_types,
        })
        
        return context


def generate_student_bulletin_pdf(request):
    """Generar boletín individual de estudiante en PDF"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'})
    
    try:
        student_id = request.POST.get('student_id')
        period = request.POST.get('period', 'Período 1')
        
        student = get_object_or_404(Student, id=student_id)
        
        # Crear respuesta HTTP para PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="boletin_{student.student_id}_{period}.pdf"'
        
        # Crear documento PDF
        doc = SimpleDocTemplate(response, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Estilo personalizado para el título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.darkblue,
            alignment=1,  # Centrado
            spaceAfter=30
        )
        
        # Título del boletín
        story.append(Paragraph("BOLETÍN ACADÉMICO", title_style))
        story.append(Spacer(1, 20))
        
        # Información del estudiante
        student_info = [
            ['Estudiante:', student.user.get_full_name()],
            ['ID:', student.student_id],
            ['Curso:', f"{student.course.grade.name} - Sección {student.course.section}" if student.course else "Sin curso"],
            ['Período:', period],
            ['Fecha:', datetime.now().strftime('%d/%m/%Y')]
        ]
        
        student_table = Table(student_info, colWidths=[2*inch, 4*inch])
        student_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(student_table)
        story.append(Spacer(1, 30))
        
        # Obtener calificaciones del período
        grades = GradeRecord.objects.filter(
            student=student,
            period=period
        ).select_related('subject', 'teacher').order_by('subject__name', 'date_recorded')
        
        if grades.exists():
            # Tabla de calificaciones
            story.append(Paragraph("CALIFICACIONES", styles['Heading2']))
            story.append(Spacer(1, 15))
            
            # Agrupar por materia
            from collections import defaultdict
            grades_by_subject = defaultdict(list)
            for grade in grades:
                grades_by_subject[grade.subject].append(grade)
            
            # Crear tabla de calificaciones
            grade_data = [['Materia', 'Actividades', 'Promedio', 'Profesor']]
            
            for subject, subject_grades in grades_by_subject.items():
                activities = []
                total_grade = 0
                for grade in subject_grades:
                    activities.append(f"{grade.activity_name}: {grade.grade_value}")
                    total_grade += float(grade.grade_value)
                
                average = total_grade / len(subject_grades) if subject_grades else 0
                teacher_name = subject_grades[0].teacher.get_full_name() if subject_grades else ''
                
                grade_data.append([
                    subject.name,
                    '\n'.join(activities),
                    f"{average:.2f}",
                    teacher_name
                ])
            
            grade_table = Table(grade_data, colWidths=[2*inch, 3*inch, 1*inch, 1.5*inch])
            grade_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ALIGN', (1, 1), (1, -1), 'LEFT'),  # Actividades alineadas a la izquierda
            ]))
            
            story.append(grade_table)
            
        else:
            story.append(Paragraph("No hay calificaciones registradas para este período", styles['Normal']))
        
        # Construir PDF
        doc.build(story)
        
        # Guardar registro del reporte generado
        from .models import GeneratedReport, ReportTemplate
        template, created = ReportTemplate.objects.get_or_create(
            report_type='bulletin',
            name='Boletín Estándar',
            defaults={'template_content': 'Boletín académico individual', 'parameters': {}}
        )
        
        GeneratedReport.objects.create(
            template=template,
            title=f"Boletín de {student.user.get_full_name()} - {period}",
            generated_by=request.user,
            file_format='pdf',
            parameters_used={'student_id': student_id, 'period': period}
        )
        
        return response
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error al generar boletín: {str(e)}'})


def generate_course_list_pdf(request):
    """Generar lista de curso en PDF"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'})
    
    try:
        course_id = request.POST.get('course_id')
        course = get_object_or_404(Course, id=course_id)
        
        # Crear respuesta HTTP para PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="lista_{course.grade.name}_{course.section}.pdf"'
        
        # Crear documento PDF
        doc = SimpleDocTemplate(response, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.darkblue,
            alignment=1,
            spaceAfter=20
        )
        
        story.append(Paragraph(f"LISTA DE ESTUDIANTES - {course.grade.name} SECCIÓN {course.section}", title_style))
        story.append(Spacer(1, 20))
        
        # Obtener estudiantes del curso
        students = Student.objects.filter(course=course).select_related('user').order_by('user__last_name', 'user__first_name')
        
        if students.exists():
            # Crear tabla con estudiantes
            student_data = [['#', 'ID Estudiante', 'Apellidos y Nombres', 'Fecha Nacimiento']]
            
            for i, student in enumerate(students, 1):
                student_data.append([
                    str(i),
                    student.student_id,
                    student.user.get_full_name(),
                    student.birth_date.strftime('%d/%m/%Y') if student.birth_date else 'N/A'
                ])
            
            student_table = Table(student_data, colWidths=[0.5*inch, 1.5*inch, 3*inch, 1.5*inch])
            student_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ALIGN', (2, 1), (2, -1), 'LEFT'),  # Nombres alineados a la izquierda
            ]))
            
            story.append(student_table)
            story.append(Spacer(1, 30))
            
            # Información adicional
            info = [
                f"Total de estudiantes: {students.count()}",
                f"Generado el: {datetime.now().strftime('%d/%m/%Y a las %H:%M')}",
                f"Por: {request.user.get_full_name()}"
            ]
            
            for line in info:
                story.append(Paragraph(line, styles['Normal']))
                story.append(Spacer(1, 10))
                
        else:
            story.append(Paragraph("No hay estudiantes matriculados en este curso", styles['Normal']))
        
        # Construir PDF
        doc.build(story)
        return response
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error al generar lista: {str(e)}'})


@csrf_exempt  
@login_required
def create_student_api(request):
    """Centro de comunicación para staff educativo"""
    template_name = 'administration/communication_center.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Solo staff puede acceder
        if not hasattr(self.request.user, 'userprofile') or \
           self.request.user.userprofile.role not in ['secretary', 'admin', 'teacher']:
            context['error'] = 'Solo el personal educativo puede acceder'
            return context
        
        # from communications.models import Announcement, InternalMessage
        
        # Anuncios recientes
        recent_announcements = Announcement.objects.filter(
            is_active=True,
            active_until__gte=timezone.now().date()
        ).order_by('-created_at')[:5]
        
        # Mensajes recibidos no leídos
        unread_messages = InternalMessage.objects.filter(
            recipient=self.request.user,
            is_read=False
        ).count()
        
        # Mensajes recibidos recientes
        recent_messages = InternalMessage.objects.filter(
            recipient=self.request.user
        ).select_related('sender').order_by('-sent_at')[:10]
        
        # Mis mensajes enviados recientes
        sent_messages = InternalMessage.objects.filter(
            sender=self.request.user
        ).select_related('recipient').order_by('-sent_at')[:5]
        
        # Lista de staff para enviar mensajes
        staff_users = User.objects.filter(
            userprofile__role__in=['secretary', 'admin', 'teacher']
        ).exclude(id=self.request.user.id).order_by('first_name', 'last_name')
        
        context.update({
            'recent_announcements': recent_announcements,
            'unread_messages': unread_messages,
            'recent_messages': recent_messages,
            'sent_messages': sent_messages,
            'staff_users': staff_users,
            'user_role': self.request.user.userprofile.role,
        })
        
        return context


@csrf_exempt
def send_message_api(request):
    """API para enviar mensajes internos"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'})
    
    try:
        data = json.loads(request.body)
        
        recipient_id = data.get('recipient_id')
        subject = data.get('subject', '').strip()
        message = data.get('message', '').strip()
        
        # Validaciones
        if not all([recipient_id, subject, message]):
            return JsonResponse({'success': False, 'message': 'Todos los campos son requeridos'})
        
        # Obtener receptor
        try:
            recipient = User.objects.get(id=recipient_id)
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Usuario destinatario no encontrado'})
        
        # Crear mensaje
        from communications.models import InternalMessage
        
        message_obj = InternalMessage.objects.create(
            sender=request.user,
            recipient=recipient,
            subject=subject,
            message=message
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Mensaje enviado a {recipient.get_full_name()}',
            'message_id': message_obj.id
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})


@csrf_exempt
def mark_message_read_api(request):
    """API para marcar mensajes como leídos"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'})
    
    try:
        data = json.loads(request.body)
        message_id = data.get('message_id')
        
        from communications.models import InternalMessage
        
        # Obtener mensaje
        message = InternalMessage.objects.get(
            id=message_id,
            recipient=request.user
        )
        
        # Marcar como leído
        if not message.is_read:
            message.is_read = True
            message.read_at = timezone.now()
            message.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Mensaje marcado como leído'
        })
        
    except InternalMessage.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Mensaje no encontrado'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})


@csrf_exempt
def create_announcement_api(request):
    """API para crear anuncios"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'})
    
    # Solo secretarios y admins pueden crear anuncios
    if not hasattr(request.user, 'profile') or \
       request.user.profile.role not in ['secretary', 'admin']:
        return JsonResponse({'success': False, 'message': 'Sin permisos para crear anuncios'})
    
    try:
        data = json.loads(request.body)
        
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        target_audience = data.get('target_audience', 'all')
        priority = data.get('priority', 'normal')
        active_days = int(data.get('active_days', 7))
        
        # Validaciones
        if not all([title, content]):
            return JsonResponse({'success': False, 'message': 'Título y contenido son requeridos'})
        
        # Calcular fecha de vencimiento
        from datetime import timedelta
        active_until = timezone.now().date() + timedelta(days=active_days)
        
        # Crear anuncio
        from communications.models import Announcement
        
        announcement = Announcement.objects.create(
            title=title,
            content=content,
            target_audience=target_audience,
            priority=priority,
            active_until=active_until,
            created_by=request.user
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Anuncio "{title}" creado exitosamente',
            'announcement_id': announcement.id
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})


@csrf_exempt  
@login_required
def create_student_api(request):
    """API para crear nuevos estudiantes"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'})
    
    # Solo secretarios y admins pueden crear estudiantes
    if not hasattr(request.user, 'profile') or \
       request.user.profile.role not in ['secretary', 'admin']:
        return JsonResponse({'success': False, 'message': 'Sin permisos para crear estudiantes'})
    
    try:
        data = json.loads(request.body)
        
        # Extraer datos del formulario
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        student_id = data.get('student_id', '').strip()
        email = data.get('email', '').strip()
        date_of_birth = data.get('date_of_birth', '')
        course_id = data.get('course')
        phone = data.get('phone', '').strip()
        address = data.get('address', '').strip()
        
        # Validaciones
        if not all([first_name, last_name, student_id, course_id]):
            return JsonResponse({'success': False, 'message': 'Nombres, apellidos, ID y curso son requeridos'})
        
        # Verificar que el ID del estudiante no exista
        if Student.objects.filter(student_id=student_id).exists():
            return JsonResponse({'success': False, 'message': f'Ya existe un estudiante con ID: {student_id}'})
        
        # Verificar que el curso existe
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'El curso seleccionado no existe'})
        
        # Crear usuario para el estudiante
        username = f"est_{student_id}"
        if User.objects.filter(username=username).exists():
            # Si ya existe, añadir sufijo numérico
            counter = 1
            while User.objects.filter(username=f"{username}_{counter}").exists():
                counter += 1
            username = f"{username}_{counter}"
        
        # Crear usuario
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email if email else f"{username}@colegiolabalsa.edu.co",
            password=student_id  # Usar ID como contraseña inicial
        )
        
        # Crear perfil de usuario como estudiante
        from authentication.models import UserProfile
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={'role': 'student'}
        )
        
        # Crear registro de estudiante
        from datetime import date, datetime
        
        # Procesar fecha de nacimiento
        birth_date_obj = date.today()  # Valor por defecto
        if date_of_birth:
            try:
                birth_date_obj = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
            except ValueError:
                pass  # Usar fecha por defecto si no es válida
        
        student = Student.objects.create(
            user=user,
            student_id=student_id,
            course=course,
            enrollment_date=date.today(),
            guardian_name="Por definir",
            guardian_phone=phone if phone else "Por definir",
            guardian_email=email if email else "",
            address=address if address else "Por definir",
            birth_date=birth_date_obj,
            status='active'
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Estudiante {first_name} {last_name} creado exitosamente',
            'student': {
                'id': student.id,
                'name': f"{first_name} {last_name}",
                'student_id': student_id,
                'course': f"{course.grade.name}{course.section}",
                'username': username
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error al crear estudiante: {str(e)}'})


# ============================================================================
# VISTAS ESPECÍFICAS PARA ADMINISTRADOR
# ============================================================================

class AdminUserManagementView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Vista para gestión de usuarios del sistema (solo administradores)"""
    template_name = 'administration/admin_users.html'
    
    def test_func(self):
        return hasattr(self.request.user, 'profile') and self.request.user.profile.role == 'admin'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Todos los usuarios del sistema
        context['all_users'] = User.objects.select_related('profile').order_by('date_joined')
        
        # Estadísticas de usuarios
        context['users_by_role'] = UserProfile.objects.values('role').annotate(count=Count('id'))
        
        # Usuarios recientes (últimos 30 días)
        context['recent_users'] = User.objects.filter(
            date_joined__gte=timezone.now() - timedelta(days=30)
        ).count()
        
        return context


class SystemConfigView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Vista para configuración del sistema (solo administradores)"""
    template_name = 'administration/system_config.html'
    
    def test_func(self):
        return hasattr(self.request.user, 'profile') and self.request.user.profile.role == 'admin'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Configuración académica
        context['academic_years'] = AcademicYear.objects.all().order_by('-start_date')
        context['current_academic_year'] = AcademicYear.objects.filter(is_current=True).first()
        
        # Estadísticas del sistema
        context['total_models'] = {
            'grades': Grade.objects.count(),
            'subjects': Subject.objects.count(),
            'courses': Course.objects.count(),
            'students': Student.objects.count(),
            'time_slots': TimeSlot.objects.count(),
        }
        
        return context


class BackupManagementView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Vista para gestión de respaldos (solo administradores)"""
    template_name = 'administration/backup_management.html'
    
    def test_func(self):
        return hasattr(self.request.user, 'profile') and self.request.user.profile.role == 'admin'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Información de la base de datos
        import os
        from django.conf import settings
        from datetime import datetime
        
        db_path = settings.DATABASES['default']['NAME']
        
        if os.path.exists(db_path):
            # Información del archivo de BD
            stat = os.stat(db_path)
            context['db_info'] = {
                'file_name': os.path.basename(db_path),
                'full_path': db_path,
                'size_mb': round(stat.st_size / 1024 / 1024, 2),
                'last_modified': datetime.fromtimestamp(stat.st_mtime),
                'table_count': self._get_table_count(),
            }
        else:
            context['db_info'] = {
                'file_name': 'No encontrado',
                'full_path': db_path,
                'size_mb': 0,
                'last_modified': None,
                'table_count': 0,
            }
        
        # Fecha actual para templates
        context['today'] = datetime.now()
        
        return context
    
    def _get_table_count(self):
        """Contar número de tablas en la base de datos"""
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table'")
                return cursor.fetchone()[0]
        except:
            return 0


# === API VIEWS PARA GESTIÓN DE USUARIOS ===

@login_required
@require_http_methods(["POST"])
def toggle_user_status_api(request):
    """API para activar/desactivar usuarios"""
    if not (hasattr(request.user, 'profile') and request.user.profile.role == 'admin'):
        return JsonResponse({'error': 'Sin permisos'}, status=403)
    
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        
        if not user_id:
            return JsonResponse({'error': 'ID de usuario requerido'}, status=400)
        
        user = User.objects.get(id=user_id)
        
        # No permitir desactivar al propio usuario
        if user == request.user:
            return JsonResponse({'error': 'No puedes desactivar tu propia cuenta'}, status=400)
        
        # Cambiar estado
        user.is_active = not user.is_active
        user.save()
        
        return JsonResponse({
            'success': True,
            'user_id': user.id,
            'is_active': user.is_active,
            'message': f'Usuario {"activado" if user.is_active else "desactivado"} exitosamente'
        })
        
    except User.DoesNotExist:
        return JsonResponse({'error': 'Usuario no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f'Error: {str(e)}'}, status=500)


@login_required
@require_http_methods(["POST"])
def delete_user_api(request):
    """API para eliminar usuarios"""
    if not (hasattr(request.user, 'profile') and request.user.profile.role == 'admin'):
        return JsonResponse({'error': 'Sin permisos'}, status=403)
    
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        
        if not user_id:
            return JsonResponse({'error': 'ID de usuario requerido'}, status=400)
        
        user = User.objects.get(id=user_id)
        
        # No permitir eliminar al propio usuario
        if user == request.user:
            return JsonResponse({'error': 'No puedes eliminar tu propia cuenta'}, status=400)
        
        # No permitir eliminar otros administradores
        if hasattr(user, 'profile') and user.profile.role == 'admin':
            return JsonResponse({'error': 'No se pueden eliminar otros administradores'}, status=400)
        
        username = user.username
        user.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Usuario "{username}" eliminado exitosamente'
        })
        
    except User.DoesNotExist:
        return JsonResponse({'error': 'Usuario no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f'Error: {str(e)}'}, status=500)


@login_required
@require_http_methods(["POST"])
def create_user_api(request):
    """API para crear nuevos usuarios"""
    if not (hasattr(request.user, 'profile') and request.user.profile.role == 'admin'):
        return JsonResponse({'error': 'Sin permisos'}, status=403)
    
    try:
        data = json.loads(request.body)
        
        # Validar datos requeridos
        required_fields = ['username', 'email', 'first_name', 'last_name', 'role', 'password']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({'error': f'Campo {field} es requerido'}, status=400)
        
        # Verificar que el username no existe
        if User.objects.filter(username=data['username']).exists():
            return JsonResponse({'error': 'El nombre de usuario ya existe'}, status=400)
        
        # Verificar que el email no existe
        if User.objects.filter(email=data['email']).exists():
            return JsonResponse({'error': 'El email ya está en uso'}, status=400)
        
        # Crear usuario
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name']
        )
        
        # Crear perfil
        UserProfile.objects.create(
            user=user,
            role=data['role']
        )
        
        return JsonResponse({
            'success': True,
            'user_id': user.id,
            'message': f'Usuario "{user.username}" creado exitosamente'
        })
        
    except Exception as e:
        return JsonResponse({'error': f'Error: {str(e)}'}, status=500)


@login_required
@require_http_methods(["POST"])
def reset_password_api(request):
    """API para resetear contraseña de usuarios"""
    if not (hasattr(request.user, 'profile') and request.user.profile.role == 'admin'):
        return JsonResponse({'error': 'Sin permisos'}, status=403)
    
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        new_password = data.get('new_password', '123456')  # Contraseña temporal por defecto
        
        if not user_id:
            return JsonResponse({'error': 'ID de usuario requerido'}, status=400)
        
        user = User.objects.get(id=user_id)
        user.set_password(new_password)
        user.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Contraseña de "{user.username}" reseteada exitosamente',
            'temp_password': new_password
        })
        
    except User.DoesNotExist:
        return JsonResponse({'error': 'Usuario no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f'Error: {str(e)}'}, status=500)
