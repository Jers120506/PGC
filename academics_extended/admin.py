from django.contrib import admin
from .models import (
    AcademicYear, Grade, Subject, Course, SubjectAssignment,
    Student
    # GradeRecord, Attendance - TEMPORALMENTE DESHABILITADO
)


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'is_current']
    list_filter = ['is_current']
    ordering = ['-start_date']
    
    def save_model(self, request, obj, form, change):
        # Si se marca como año actual, desmarcar los demás
        if obj.is_current:
            AcademicYear.objects.filter(is_current=True).update(is_current=False)
        super().save_model(request, obj, form, change)


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['name', 'level', 'order']
    list_filter = ['level']
    ordering = ['order']


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'area', 'hours_per_week']
    list_filter = ['area']
    search_fields = ['name', 'code']
    ordering = ['area', 'name']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'homeroom_teacher', 'current_students_count', 'max_students', 'available_spots']
    list_filter = ['academic_year', 'grade__level', 'section']
    search_fields = ['grade__name']
    ordering = ['academic_year', 'grade__order', 'section']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('grade', 'academic_year', 'homeroom_teacher')


@admin.register(SubjectAssignment)
class SubjectAssignmentAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'subject', 'course', 'academic_year']
    list_filter = ['academic_year', 'subject__area', 'course__grade__level']
    search_fields = ['teacher__first_name', 'teacher__last_name', 'subject__name', 'course__grade__name']
    ordering = ['academic_year', 'course', 'subject']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'teacher', 'subject', 'course__grade', 'academic_year'
        )


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = [
        'student_id', 'get_full_name', 'course', 'status', 
        'guardian_name', 'guardian_phone', 'enrollment_date'
    ]
    list_filter = ['status', 'course__grade__level', 'course__academic_year', 'enrollment_date']
    search_fields = [
        'student_id', 'user__first_name', 'user__last_name', 
        'guardian_name', 'guardian_phone'
    ]
    ordering = ['user__last_name', 'user__first_name']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('user', 'student_id', 'course', 'enrollment_date', 'status')
        }),
        ('Información del Acudiente', {
            'fields': ('guardian_name', 'guardian_phone', 'guardian_email', 'guardian_relationship')
        }),
        ('Información Personal', {
            'fields': ('birth_date', 'birth_place', 'address', 'medical_info')
        }),
    )
    
    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_full_name.short_description = 'Nombre Completo'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'course__grade', 'course__academic_year')


# @admin.register(GradeRecord)
# class GradeRecordAdmin(admin.ModelAdmin):
#     """TEMPORALMENTE DESHABILITADO"""
#     pass


# @admin.register(Attendance)
# class AttendanceAdmin(admin.ModelAdmin):
#     """TEMPORALMENTE DESHABILITADO"""
#     pass
