from django.contrib import admin
from .models import (
    Enrollment, PaymentConcept, Payment, SchoolCalendar,
    StudentDocument, AcademicReport
)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'academic_year', 'status', 'enrollment_date', 'enrolled_by')
    list_filter = ('academic_year', 'status', 'enrollment_date')
    search_fields = ('student__user__first_name', 'student__user__last_name', 'student__student_id')
    ordering = ('-enrollment_date', 'student__user__last_name')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('student', 'academic_year', 'course', 'status')
        }),
        ('Fechas', {
            'fields': ('enrollment_date', 'enrolled_by')
        }),
        ('Información Financiera', {
            'fields': ('enrollment_fee', 'monthly_fee')
        }),
        ('Observaciones', {
            'fields': ('notes',)
        }),
    )


@admin.register(PaymentConcept)
class PaymentConceptAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'default_amount', 'is_active')
    list_filter = ('type', 'is_active')
    search_fields = ('name',)
    ordering = ('type', 'name')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('student', 'concept', 'amount', 'paid_amount', 'balance', 'due_date', 'status', 'is_overdue')
    list_filter = ('status', 'concept', 'due_date', 'payment_method')
    search_fields = ('student__user__first_name', 'student__user__last_name', 'student__student_id')
    ordering = ('-due_date', 'student__user__last_name')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('student', 'concept', 'due_date')
        }),
        ('Montos', {
            'fields': ('amount', 'paid_amount', 'status')
        }),
        ('Pago', {
            'fields': ('paid_date', 'payment_method', 'received_by', 'receipt_number')
        }),
        ('Observaciones', {
            'fields': ('notes',)
        }),
    )


@admin.register(SchoolCalendar)
class SchoolCalendarAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_type', 'start_date', 'end_date', 'duration_days', 'affects_all_grades', 'is_active')
    list_filter = ('event_type', 'start_date', 'affects_all_grades', 'is_active')
    search_fields = ('title', 'description')
    ordering = ('start_date', 'title')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('title', 'description', 'event_type', 'is_active')
        }),
        ('Fechas', {
            'fields': ('start_date', 'end_date')
        }),
        ('Audiencia', {
            'fields': ('affects_all_grades', 'specific_grades')
        }),
        ('Metadatos', {
            'fields': ('created_by',)
        }),
    )


@admin.register(StudentDocument)
class StudentDocumentAdmin(admin.ModelAdmin):
    list_display = ('student', 'document_type', 'title', 'is_required', 'is_verified', 'is_expired', 'uploaded_by')
    list_filter = ('document_type', 'is_required', 'is_verified', 'expiry_date')
    search_fields = ('student__user__first_name', 'student__user__last_name', 'title')
    ordering = ('student__user__last_name', 'document_type')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('student', 'document_type', 'title', 'file')
        }),
        ('Estado', {
            'fields': ('is_required', 'is_verified', 'expiry_date')
        }),
        ('Metadatos', {
            'fields': ('description', 'uploaded_by', 'verified_by', 'verified_at')
        }),
    )


@admin.register(AcademicReport)
class AcademicReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'report_type', 'student', 'course', 'academic_year', 'generated_by', 'generated_at')
    list_filter = ('report_type', 'generated_at', 'academic_year')
    search_fields = ('title', 'student__user__first_name', 'student__user__last_name')
    ordering = ('-generated_at', 'title')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('title', 'report_type', 'description')
        }),
        ('Referencias', {
            'fields': ('student', 'course', 'academic_year')
        }),
        ('Archivo', {
            'fields': ('file_path', 'parameters')
        }),
        ('Metadatos', {
            'fields': ('generated_by',)
        }),
    )
