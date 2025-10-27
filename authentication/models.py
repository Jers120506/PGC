from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class PasswordResetRequest(models.Model):
    """Solicitudes de recuperación de contraseña (manual por administrador)"""
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('approved', 'Aprobado'),
        ('rejected', 'Rechazado'),
        ('completed', 'Completado'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_requests', verbose_name='Usuario')
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_resets_requested', verbose_name='Solicitado por')
    reason = models.TextField(verbose_name='Motivo de la Solicitud')
    
    # Control del proceso
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Estado')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Solicitud')
    
    # Resolución
    resolved_at = models.DateTimeField(blank=True, null=True, verbose_name='Fecha de Resolución')
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='password_resets_resolved', verbose_name='Resuelto por')
    resolution_notes = models.TextField(blank=True, verbose_name='Notas de Resolución')
    
    # Nueva contraseña temporal (se puede generar automáticamente)
    temporary_password = models.CharField(max_length=20, blank=True, verbose_name='Contraseña Temporal')
    
    def __str__(self):
        return f"Solicitud de {self.user.get_full_name()} - {self.get_status_display()}"
    
    @property
    def is_pending(self):
        return self.status == 'pending'
    
    @property
    def days_pending(self):
        """Días transcurridos desde la solicitud"""
        from django.utils import timezone
        return (timezone.now() - self.created_at).days
    
    class Meta:
        verbose_name = 'Solicitud de Recuperación de Contraseña'
        verbose_name_plural = 'Solicitudes de Recuperación de Contraseña'
        ordering = ['-created_at']


class UserProfile(models.Model):
    """
    Perfil extendido del usuario para manejar roles y información adicional
    """
    ROLE_CHOICES = [
        ('student', 'Estudiante'),
        ('teacher', 'Profesor'),
        ('admin', 'Administrador'),
        ('secretary', 'Secretaría'),  # NUEVO ROL AGREGADO
    ]
    
    EDUCATION_LEVEL_CHOICES = [
        ('bachillerato', 'Bachillerato'),
        ('tecnico', 'Técnico'),
        ('tecnologo', 'Tecnólogo'),
        ('profesional', 'Profesional'),
        ('especialista', 'Especialista'),
        ('magister', 'Magíster'),
        ('doctorado', 'Doctorado'),
    ]
    
    GENDER_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
        ('N', 'Prefiero no decir'),
    ]
    
    # Relación básica
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                               related_name='assigned_students', 
                               limit_choices_to={'profile__role': 'teacher'},
                               help_text='Profesor asignado (solo para estudiantes)')
    
    # Información personal básica
    phone = models.CharField(max_length=15, blank=True, null=True, verbose_name='Teléfono')
    mobile_phone = models.CharField(max_length=15, blank=True, null=True, verbose_name='Celular')
    bio = models.TextField(max_length=500, blank=True, verbose_name='Biografía')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Foto de Perfil')
    
    # Información personal extendida
    date_of_birth = models.DateField(blank=True, null=True, verbose_name='Fecha de Nacimiento')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, verbose_name='Género')
    identification_number = models.CharField(max_length=20, blank=True, unique=True, null=True, verbose_name='Número de Identificación')
    address = models.TextField(max_length=200, blank=True, verbose_name='Dirección')
    city = models.CharField(max_length=50, blank=True, verbose_name='Ciudad')
    emergency_contact_name = models.CharField(max_length=100, blank=True, verbose_name='Contacto de Emergencia')
    emergency_contact_phone = models.CharField(max_length=15, blank=True, verbose_name='Teléfono de Emergencia')
    
    # Información académica/profesional
    education_level = models.CharField(max_length=20, choices=EDUCATION_LEVEL_CHOICES, blank=True, verbose_name='Nivel Educativo')
    institution = models.CharField(max_length=100, blank=True, verbose_name='Institución de Estudios')
    graduation_year = models.PositiveIntegerField(blank=True, null=True, verbose_name='Año de Graduación')
    professional_title = models.CharField(max_length=100, blank=True, verbose_name='Título Profesional')
    specialization = models.CharField(max_length=100, blank=True, verbose_name='Especialización')
    years_of_experience = models.PositiveIntegerField(blank=True, null=True, verbose_name='Años de Experiencia')
    
    # Información laboral específica
    department = models.CharField(max_length=50, blank=True, verbose_name='Departamento')
    position = models.CharField(max_length=50, blank=True, verbose_name='Cargo')
    hire_date = models.DateField(blank=True, null=True, verbose_name='Fecha de Contratación')
    work_schedule = models.CharField(max_length=100, blank=True, verbose_name='Horario de Trabajo')
    
    # Para estudiantes - información familiar
    parent_guardian_name = models.CharField(max_length=100, blank=True, verbose_name='Nombre del Padre/Tutor')
    parent_guardian_phone = models.CharField(max_length=15, blank=True, verbose_name='Teléfono del Padre/Tutor')
    parent_guardian_email = models.EmailField(blank=True, verbose_name='Email del Padre/Tutor')
    
    # Configuraciones del sistema
    notifications_enabled = models.BooleanField(default=True, verbose_name='Notificaciones Activadas')
    email_notifications = models.BooleanField(default=True, verbose_name='Notificaciones por Email')
    language_preference = models.CharField(max_length=10, default='es', verbose_name='Idioma Preferido')
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_profile_complete = models.BooleanField(default=False, verbose_name='Perfil Completo')
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
    
    @property
    def age(self):
        """Calcular edad basada en fecha de nacimiento"""
        if self.date_of_birth:
            from datetime import date
            today = date.today()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None
    
    @property
    def full_name(self):
        """Nombre completo del usuario"""
        return f"{self.user.first_name} {self.user.last_name}".strip()
    
    @property
    def profile_completion_percentage(self):
        """Calcular porcentaje de completitud del perfil"""
        total_fields = 20  # Campos importantes a completar
        completed_fields = 0
        
        # Campos básicos
        if self.user.first_name: completed_fields += 1
        if self.user.last_name: completed_fields += 1
        if self.user.email: completed_fields += 1
        if self.phone: completed_fields += 1
        if self.bio: completed_fields += 1
        if self.avatar: completed_fields += 1
        
        # Información personal
        if self.date_of_birth: completed_fields += 1
        if self.gender: completed_fields += 1
        if self.identification_number: completed_fields += 1
        if self.address: completed_fields += 1
        if self.city: completed_fields += 1
        if self.emergency_contact_name: completed_fields += 1
        if self.emergency_contact_phone: completed_fields += 1
        
        # Información académica/profesional
        if self.education_level: completed_fields += 1
        if self.institution: completed_fields += 1
        if self.professional_title: completed_fields += 1
        
        # Información laboral
        if self.department: completed_fields += 1
        if self.position: completed_fields += 1
        if self.hire_date: completed_fields += 1
        if self.work_schedule: completed_fields += 1
        
        return round((completed_fields / total_fields) * 100, 1)
    
    @property
    def is_student(self):
        return self.role == 'student'
    
    @property
    def is_teacher(self):
        return self.role == 'teacher'
    
    @property
    def is_admin(self):
        return self.role == 'admin' or self.user.is_superuser
    
    @property
    def is_secretary(self):
        """Nuevo método para verificar si es secretaría"""
        return self.role == 'secretary'
    
    @property
    def is_staff_member(self):
        """Verificar si es personal del colegio (no estudiante)"""
        return self.role in ['admin', 'teacher', 'secretary']
    
    def get_assigned_students(self):
        """Obtener estudiantes asignados a este profesor"""
        if self.is_teacher:
            return User.objects.filter(profile__teacher=self.user, profile__role='student')
        return User.objects.none()
    
    def get_assigned_teacher(self):
        """Obtener el profesor asignado a este estudiante"""
        if self.is_student and self.teacher:
            return self.teacher
        return None
    
    def mark_profile_complete(self):
        """Marcar perfil como completo si cumple criterios mínimos"""
        completion = self.profile_completion_percentage
        self.is_profile_complete = completion >= 70  # 70% o más se considera completo
        self.save()
    
    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Crear perfil automáticamente cuando se crea un usuario"""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Guardar perfil cuando se guarda el usuario"""
    if hasattr(instance, 'profile'):
        instance.profile.save()


class UserGroup(models.Model):
    """Modelo para gestionar grupos de usuarios"""
    
    GROUP_TYPES = [
        ('academic', 'Académico'),
        ('departmental', 'Departamental'),
        ('functional', 'Funcional'),
        ('distribution', 'Lista de Distribución'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='Nombre del Grupo')
    description = models.TextField(blank=True, verbose_name='Descripción')
    group_type = models.CharField(max_length=20, choices=GROUP_TYPES, default='functional', verbose_name='Tipo de Grupo')
    
    # Gestión
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_groups', verbose_name='Creado por')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')
    
    # Estado
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    
    # Configuración
    allow_self_join = models.BooleanField(default=False, verbose_name='Permitir Auto-unirse')
    is_public = models.BooleanField(default=True, verbose_name='Visible Públicamente')
    
    def __str__(self):
        return f"{self.name} ({self.get_group_type_display()})"
    
    @property
    def member_count(self):
        """Número total de miembros"""
        return self.memberships.filter(is_active=True).count()
    
    @property
    def leaders_count(self):
        """Número de líderes del grupo"""
        return self.memberships.filter(is_active=True, role='leader').count()
    
    def get_members(self):
        """Obtener todos los miembros activos"""
        return User.objects.filter(
            group_memberships__group=self,
            group_memberships__is_active=True
        ).distinct()
    
    def get_leaders(self):
        """Obtener líderes del grupo"""
        return User.objects.filter(
            group_memberships__group=self,
            group_memberships__is_active=True,
            group_memberships__role='leader'
        ).distinct()
    
    class Meta:
        verbose_name = 'Grupo de Usuarios'
        verbose_name_plural = 'Grupos de Usuarios'
        ordering = ['name']


class GroupMembership(models.Model):
    """Modelo intermedio para la pertenencia a grupos"""
    
    ROLE_CHOICES = [
        ('member', 'Miembro'),
        ('leader', 'Líder'),
        ('moderator', 'Moderador'),
        ('observer', 'Observador'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_memberships', verbose_name='Usuario')
    group = models.ForeignKey(UserGroup, on_delete=models.CASCADE, related_name='memberships', verbose_name='Grupo')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member', verbose_name='Rol en el Grupo')
    
    # Gestión
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Ingreso')
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='added_memberships', verbose_name='Agregado por')
    is_active = models.BooleanField(default=True, verbose_name='Membresía Activa')
    
    # Configuración específica del miembro
    can_invite_others = models.BooleanField(default=False, verbose_name='Puede Invitar Otros')
    notifications_enabled = models.BooleanField(default=True, verbose_name='Notificaciones Habilitadas')
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.group.name} ({self.get_role_display()})"
    
    @property
    def is_leader(self):
        return self.role == 'leader'
    
    @property
    def can_manage_group(self):
        return self.role in ['leader', 'moderator']
    
    class Meta:
        verbose_name = 'Membresía de Grupo'
        verbose_name_plural = 'Membresías de Grupo'
        unique_together = ['user', 'group']  # Un usuario solo puede estar una vez en cada grupo
        ordering = ['-joined_at']


class StudentEnrollment(models.Model):
    """Modelo para gestionar las matrículas de estudiantes por año académico"""
    
    GRADE_CHOICES = [
        # Primaria
        ('preescolar', 'Preescolar'),
        ('primero', 'Primero'),
        ('segundo', 'Segundo'),
        ('tercero', 'Tercero'),
        ('cuarto', 'Cuarto'),
        ('quinto', 'Quinto'),
        
        # Bachillerato
        ('sexto', 'Sexto'),
        ('septimo', 'Séptimo'),
        ('octavo', 'Octavo'),
        ('noveno', 'Noveno'),
        ('decimo', 'Décimo'),
        ('once', 'Once'),
    ]
    
    SECTION_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
    ]
    
    STATUS_CHOICES = [
        ('enrolled', 'Matriculado'),
        ('active', 'Activo'),
        ('inactive', 'Inactivo'),
        ('withdrawn', 'Retirado'),
        ('graduated', 'Graduado'),
        ('transferred', 'Trasladado'),
    ]
    
    # Relaciones básicas
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments', 
                               limit_choices_to={'profile__role': 'student'}, verbose_name='Estudiante')
    academic_year = models.CharField(max_length=4, default='2025', verbose_name='Año Académico')
    
    # Información académica
    grade = models.CharField(max_length=20, choices=GRADE_CHOICES, verbose_name='Grado')
    section = models.CharField(max_length=1, choices=SECTION_CHOICES, default='A', verbose_name='Sección')
    
    # Profesor director de grupo
    homeroom_teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='homeroom_students',
                                       limit_choices_to={'profile__role': 'teacher'},
                                       verbose_name='Profesor Director de Grupo')
    
    # Estado y gestión
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='enrolled', verbose_name='Estado')
    enrollment_date = models.DateField(auto_now_add=True, verbose_name='Fecha de Matrícula')
    
    # Información adicional
    previous_school = models.CharField(max_length=200, blank=True, verbose_name='Colegio Anterior')
    has_special_needs = models.BooleanField(default=False, verbose_name='Necesidades Especiales')
    special_needs_description = models.TextField(blank=True, verbose_name='Descripción Necesidades Especiales')
    
    # Información de contacto específica para la matrícula
    parent_guardian_name = models.CharField(max_length=100, verbose_name='Nombre del Padre/Acudiente')
    parent_guardian_phone = models.CharField(max_length=15, verbose_name='Teléfono del Acudiente')
    parent_guardian_email = models.EmailField(blank=True, verbose_name='Email del Acudiente')
    
    # Gestión administrativa
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='created_enrollments', verbose_name='Creado por')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.get_grade_display()} {self.section} ({self.academic_year})"
    
    @property
    def full_grade(self):
        """Retorna el grado completo con sección (ej: Sexto A)"""
        return f"{self.get_grade_display()} {self.section}"
    
    @property
    def is_active(self):
        return self.status in ['enrolled', 'active']
    
    @property
    def is_primary(self):
        """Determina si el estudiante está en primaria"""
        return self.grade in ['preescolar', 'primero', 'segundo', 'tercero', 'cuarto', 'quinto']
    
    @property
    def is_secondary(self):
        """Determina si el estudiante está en bachillerato"""
        return self.grade in ['sexto', 'septimo', 'octavo', 'noveno', 'decimo', 'once']
    
    def get_academic_group_name(self):
        """Genera el nombre del grupo académico al que debería pertenecer"""
        return f"{self.get_grade_display()} {self.section}"
    
    def assign_to_academic_group(self):
        """Asigna automáticamente al estudiante al grupo académico correspondiente"""
        group_name = self.get_academic_group_name()
        
        try:
            # Buscar el grupo académico correspondiente
            academic_group = UserGroup.objects.get(
                name=group_name,
                group_type='academic'
            )
            
            # Verificar si ya está en el grupo
            existing_membership = GroupMembership.objects.filter(
                user=self.student,
                group=academic_group,
                is_active=True
            ).first()
            
            if not existing_membership:
                # Crear la membresía
                GroupMembership.objects.create(
                    user=self.student,
                    group=academic_group,
                    role='member',
                    added_by=self.created_by or self.student
                )
                return True
            return False
        except UserGroup.DoesNotExist:
            # El grupo no existe, se podría crear automáticamente
            return None
    
    class Meta:
        verbose_name = 'Matrícula de Estudiante'
        verbose_name_plural = 'Matrículas de Estudiantes'
        unique_together = ['student', 'academic_year']  # Un estudiante solo puede tener una matrícula por año
        ordering = ['-academic_year', 'grade', 'section', 'student__last_name']


# Signals para gestión automática
@receiver(post_save, sender=StudentEnrollment)
def auto_assign_to_group(sender, instance, created, **kwargs):
    """Asigna automáticamente al estudiante al grupo académico cuando se crea una matrícula"""
    if created and instance.is_active:
        instance.assign_to_academic_group()
