from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class AcademicYear(models.Model):
    """Año académico"""
    name = models.CharField(max_length=20, verbose_name="Año Académico")  # ej: "2025"
    start_date = models.DateField(verbose_name="Fecha de Inicio")
    end_date = models.DateField(verbose_name="Fecha de Fin")
    is_current = models.BooleanField(default=False, verbose_name="Año Actual")
    
    class Meta:
        verbose_name = "Año Académico"
        verbose_name_plural = "Años Académicos"
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.name} ({'Actual' if self.is_current else 'Inactivo'})"


class Grade(models.Model):
    """Grados escolares"""
    LEVEL_CHOICES = [
        ('primaria', 'Primaria'),
        ('bachillerato', 'Bachillerato'),
    ]
    
    name = models.CharField(max_length=20, verbose_name="Nombre del Grado")  # ej: "5° Primaria", "9° Bachillerato"
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, verbose_name="Nivel")
    order = models.PositiveIntegerField(verbose_name="Orden", help_text="Para ordenar los grados")
    
    class Meta:
        verbose_name = "Grado"
        verbose_name_plural = "Grados"
        ordering = ['order']
    
    def __str__(self):
        return f"{self.name} - {self.get_level_display()}"


class Subject(models.Model):
    """Materias/Asignaturas"""
    AREA_CHOICES = [
        ('matematicas', 'Matemáticas'),
        ('ciencias', 'Ciencias Naturales'),
        ('sociales', 'Ciencias Sociales'),
        ('lenguaje', 'Lenguaje y Literatura'),
        ('ingles', 'Inglés'),
        ('educacion_fisica', 'Educación Física'),
        ('artes', 'Artes'),
        ('informatica', 'Informática'),
        ('religion', 'Religión'),
        ('etica', 'Ética y Valores'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Nombre de la Materia")
    code = models.CharField(max_length=10, unique=True, verbose_name="Código")
    area = models.CharField(max_length=50, choices=AREA_CHOICES, verbose_name="Área")
    hours_per_week = models.PositiveIntegerField(verbose_name="Horas por Semana")
    description = models.TextField(blank=True, verbose_name="Descripción")
    
    class Meta:
        verbose_name = "Materia"
        verbose_name_plural = "Materias"
        ordering = ['area', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class GradeSubjectAssignment(models.Model):
    """Asignación de materias a grados escolares"""
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, verbose_name="Grado")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name="Materia")
    hours_per_week = models.PositiveIntegerField(
        verbose_name="Horas por Semana",
        help_text="Horas semanales para esta materia en este grado"
    )
    is_mandatory = models.BooleanField(default=True, verbose_name="Es Obligatoria")
    semester = models.CharField(
        max_length=20,
        choices=[
            ('anual', 'Anual'),
            ('primer_semestre', 'Primer Semestre'),
            ('segundo_semestre', 'Segundo Semestre'),
        ],
        default='anual',
        verbose_name="Período"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Asignación de Materia a Grado"
        verbose_name_plural = "Asignaciones de Materias a Grados"
        unique_together = ['grade', 'subject', 'semester']
        ordering = ['grade__order', 'subject__area', 'subject__name']
    
    def __str__(self):
        return f"{self.grade.name} - {self.subject.name} ({self.hours_per_week}h/sem)"


class Course(models.Model):
    """Cursos específicos (combinación de grado + sección)"""
    SECTION_CHOICES = [
        ('A', 'Sección A'),
        ('B', 'Sección B'),
        ('C', 'Sección C'),
        ('D', 'Sección D'),
    ]
    
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, verbose_name="Grado")
    section = models.CharField(max_length=5, choices=SECTION_CHOICES, verbose_name="Sección")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, verbose_name="Año Académico")
    homeroom_teacher = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        limit_choices_to={'profile__role': 'teacher'},
        verbose_name="Profesor Director de Grupo"
    )
    max_students = models.PositiveIntegerField(default=35, verbose_name="Máximo de Estudiantes")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    
    class Meta:
        verbose_name = "Curso"
        verbose_name_plural = "Cursos"
        unique_together = ['grade', 'section', 'academic_year']
        ordering = ['academic_year', 'grade__order', 'section']
    
    def __str__(self):
        return f"{self.grade.name} - {self.section} ({self.academic_year.name})"
    
    @property
    def current_students_count(self):
        """Número actual de estudiantes en el curso"""
        return self.students.count()
    
    @property
    def available_spots(self):
        """Cupos disponibles en el curso"""
        return self.max_students - self.current_students_count


class SubjectAssignment(models.Model):
    """Asignación de docentes a materias por curso"""
    teacher = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        limit_choices_to={'profile__role': 'teacher'},
        related_name='subject_assignments_extended',
        verbose_name="Profesor"
    )
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name="Materia")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="Curso")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, verbose_name="Año Académico")
    
    class Meta:
        verbose_name = "Asignación de Materia"
        verbose_name_plural = "Asignaciones de Materias"
        unique_together = ['teacher', 'subject', 'course', 'academic_year']
        ordering = ['academic_year', 'course', 'subject']
    
    def __str__(self):
        return f"{self.teacher.get_full_name()} - {self.subject.name} - {self.course}"


class Student(models.Model):
    """Perfil estudiantil extendido"""
    STATUS_CHOICES = [
        ('active', 'Activo'),
        ('inactive', 'Inactivo'),
        ('transferred', 'Trasladado'),
        ('graduated', 'Graduado'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Usuario")
    student_id = models.CharField(max_length=20, unique=True, verbose_name="ID de Estudiante")
    course = models.ForeignKey(
        Course, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='students',
        verbose_name="Curso"
    )
    enrollment_date = models.DateField(verbose_name="Fecha de Matrícula")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Estado")
    
    # Información del acudiente
    guardian_name = models.CharField(max_length=200, verbose_name="Nombre del Acudiente")
    guardian_phone = models.CharField(max_length=20, verbose_name="Teléfono del Acudiente")
    guardian_email = models.EmailField(blank=True, verbose_name="Email del Acudiente")
    guardian_relationship = models.CharField(max_length=50, default="Padre/Madre", verbose_name="Parentesco")
    
    # Información personal
    address = models.TextField(verbose_name="Dirección")
    birth_date = models.DateField(verbose_name="Fecha de Nacimiento")
    birth_place = models.CharField(max_length=100, blank=True, verbose_name="Lugar de Nacimiento")
    medical_info = models.TextField(blank=True, verbose_name="Información Médica")
    
    class Meta:
        verbose_name = "Estudiante"
        verbose_name_plural = "Estudiantes"
        ordering = ['user__last_name', 'user__first_name']
    
    def __str__(self):
        return f"{self.student_id} - {self.user.get_full_name()}"
    
    @property
    def age(self):
        """Calcular edad del estudiante"""
        from datetime import date
        today = date.today()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))


# class GradeRecord(models.Model):
#     """Registro de calificaciones - TEMPORALMENTE DESHABILITADO"""
#     pass


# class Attendance(models.Model):
#     """Control de asistencia - TEMPORALMENTE DESHABILITADO"""
#     pass


class Classroom(models.Model):
    """Aulas/Salones del colegio"""
    name = models.CharField(max_length=50, verbose_name="Nombre del Salón")
    code = models.CharField(max_length=20, unique=True, verbose_name="Código")
    capacity = models.PositiveIntegerField(verbose_name="Capacidad")
    building = models.CharField(max_length=50, blank=True, verbose_name="Edificio")
    floor = models.CharField(max_length=20, blank=True, verbose_name="Piso")
    equipment = models.TextField(blank=True, verbose_name="Equipamiento")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    
    class Meta:
        verbose_name = "Salón"
        verbose_name_plural = "Salones"
        ordering = ['building', 'floor', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class TimeSlot(models.Model):
    """Franjas horarias"""
    name = models.CharField(max_length=50, verbose_name="Nombre")
    start_time = models.TimeField(verbose_name="Hora de Inicio")
    end_time = models.TimeField(verbose_name="Hora de Fin")
    order = models.PositiveIntegerField(verbose_name="Orden")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    
    class Meta:
        verbose_name = "Franja Horaria"
        verbose_name_plural = "Franjas Horarias"
        ordering = ['order', 'start_time']
    
    def __str__(self):
        return f"{self.name}: {self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"


class Schedule(models.Model):
    """Horario de clases"""
    WEEKDAY_CHOICES = [
        (1, 'Lunes'),
        (2, 'Martes'), 
        (3, 'Miércoles'),
        (4, 'Jueves'),
        (5, 'Viernes'),
    ]
    
    # Relaciones principales
    course = models.ForeignKey(
        Course, 
        on_delete=models.CASCADE, 
        verbose_name='Curso',
        related_name='schedules'
    )
    subject = models.ForeignKey(
        Subject, 
        on_delete=models.CASCADE, 
        verbose_name='Materia'
    )
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'profile__role': 'teacher'},
        verbose_name='Profesor'
    )
    classroom = models.ForeignKey(
        Classroom, 
        on_delete=models.CASCADE, 
        verbose_name='Salón'
    )
    time_slot = models.ForeignKey(
        TimeSlot, 
        on_delete=models.CASCADE, 
        verbose_name='Franja Horaria'
    )
    
    # Información temporal
    weekday = models.PositiveIntegerField(
        choices=WEEKDAY_CHOICES,
        verbose_name='Día de la Semana'
    )
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        verbose_name='Año Académico'
    )
    
    # Metadatos
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    notes = models.TextField(blank=True, verbose_name='Notas')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='schedules_created',
        verbose_name='Creado por'
    )
    
    class Meta:
        verbose_name = "Horario"
        verbose_name_plural = "Horarios"
        unique_together = [
            ['course', 'time_slot', 'weekday', 'academic_year'],  # Un curso no puede tener dos materias al mismo tiempo
            ['teacher', 'time_slot', 'weekday', 'academic_year'],  # Un profesor no puede estar en dos lugares al mismo tiempo
            ['classroom', 'time_slot', 'weekday', 'academic_year'],  # Un salón no puede tener dos clases al mismo tiempo
        ]
        ordering = ['weekday', 'time_slot__order']
    
    def __str__(self):
        weekday_name = dict(self.WEEKDAY_CHOICES)[self.weekday]
        return f"{weekday_name} {self.time_slot.name} - {self.course} - {self.subject.name}"
    
    def get_weekday_display_full(self):
        """Obtener nombre completo del día"""
        return dict(self.WEEKDAY_CHOICES)[self.weekday]
    
    @property
    def schedule_summary(self):
        """Resumen del horario para mostrar en interfaces"""
        return {
            'day': self.get_weekday_display_full(),
            'time': f"{self.time_slot.start_time.strftime('%H:%M')} - {self.time_slot.end_time.strftime('%H:%M')}",
            'subject': self.subject.name,
            'teacher': self.teacher.get_full_name(),
            'classroom': self.classroom.name,
            'course': str(self.course)
        }


# class EvaluationCriteria(models.Model):
#     """Criterios de evaluación por materia y período - TEMPORALMENTE DESHABILITADO"""
#     pass


# class GradingScale(models.Model):
#     """Escala de calificaciones institucional - TEMPORALMENTE DESHABILITADO"""
#     pass


# class StudentGradeSummary(models.Model):
#     """Resumen de calificaciones por estudiante, materia y período - TEMPORALMENTE DESHABILITADO"""
#     pass


# class AttendanceRecord(models.Model):
#     """Registro de asistencia - TEMPORALMENTE DESHABILITADO"""
#     pass


# === SISTEMA DE HORARIOS (GESTIONADO POR SECRETARIOS) ===

class TeacherSubjectAssignment(models.Model):
    """Asignación de profesores a materias y cursos"""
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'profile__role': 'teacher'},
        verbose_name='Profesor'
    )
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name='Materia')
    courses = models.ManyToManyField(Course, verbose_name='Cursos Asignados')
    
    is_main_teacher = models.BooleanField(default=False, verbose_name='Profesor Principal')  # Director de curso
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        verbose_name='Año Académico'
    )
    
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='teacher_assignments_made',
        limit_choices_to={'profile__role__in': ['admin', 'secretary']},
        verbose_name='Asignado por'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Asignación de Profesor'
        verbose_name_plural = 'Asignaciones de Profesores'
        unique_together = ['teacher', 'subject', 'academic_year']
    
    def __str__(self):
        courses_list = ", ".join([str(course) for course in self.courses.all()[:3]])
        if self.courses.count() > 3:
            courses_list += f" y {self.courses.count() - 3} más"
        return f"{self.teacher.get_full_name()} - {self.subject.name} ({courses_list})"
