from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from academics.models import Student, AcademicYear, Course
import json


# === REPORTES ACADÉMICOS ===

class ReportTemplate(models.Model):
    """Plantillas de reportes predefinidas"""
    REPORT_TYPES = [
        ('bulletin', 'Boletín Individual'),
        ('course_summary', 'Resumen de Curso'),
        ('attendance_report', 'Reporte de Asistencia'),
        ('grade_analysis', 'Análisis de Rendimiento'),
        ('student_certificate', 'Certificado de Estudiante'),
        ('course_list', 'Lista de Curso'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='Nombre de la Plantilla')
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES, verbose_name='Tipo de Reporte')
    description = models.TextField(blank=True, verbose_name='Descripción')
    template_content = models.TextField(help_text='HTML template del reporte')
    css_styles = models.TextField(blank=True, help_text='CSS personalizado para el reporte')
    parameters = models.JSONField(default=dict, help_text='Parámetros configurables del reporte')
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Plantilla de Reporte'
        verbose_name_plural = 'Plantillas de Reportes'
        ordering = ['report_type', 'name']
    
    def __str__(self):
        return f"{self.get_report_type_display()} - {self.name}"


class GeneratedReport(models.Model):
    """Reportes generados y guardados"""
    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('html', 'HTML'),
    ]
    
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, verbose_name='Plantilla')
    title = models.CharField(max_length=200, verbose_name='Título del Reporte')
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Generado por')
    generated_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Generación')
    file_format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='pdf')
    file_path = models.FileField(upload_to='reports/%Y/%m/', verbose_name='Archivo')
    parameters_used = models.JSONField(default=dict, verbose_name='Parámetros Utilizados')
    download_count = models.PositiveIntegerField(default=0, verbose_name='Descargas')
    
    class Meta:
        verbose_name = 'Reporte Generado'
        verbose_name_plural = 'Reportes Generados'
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.title} - {self.generated_at.strftime('%d/%m/%Y')}"
    
    def increment_download(self):
        """Incrementar contador de descargas"""
        self.download_count += 1
        self.save(update_fields=['download_count'])


class Enrollment(models.Model):
    """Matrículas de estudiantes"""
    STATUS_CHOICES = [
        ('active', 'Activo'),
        ('inactive', 'Inactivo'),
        ('transferred', 'Trasladado'),
        ('graduated', 'Graduado'),
        ('suspended', 'Suspendido'),
        ('withdrawn', 'Retirado'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments', verbose_name='Estudiante')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, verbose_name='Año Académico')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='Curso')
    
    enrollment_date = models.DateField(verbose_name='Fecha de Matrícula')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='Estado')
    
    # Información financiera
    enrollment_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Valor de Matrícula')
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Pensión Mensual')
    
    # Seguimiento
    enrolled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Matriculado por')
    notes = models.TextField(blank=True, verbose_name='Observaciones')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.student.full_name} - {self.course} - {self.academic_year}"
    
    @property
    def is_current(self):
        """Verificar si es la matrícula del año actual"""
        return self.academic_year.is_current and self.status == 'active'
    
    class Meta:
        verbose_name = 'Matrícula'
        verbose_name_plural = 'Matrículas'
        unique_together = ['student', 'academic_year']
        ordering = ['-academic_year__start_date', 'student__last_name']


class PaymentConcept(models.Model):
    """Conceptos de pago (pensión, matrícula, etc.)"""
    TYPE_CHOICES = [
        ('enrollment', 'Matrícula'),
        ('monthly', 'Pensión Mensual'),
        ('supplies', 'Útiles Escolares'),
        ('uniform', 'Uniforme'),
        ('transport', 'Transporte'),
        ('food', 'Alimentación'),
        ('extra', 'Actividad Extracurricular'),
        ('other', 'Otro'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='Nombre del Concepto')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name='Tipo')
    description = models.TextField(blank=True, verbose_name='Descripción')
    default_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Valor por Defecto')
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    
    def __str__(self):
        return f"{self.name} - ${self.default_amount:,.0f}"
    
    class Meta:
        verbose_name = 'Concepto de Pago'
        verbose_name_plural = 'Conceptos de Pago'
        ordering = ['type', 'name']


class Payment(models.Model):
    """Control de pagos"""
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('paid', 'Pagado'),
        ('overdue', 'Vencido'),
        ('partial', 'Pago Parcial'),
        ('cancelled', 'Cancelado'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Efectivo'),
        ('transfer', 'Transferencia Bancaria'),
        ('card', 'Tarjeta'),
        ('check', 'Cheque'),
        ('other', 'Otro'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments', verbose_name='Estudiante')
    concept = models.ForeignKey(PaymentConcept, on_delete=models.CASCADE, verbose_name='Concepto')
    
    # Fechas
    due_date = models.DateField(verbose_name='Fecha de Vencimiento')
    paid_date = models.DateField(blank=True, null=True, verbose_name='Fecha de Pago')
    
    # Montos
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Valor')
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Valor Pagado')
    
    # Estado y método
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Estado')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True, verbose_name='Método de Pago')
    
    # Seguimiento
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Recibido por')
    receipt_number = models.CharField(max_length=50, blank=True, verbose_name='Número de Recibo')
    notes = models.TextField(blank=True, verbose_name='Observaciones')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.student.full_name} - {self.concept.name} - ${self.amount:,.0f}"
    
    @property
    def balance(self):
        """Saldo pendiente"""
        return self.amount - self.paid_amount
    
    @property
    def is_overdue(self):
        """Verificar si está vencido"""
        return self.due_date < timezone.now().date() and self.status in ['pending', 'partial']
    
    def save(self, *args, **kwargs):
        # Actualizar estado automáticamente
        if self.paid_amount >= self.amount:
            self.status = 'paid'
        elif self.paid_amount > 0:
            self.status = 'partial'
        elif self.is_overdue:
            self.status = 'overdue'
        
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
        ordering = ['-due_date', 'student__last_name']


class SchoolCalendar(models.Model):
    """Calendario escolar"""
    EVENT_TYPE_CHOICES = [
        ('holiday', 'Festivo'),
        ('vacation', 'Vacaciones'),
        ('exam_period', 'Período de Exámenes'),
        ('enrollment', 'Matrícula'),
        ('graduation', 'Graduación'),
        ('meeting', 'Reunión'),
        ('activity', 'Actividad Especial'),
        ('no_classes', 'Sin Clases'),
    ]
    
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='calendar_events')
    title = models.CharField(max_length=200, verbose_name='Título')
    description = models.TextField(blank=True, verbose_name='Descripción')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES, verbose_name='Tipo de Evento')
    
    start_date = models.DateField(verbose_name='Fecha de Inicio')
    end_date = models.DateField(verbose_name='Fecha de Fin')
    
    affects_all_grades = models.BooleanField(default=True, verbose_name='Afecta a Todos los Grados')
    specific_grades = models.ManyToManyField('academics.Grade', blank=True, verbose_name='Grados Específicos')
    
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Creado por')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} ({self.start_date} - {self.end_date})"
    
    @property
    def duration_days(self):
        """Duración en días"""
        return (self.end_date - self.start_date).days + 1
    
    class Meta:
        verbose_name = 'Evento del Calendario'
        verbose_name_plural = 'Eventos del Calendario'
        ordering = ['start_date', 'title']


class StudentDocument(models.Model):
    """Documentos de estudiantes"""
    DOCUMENT_TYPE_CHOICES = [
        ('birth_certificate', 'Certificado de Nacimiento'),
        ('vaccination_card', 'Carnet de Vacunas'),
        ('medical_certificate', 'Certificado Médico'),
        ('academic_transcript', 'Certificado de Notas'),
        ('photo', 'Fotografía'),
        ('id_copy', 'Copia de Documento'),
        ('guardian_id', 'Documento del Acudiente'),
        ('other', 'Otro'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='documents', verbose_name='Estudiante')
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPE_CHOICES, verbose_name='Tipo de Documento')
    title = models.CharField(max_length=200, verbose_name='Título')
    file = models.FileField(upload_to='student_documents/', verbose_name='Archivo')
    
    # Información adicional
    description = models.TextField(blank=True, verbose_name='Descripción')
    expiry_date = models.DateField(blank=True, null=True, verbose_name='Fecha de Vencimiento')
    is_required = models.BooleanField(default=False, verbose_name='Documento Requerido')
    is_verified = models.BooleanField(default=False, verbose_name='Verificado')
    
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Subido por')
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_documents', verbose_name='Verificado por')
    
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(blank=True, null=True, verbose_name='Fecha de Verificación')
    
    def __str__(self):
        return f"{self.student.full_name} - {self.get_document_type_display()}"
    
    @property
    def is_expired(self):
        """Verificar si el documento está vencido"""
        return self.expiry_date and self.expiry_date < timezone.now().date()
    
    class Meta:
        verbose_name = 'Documento de Estudiante'
        verbose_name_plural = 'Documentos de Estudiantes'
        ordering = ['student__last_name', 'document_type']


class AcademicReport(models.Model):
    """Reportes académicos generados"""
    REPORT_TYPE_CHOICES = [
        ('bulletin', 'Boletín Individual'),
        ('course_summary', 'Resumen de Curso'),
        ('attendance_report', 'Reporte de Asistencia'),
        ('grade_analysis', 'Análisis de Rendimiento'),
        ('enrollment_list', 'Lista de Matrícula'),
        ('payment_report', 'Reporte de Pagos'),
        ('behavioral_report', 'Reporte de Comportamiento'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='Título')
    report_type = models.CharField(max_length=30, choices=REPORT_TYPE_CHOICES, verbose_name='Tipo de Reporte')
    description = models.TextField(blank=True, verbose_name='Descripción')
    
    # Referencias opcionales
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Estudiante')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Curso')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Año Académico')
    
    # Archivo y metadatos
    file_path = models.FileField(upload_to='reports/', verbose_name='Archivo')
    parameters = models.JSONField(default=dict, verbose_name='Parámetros del Reporte')
    
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Generado por')
    generated_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Generación')
    
    def __str__(self):
        return f"{self.title} - {self.get_report_type_display()}"
    
    class Meta:
        verbose_name = 'Reporte Académico'
        verbose_name_plural = 'Reportes Académicos'
        ordering = ['-generated_at']
