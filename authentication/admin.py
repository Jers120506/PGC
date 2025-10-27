from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserProfile, PasswordResetRequest

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    fk_name = 'user'  # Especificar que ForeignKey usar
    can_delete = False
    verbose_name_plural = 'Perfil'

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role', 'is_staff')
    list_filter = BaseUserAdmin.list_filter + ('profile__role',)
    
    def get_role(self, obj):
        return obj.profile.get_role_display() if hasattr(obj, 'profile') else 'Sin perfil'
    get_role.short_description = 'Rol'

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'is_staff_member', 'phone', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone', 'employee_id')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('user', 'role')
        }),
        ('Información del Personal', {
            'fields': ('employee_id', 'department', 'hire_date', 'is_active_employee'),
            'classes': ('collapse',)
        }),
        ('Permisos Específicos', {
            'fields': ('can_manage_grades', 'can_manage_attendance', 'can_manage_payments', 'can_generate_reports'),
            'classes': ('collapse',)
        }),
        ('Información de Contacto', {
            'fields': ('phone', 'bio', 'avatar'),
            'classes': ('collapse',)
        }),
        ('Relaciones', {
            'fields': ('teacher',),
            'classes': ('collapse',)
        }),
    )

@admin.register(PasswordResetRequest)
class PasswordResetRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'requested_by', 'status', 'days_pending', 'created_at', 'resolved_by')
    list_filter = ('status', 'created_at', 'resolved_at')
    search_fields = ('user__first_name', 'user__last_name', 'user__username', 'reason')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Solicitud', {
            'fields': ('user', 'requested_by', 'reason', 'status')
        }),
        ('Resolución', {
            'fields': ('resolved_by', 'resolved_at', 'resolution_notes', 'temporary_password')
        }),
    )
    
    readonly_fields = ('created_at', 'days_pending')
