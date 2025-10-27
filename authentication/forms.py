from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from authentication.models import UserProfile
from datetime import date
import re


class BaseProfileForm(forms.ModelForm):
    """Formulario base para información común de perfiles"""
    
    # Campos del modelo User
    first_name = forms.CharField(
        max_length=30,
        required=True,
        label='Nombres',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese los nombres'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        label='Apellidos',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese los apellidos'
        })
    )
    
    email = forms.EmailField(
        required=True,
        label='Correo Electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com'
        })
    )
    
    class Meta:
        model = UserProfile
        fields = [
            'phone', 'mobile_phone', 'bio', 'date_of_birth', 'gender',
            'identification_number', 'address', 'city', 'emergency_contact_name',
            'emergency_contact_phone', 'notifications_enabled', 'email_notifications'
        ]
        
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono fijo'
            }),
            'mobile_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de celular'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción breve...'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control'
            }),
            'identification_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de cédula'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Dirección completa'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ciudad'
            }),
            'emergency_contact_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del contacto de emergencia'
            }),
            'emergency_contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono de emergencia'
            }),
            'notifications_enabled': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'email_notifications': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        
        labels = {
            'phone': 'Teléfono',
            'mobile_phone': 'Celular',
            'bio': 'Biografía',
            'date_of_birth': 'Fecha de Nacimiento',
            'gender': 'Género',
            'identification_number': 'Número de Identificación',
            'address': 'Dirección',
            'city': 'Ciudad',
            'emergency_contact_name': 'Contacto de Emergencia',
            'emergency_contact_phone': 'Teléfono de Emergencia',
            'notifications_enabled': 'Notificaciones Activadas',
            'email_notifications': 'Notificaciones por Email',
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Si tenemos un usuario, prellenar campos del User
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email
    
    def clean_identification_number(self):
        """Validar número de identificación"""
        identification = self.cleaned_data.get('identification_number')
        if identification:
            # Verificar que solo contenga números
            if not re.match(r'^\d+$', identification):
                raise ValidationError('El número de identificación solo debe contener números.')
            
            # Verificar que no existe otro usuario con el mismo número
            existing = UserProfile.objects.filter(identification_number=identification)
            if self.instance and self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise ValidationError('Ya existe un usuario con este número de identificación.')
        
        return identification
    
    def clean_phone(self):
        """Validar formato de teléfono"""
        phone = self.cleaned_data.get('phone')
        if phone and not re.match(r'^[\d\s\-\+\(\)]+$', phone):
            raise ValidationError('Formato de teléfono inválido.')
        return phone
    
    def clean_mobile_phone(self):
        """Validar formato de celular"""
        mobile = self.cleaned_data.get('mobile_phone')
        if mobile and not re.match(r'^[\d\s\-\+\(\)]+$', mobile):
            raise ValidationError('Formato de celular inválido.')
        return mobile
    
    def clean_date_of_birth(self):
        """Validar fecha de nacimiento"""
        birth_date = self.cleaned_data.get('date_of_birth')
        if birth_date:
            today = date.today()
            age = today.year - birth_date.year - ((today.month, birth_date.day) < (birth_date.month, birth_date.day))
            
            if birth_date > today:
                raise ValidationError('La fecha de nacimiento no puede ser futura.')
            if age > 120:
                raise ValidationError('La fecha de nacimiento no es válida.')
        
        return birth_date


class AdminProfileForm(BaseProfileForm):
    """Formulario específico para administradores"""
    
    class Meta(BaseProfileForm.Meta):
        fields = BaseProfileForm.Meta.fields + [
            'education_level', 'institution', 'graduation_year',
            'professional_title', 'specialization', 'years_of_experience',
            'department', 'position', 'hire_date', 'work_schedule'
        ]
        
        widgets = {
            **BaseProfileForm.Meta.widgets,
            'education_level': forms.Select(attrs={'class': 'form-control'}),
            'institution': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Universidad o institución'
            }),
            'graduation_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1950,
                'max': date.today().year + 5
            }),
            'professional_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título profesional'
            }),
            'specialization': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Área de especialización'
            }),
            'years_of_experience': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 50
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Departamento'
            }),
            'position': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cargo'
            }),
            'hire_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'work_schedule': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Lunes a Viernes 8:00-17:00'
            }),
        }
        
        labels = {
            **BaseProfileForm.Meta.labels,
            'education_level': 'Nivel Educativo',
            'institution': 'Institución',
            'graduation_year': 'Año de Graduación',
            'professional_title': 'Título Profesional',
            'specialization': 'Especialización',
            'years_of_experience': 'Años de Experiencia',
            'department': 'Departamento',
            'position': 'Cargo',
            'hire_date': 'Fecha de Contratación',
            'work_schedule': 'Horario de Trabajo',
        }


class TeacherProfileForm(BaseProfileForm):
    """Formulario específico para profesores"""
    
    class Meta(BaseProfileForm.Meta):
        fields = BaseProfileForm.Meta.fields + [
            'education_level', 'institution', 'graduation_year',
            'professional_title', 'specialization', 'years_of_experience',
            'department', 'work_schedule'
        ]
        
        widgets = {
            **BaseProfileForm.Meta.widgets,
            'education_level': forms.Select(attrs={'class': 'form-control'}),
            'institution': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Universidad donde estudió'
            }),
            'graduation_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1950,
                'max': date.today().year + 5
            }),
            'professional_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Licenciatura, Ingeniería, etc.'
            }),
            'specialization': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Materias que enseña'
            }),
            'years_of_experience': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 50,
                'placeholder': 'Años como docente'
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Área académica'
            }),
            'work_schedule': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Horario de clases'
            }),
        }
        
        labels = {
            **BaseProfileForm.Meta.labels,
            'education_level': 'Nivel Educativo',
            'institution': 'Universidad',
            'graduation_year': 'Año de Graduación',
            'professional_title': 'Título Profesional',
            'specialization': 'Materias/Especialización',
            'years_of_experience': 'Años de Experiencia Docente',
            'department': 'Departamento Académico',
            'work_schedule': 'Horario de Trabajo',
        }


class SecretaryProfileForm(BaseProfileForm):
    """Formulario específico para secretarios"""
    
    class Meta(BaseProfileForm.Meta):
        fields = BaseProfileForm.Meta.fields + [
            'education_level', 'professional_title', 'years_of_experience',
            'department', 'position', 'hire_date', 'work_schedule'
        ]
        
        widgets = {
            **BaseProfileForm.Meta.widgets,
            'education_level': forms.Select(attrs={'class': 'form-control'}),
            'professional_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título o certificación'
            }),
            'years_of_experience': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 50
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Área asignada'
            }),
            'position': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cargo específico'
            }),
            'hire_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'work_schedule': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Horario de atención'
            }),
        }
        
        labels = {
            **BaseProfileForm.Meta.labels,
            'education_level': 'Nivel Educativo',
            'professional_title': 'Título/Certificación',
            'years_of_experience': 'Años de Experiencia',
            'department': 'Departamento',
            'position': 'Cargo',
            'hire_date': 'Fecha de Contratación',
            'work_schedule': 'Horario de Trabajo',
        }


class StudentProfileForm(BaseProfileForm):
    """Formulario específico para estudiantes"""
    
    class Meta(BaseProfileForm.Meta):
        fields = BaseProfileForm.Meta.fields + [
            'parent_guardian_name', 'parent_guardian_phone', 'parent_guardian_email'
        ]
        
        widgets = {
            **BaseProfileForm.Meta.widgets,
            'parent_guardian_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del padre, madre o tutor'
            }),
            'parent_guardian_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono del padre/tutor'
            }),
            'parent_guardian_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@padre.com'
            }),
        }
        
        labels = {
            **BaseProfileForm.Meta.labels,
            'parent_guardian_name': 'Nombre del Padre/Tutor',
            'parent_guardian_phone': 'Teléfono del Padre/Tutor',
            'parent_guardian_email': 'Email del Padre/Tutor',
        }
    
    def clean_parent_guardian_phone(self):
        """Validar teléfono del padre/tutor"""
        phone = self.cleaned_data.get('parent_guardian_phone')
        if phone and not re.match(r'^[\d\s\-\+\(\)]+$', phone):
            raise ValidationError('Formato de teléfono inválido.')
        return phone


class QuickProfileForm(forms.ModelForm):
    """Formulario rápido para edición básica de perfil"""
    
    first_name = forms.CharField(max_length=30, required=True, label='Nombres')
    last_name = forms.CharField(max_length=30, required=True, label='Apellidos')
    email = forms.EmailField(required=True, label='Correo Electrónico')
    
    class Meta:
        model = UserProfile
        fields = ['phone', 'bio', 'notifications_enabled']
        
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notifications_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email


class ProfileImageForm(forms.ModelForm):
    """Formulario específico para subir avatar"""
    
    class Meta:
        model = UserProfile
        fields = ['avatar']
        
        widgets = {
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
    
    def clean_avatar(self):
        """Validar imagen de avatar"""
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            # Verificar tamaño (máximo 5MB)
            if avatar.size > 5 * 1024 * 1024:
                raise ValidationError('La imagen no puede superar los 5MB.')
            
            # Verificar tipo de archivo
            valid_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if avatar.content_type not in valid_types:
                raise ValidationError('Solo se permiten imágenes JPG, PNG, GIF o WebP.')
        
        return avatar


# Formularios heredados del sistema anterior (mantenemos compatibilidad)
class UserAvatarForm(ProfileImageForm):
    """Alias para compatibilidad con código existente"""
    pass


class UserProfileForm(QuickProfileForm):
    """Alias para compatibilidad con código existente"""
    pass


# Función utilitaria para obtener el formulario correcto según el rol
def get_profile_form_class(role):
    """
    Devuelve la clase de formulario apropiada para el rol especificado
    
    Args:
        role (str): El rol del usuario ('admin', 'teacher', 'secretary', 'student')
    
    Returns:
        Form class: La clase de formulario correspondiente
    """
    form_mapping = {
        'admin': AdminProfileForm,
        'teacher': TeacherProfileForm,
        'secretary': SecretaryProfileForm,
        'student': StudentProfileForm,
    }
    
    return form_mapping.get(role, BaseProfileForm)


def get_profile_form(user, role=None, data=None, instance=None):
    """
    Crea una instancia del formulario apropiado para el usuario
    
    Args:
        user: El usuario de Django
        role: El rol (opcional, se toma del profile si no se especifica)
        data: Datos del formulario (opcional)
        instance: Instancia del UserProfile (opcional)
    
    Returns:
        Form instance: Instancia del formulario apropiado
    """
    if not role and hasattr(user, 'profile'):
        role = user.profile.role
    
    form_class = get_profile_form_class(role)
    
    kwargs = {'user': user}
    if data is not None:
        kwargs['data'] = data
    if instance is not None:
        kwargs['instance'] = instance
        
    return form_class(**kwargs)
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
            
        # Agregar clases CSS
        for field_name, field in self.fields.items():
            if field_name not in ['avatar', 'phone', 'bio']:  # Ya tienen clases
                field.widget.attrs.update({'class': 'form-control'})
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        
        if commit:
            # Actualizar también los datos del User
            user = profile.user
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            user.save()
            profile.save()
            
        return profile

class AdminUserCreationForm(UserCreationForm):
    """Formulario para que administradores creen profesores"""
    email = forms.EmailField(required=True, label='Correo Electrónico')
    first_name = forms.CharField(max_length=30, required=True, label='Nombre')
    last_name = forms.CharField(max_length=30, required=True, label='Apellido')
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar clases CSS a los campos
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control'
            })
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Asignar rol de profesor
            user.profile.role = 'teacher'
            user.profile.save()
        
        return user


class AssignStudentToTeacherForm(forms.Form):
    """Formulario para asignar estudiantes a profesores"""
    teacher = forms.ModelChoiceField(
        queryset=User.objects.filter(profile__role='teacher'),
        empty_label="Seleccionar profesor...",
        label='Profesor',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    students = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(profile__role='student', profile__teacher__isnull=True),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label='Estudiantes disponibles para asignar'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Actualizar querysets para mostrar nombres completos
        self.fields['teacher'].queryset = User.objects.filter(profile__role='teacher').select_related('profile')
        # Solo mostrar estudiantes que NO tienen profesor asignado
        self.fields['students'].queryset = User.objects.filter(
            profile__role='student', 
            profile__teacher__isnull=True
        ).select_related('profile')
        
        # Personalizar la representación
        self.fields['teacher'].label_from_instance = lambda obj: f"{obj.get_full_name() or obj.username} ({obj.email})"
        self.fields['students'].label_from_instance = lambda obj: f"{obj.get_full_name() or obj.username} ({obj.email})"


class UnassignStudentForm(forms.Form):
    """Formulario para desasignar estudiantes de profesores"""
    students = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label='Estudiantes a desasignar'
    )
    
    def __init__(self, teacher=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if teacher:
            self.fields['students'].queryset = User.objects.filter(
                profile__teacher=teacher, 
                profile__role='student'
            ).select_related('profile')
            self.fields['students'].label_from_instance = lambda obj: f"{obj.get_full_name() or obj.username} ({obj.email})"