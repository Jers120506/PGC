from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal


class AcademicYear(models.Model):
    """Año académico escolar"""
    name = models.CharField(max_length=20, verbose_name='Año Académico')  # ej: "2025"
    start_date = models.DateField(verbose_name='Fecha de Inicio')
    end_date = models.DateField(verbose_name='Fecha de Fin')
    is_current = models.BooleanField(default=False, verbose_name='Año Actual')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Solo un año puede ser el actual
        if self.is_current:
            AcademicYear.objects.filter(is_current=True).update(is_current=False)
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Año Académico'
        verbose_name_plural = 'Años Académicos'
        ordering = ['-start_date']


class AcademicPeriod(models.Model):
    """Períodos académicos del año (4 períodos)"""
    PERIOD_CHOICES = [
        ('1', 'Primer Período'),
        ('2', 'Segundo Período'),
        ('3', 'Tercer Período'),
        ('4', 'Cuarto Período'),
    ]
    
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='periods')
    number = models.CharField(max_length=1, choices=PERIOD_CHOICES, verbose_name='Período')
    name = models.CharField(max_length=50, verbose_name='Nombre del Período')
    start_date = models.DateField(verbose_name='Fecha de Inicio')
    end_date = models.DateField(verbose_name='Fecha de Fin')
    is_current = models.BooleanField(default=False, verbose_name='Período Actual')
    
    def __str__(self):
        return f"{self.academic_year.name} - {self.get_number_display()}"
    
    def save(self, *args, **kwargs):
        # Solo un período puede ser el actual por año académico
        if self.is_current:
            AcademicPeriod.objects.filter(
                academic_year=self.academic_year,
                is_current=True
            ).update(is_current=False)
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Período Académico'
        verbose_name_plural = 'Períodos Académicos'
        unique_together = ['academic_year', 'number']
        ordering = ['academic_year', 'number']


class Grade(models.Model):
    """Grados escolares"""
    LEVEL_CHOICES = [
        ('primaria', 'Primaria'),
        ('bachillerato', 'Bachillerato'),
    ]
    
    name = models.CharField(max_length=30, verbose_name='Nombre del Grado')  # ej: "5° Primaria", "9° Bachillerato"
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, verbose_name='Nivel')
    numeric_grade = models.PositiveIntegerField(verbose_name='Grado Numérico')  # 1, 2, 3... 11
    order = models.PositiveIntegerField(verbose_name='Orden', help_text='Para ordenar en listas')
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Grado'
        verbose_name_plural = 'Grados'
        ordering = ['order']


class Subject(models.Model):
    """Materias/Asignaturas"""
    AREA_CHOICES = [
        ('matematicas', 'Matemáticas'),
        ('lenguaje', 'Lenguaje'),
        ('ciencias_naturales', 'Ciencias Naturales'),
        ('ciencias_sociales', 'Ciencias Sociales'),
        ('ingles', 'Inglés'),
        ('educacion_fisica', 'Educación Física'),
        ('educacion_artistica', 'Educación Artística'),
        ('etica', 'Ética y Valores'),
        ('religion', 'Religión'),
        ('tecnologia', 'Tecnología e Informática'),
        ('filosofia', 'Filosofía'),
        ('quimica', 'Química'),
        ('fisica', 'Física'),
        ('biologia', 'Biología'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='Nombre de la Materia')
    code = models.CharField(max_length=10, unique=True, verbose_name='Código')
    area = models.CharField(max_length=30, choices=AREA_CHOICES, verbose_name='Área')
    hours_per_week = models.PositiveIntegerField(verbose_name='Horas por Semana')
    is_active = models.BooleanField(default=True, verbose_name='Activa')
    description = models.TextField(blank=True, verbose_name='Descripción')
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    class Meta:
        verbose_name = 'Materia'
        verbose_name_plural = 'Materias'
        ordering = ['area', 'name']


class Course(models.Model):
    """Cursos específicos (combinación de grado + sección)"""
    SECTION_CHOICES = [
        ('A', 'Sección A'),
        ('B', 'Sección B'),
        ('C', 'Sección C'),
        ('D', 'Sección D'),
    ]
    
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, verbose_name='Grado')
    section = models.CharField(max_length=1, choices=SECTION_CHOICES, verbose_name='Sección')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, verbose_name='Año Académico')
    homeroom_teacher = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='Director de Curso',
        related_name='homeroom_courses'
    )
    max_students = models.PositiveIntegerField(default=20, verbose_name='Máximo de Estudiantes')
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    
    def __str__(self):
        return f"{self.grade.name} - {self.section} ({self.academic_year.name})"
    
    @property
    def current_students_count(self):
        """Número actual de estudiantes matriculados"""
        return self.students.filter(is_active=True).count()
    
    @property
    def available_slots(self):
        """Cupos disponibles"""
        return self.max_students - self.current_students_count
    
    @property
    def full_name(self):
        """Nombre completo del curso"""
        return f"{self.grade.name} {self.section}"
    
    class Meta:
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'
        unique_together = ['grade', 'section', 'academic_year']
        ordering = ['grade__order', 'section']


class SubjectAssignment(models.Model):
    """Asignación de docentes a materias por curso"""
    teacher = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name='Docente',
        limit_choices_to={'profile__role': 'teacher'}
    )
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name='Materia')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='Curso')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, verbose_name='Año Académico')
    is_active = models.BooleanField(default=True, verbose_name='Asignación Activa')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.teacher.get_full_name()} - {self.subject.name} - {self.course}"
    
    class Meta:
        verbose_name = 'Asignación de Materia'
        verbose_name_plural = 'Asignaciones de Materias'
        unique_together = ['teacher', 'subject', 'course', 'academic_year']


class Student(models.Model):
    """
    Modelo simplificado de estudiante - NO es usuario del sistema
    Solo datos gestionados por secretarios y consultados por profesores
    """
    GENDER_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Activo'),
        ('inactive', 'Inactivo'),
        ('graduated', 'Graduado'),
        ('transferred', 'Trasladado'),
    ]
    
    # Información básica
    student_id = models.CharField(max_length=20, unique=True, verbose_name='Código Estudiantil')
    first_name = models.CharField(max_length=100, verbose_name='Nombres')
    last_name = models.CharField(max_length=100, verbose_name='Apellidos')
    identification_number = models.CharField(max_length=20, unique=True, verbose_name='Documento de Identidad')
    
    # Información académica
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, related_name='students', verbose_name='Curso Actual')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='Estado')
    enrollment_date = models.DateField(verbose_name='Fecha de Matrícula')
    
    # Información personal
    birth_date = models.DateField(verbose_name='Fecha de Nacimiento')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name='Género')
    address = models.TextField(verbose_name='Dirección')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Teléfono')
    
    # Información del acudiente
    guardian_name = models.CharField(max_length=200, verbose_name='Nombre del Acudiente')
    guardian_relationship = models.CharField(max_length=50, verbose_name='Parentesco')
    guardian_phone = models.CharField(max_length=20, verbose_name='Teléfono del Acudiente')
    guardian_email = models.EmailField(blank=True, verbose_name='Email del Acudiente')
    
    # Información médica básica
    medical_info = models.TextField(blank=True, verbose_name='Información Médica')
    allergies = models.TextField(blank=True, verbose_name='Alergias')
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, verbose_name='Observaciones')
    
    class Meta:
        verbose_name = 'Estudiante'
        verbose_name_plural = 'Estudiantes'
        ordering = ['course__grade__level', 'course__section', 'last_name', 'first_name']
    
    def __str__(self):
        return f"{self.student_id} - {self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        """Calcular edad actual"""
        today = timezone.now().date()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))


class GradeRecord(models.Model):
    """Registro de calificaciones (escala 1-5)"""
    ACTIVITY_TYPE_CHOICES = [
        ('quiz', 'Quiz'),
        ('exam', 'Examen'),
        ('homework', 'Tarea'),
        ('project', 'Proyecto'),
        ('participation', 'Participación'),
        ('workshop', 'Taller'),
        ('lab', 'Laboratorio'),
        ('oral_exam', 'Examen Oral'),
        ('written_exam', 'Examen Escrito'),
        ('group_work', 'Trabajo en Grupo'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grades', verbose_name='Estudiante')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name='Materia')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Docente')
    period = models.ForeignKey(AcademicPeriod, on_delete=models.CASCADE, verbose_name='Período')
    
    activity_name = models.CharField(max_length=200, verbose_name='Nombre de la Actividad')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPE_CHOICES, verbose_name='Tipo de Actividad')
    
    # Calificación en escala 1-5
    grade_value = models.DecimalField(
        max_digits=3, 
        decimal_places=1, 
        validators=[MinValueValidator(Decimal('1.0')), MaxValueValidator(Decimal('5.0'))],
        verbose_name='Calificación'
    )
    
    date_recorded = models.DateField(verbose_name='Fecha de Registro')
    observations = models.TextField(blank=True, verbose_name='Observaciones')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.student.full_name} - {self.subject.name} - {self.grade_value}/5.0"
    
    @property
    def grade_text(self):
        """Convertir calificación numérica a texto"""
        if self.grade_value >= 4.6:
            return "Excelente"
        elif self.grade_value >= 4.0:
            return "Sobresaliente"
        elif self.grade_value >= 3.0:
            return "Aceptable"
        elif self.grade_value >= 2.0:
            return "Insuficiente"
        else:
            return "Deficiente"
    
    @property
    def is_passing(self):
        """Determinar si la calificación es aprobatoria"""
        return self.grade_value >= 3.0
    
    class Meta:
        verbose_name = 'Registro de Calificación'
        verbose_name_plural = 'Registros de Calificaciones'
        ordering = ['-date_recorded', 'student__last_name']


class Attendance(models.Model):
    """Control de asistencia diaria"""
    STATUS_CHOICES = [
        ('present', 'Presente'),
        ('absent', 'Ausente'),
        ('late', 'Tardanza'),
        ('justified', 'Falta Justificada'),
        ('early_departure', 'Salida Temprana'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records', verbose_name='Estudiante')
    date = models.DateField(verbose_name='Fecha')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Materia')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name='Estado')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Docente')
    
    # Información adicional
    arrival_time = models.TimeField(null=True, blank=True, verbose_name='Hora de Llegada')
    departure_time = models.TimeField(null=True, blank=True, verbose_name='Hora de Salida')
    justification = models.TextField(blank=True, verbose_name='Justificación')
    notes = models.TextField(blank=True, verbose_name='Observaciones')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.student.full_name} - {self.date} - {self.get_status_display()}"
    
    class Meta:
        verbose_name = 'Registro de Asistencia'
        verbose_name_plural = 'Registros de Asistencia'
        unique_together = ['student', 'date', 'subject']
        ordering = ['-date', 'student__last_name']


class BehaviorRecord(models.Model):
    """Registro de observaciones de comportamiento"""
    TYPE_CHOICES = [
        ('positive', 'Positivo'),
        ('negative', 'Negativo'),
        ('neutral', 'Neutral'),
    ]
    
    CATEGORY_CHOICES = [
        ('discipline', 'Disciplina'),
        ('participation', 'Participación'),
        ('collaboration', 'Colaboración'),
        ('respect', 'Respeto'),
        ('responsibility', 'Responsabilidad'),
        ('academic', 'Académico'),
        ('social', 'Social'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='behavior_records', verbose_name='Estudiante')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Docente')
    date = models.DateField(verbose_name='Fecha')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name='Tipo')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name='Categoría')
    
    description = models.TextField(verbose_name='Descripción')
    action_taken = models.TextField(blank=True, verbose_name='Acción Tomada')
    
    # Para seguimiento
    requires_followup = models.BooleanField(default=False, verbose_name='Requiere Seguimiento')
    parent_notified = models.BooleanField(default=False, verbose_name='Padre Notificado')
    notification_date = models.DateField(null=True, blank=True, verbose_name='Fecha de Notificación')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.student.full_name} - {self.get_type_display()} - {self.date}"
    
    class Meta:
        verbose_name = 'Registro de Comportamiento'
        verbose_name_plural = 'Registros de Comportamiento'
        ordering = ['-date', '-created_at']
