from django.contrib import admin
from .models import (
    AcademicYear, AcademicPeriod, Grade, Subject, Course,
    SubjectAssignment, Student, GradeRecord, Attendance, BehaviorRecord
)


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_current')
    list_filter = ('is_current',)
    ordering = ('-start_date',)


@admin.register(AcademicPeriod)
class AcademicPeriodAdmin(admin.ModelAdmin):
    list_display = ('academic_year', 'get_number_display', 'start_date', 'end_date', 'is_current')
    list_filter = ('academic_year', 'number', 'is_current')
    ordering = ('academic_year', 'number')


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'numeric_grade', 'order', 'is_active')
    list_filter = ('level', 'is_active')
    ordering = ('order',)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'area', 'hours_per_week', 'is_active')
    list_filter = ('area', 'is_active')
    search_fields = ('name', 'code')
    ordering = ('area', 'name')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('grade', 'section', 'academic_year', 'homeroom_teacher', 'current_students_count', 'max_students', 'is_active')
    list_filter = ('academic_year', 'grade', 'section', 'is_active')
    search_fields = ('grade__name',)
    ordering = ('academic_year', 'grade__order', 'section')


@admin.register(SubjectAssignment)
class SubjectAssignmentAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'subject', 'course', 'academic_year', 'is_active')
    list_filter = ('academic_year', 'subject', 'is_active')
    search_fields = ('teacher__first_name', 'teacher__last_name', 'subject__name')
    ordering = ('academic_year', 'course', 'subject')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'full_name', 'course', 'age', 'enrollment_date', 'status')
    list_filter = ('course', 'gender', 'status', 'enrollment_date')
    search_fields = ('student_id', 'first_name', 'last_name', 'identification_number')
    ordering = ('last_name', 'first_name')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('student_id', 'first_name', 'last_name', 'identification_number', 'course', 'status')
        }),
        ('Información Personal', {
            'fields': ('birth_date', 'gender', 'phone', 'address')
        }),
        ('Información del Acudiente', {
            'fields': ('guardian_name', 'guardian_relationship', 'guardian_phone', 'guardian_email')
        }),
        ('Información Médica', {
            'fields': ('medical_info', 'allergies')
        }),
        ('Matrícula', {
            'fields': ('enrollment_date', 'notes')
        }),
    )


@admin.register(GradeRecord)
class GradeRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'activity_name', 'grade_value', 'grade_text', 'period', 'date_recorded', 'teacher')
    list_filter = ('period', 'subject', 'activity_type', 'date_recorded')
    search_fields = ('student__user__first_name', 'student__user__last_name', 'activity_name')
    ordering = ('-date_recorded', 'student__user__last_name')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('student', 'subject', 'teacher', 'period')
        }),
        ('Actividad', {
            'fields': ('activity_name', 'activity_type', 'date_recorded')
        }),
        ('Calificación', {
            'fields': ('grade_value', 'observations')
        }),
    )


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'subject', 'status', 'arrival_time', 'teacher')
    list_filter = ('date', 'status', 'subject')
    search_fields = ('student__user__first_name', 'student__user__last_name')
    ordering = ('-date', 'student__user__last_name')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('student', 'date', 'subject', 'teacher')
        }),
        ('Asistencia', {
            'fields': ('status', 'arrival_time', 'departure_time')
        }),
        ('Observaciones', {
            'fields': ('justification', 'notes')
        }),
    )


@admin.register(BehaviorRecord)
class BehaviorRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'type', 'category', 'teacher', 'requires_followup', 'parent_notified')
    list_filter = ('date', 'type', 'category', 'requires_followup', 'parent_notified')
    search_fields = ('student__user__first_name', 'student__user__last_name', 'description')
    ordering = ('-date', 'student__user__last_name')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('student', 'teacher', 'date')
        }),
        ('Comportamiento', {
            'fields': ('type', 'category', 'description', 'action_taken')
        }),
        ('Seguimiento', {
            'fields': ('requires_followup', 'parent_notified', 'notification_date')
        }),
    )
