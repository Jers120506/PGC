from django.shortcuts import render, redirect
from django.contrib.auth import views as auth_views, login
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, View, TemplateView, FormView
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from .models import UserProfile
from .forms import AdminUserCreationForm, AssignStudentToTeacherForm, UnassignStudentForm, UserProfileForm, UserAvatarForm
import logging
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from django.utils import timezone

logger = logging.getLogger('authentication')

class CustomUserCreationForm(UserCreationForm):
    """Formulario personalizado de registro con información adicional"""
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
            # Todos los usuarios registrados son estudiantes por defecto
            user.profile.role = 'student'
            user.profile.save()
        
        return user


class CustomLoginView(auth_views.LoginView):
    """Vista personalizada de inicio de sesión con logging de seguridad"""
    template_name = 'authentication/login.html'
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        """Se ejecuta cuando el login es exitoso"""
        user = form.get_user()
        logger.info(f'Login exitoso para usuario: {user.username} desde IP: {self.get_client_ip()}')
        
        # Actualizar última actividad
        user.last_login = timezone.now()
        user.save()
        
        # Mostrar mensaje de bienvenida
        messages.success(
            self.request, 
            f'¡Bienvenido, {user.first_name or user.username}!'
        )
        
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Se ejecuta cuando el login falla"""
        username = form.data.get('username', 'Usuario desconocido')
        logger.warning(f'Intento de login fallido para usuario: {username} desde IP: {self.get_client_ip()}')
        messages.error(self.request, 'Usuario o contraseña incorrectos.')
        return super().form_invalid(form)
    
    def get_client_ip(self):
        """Obtener la IP del cliente"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip
    
    def get_success_url(self):
        """Redirigir directamente según el rol del usuario al panel de administración"""
        user = self.request.user
        if hasattr(user, 'profile'):
            if user.profile.role in ['teacher', 'admin', 'student', 'secretary']:
                return '/administration/'
        return '/dashboard/'

class CustomLogoutView(auth_views.LogoutView):
    """Vista personalizada de cierre de sesión con logging"""
    http_method_names = ['post', 'get']  # Permitir tanto GET como POST
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user = request.user
            ip = self.get_client_ip(request)
            logger.info(f'Usuario {user.username} iniciando logout desde IP {ip}')
            messages.info(request, 'Has cerrado sesión exitosamente.')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        # Permitir logout con GET request para compatibilidad
        return self.post(request, *args, **kwargs)
    
    def get_client_ip(self, request):
        """Obtener la IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def get_next_page(self):
        return reverse_lazy('authentication:login')

class RegisterView(CreateView):
    """Vista de registro de nuevos usuarios"""
    form_class = CustomUserCreationForm
    template_name = 'authentication/register.html'
    success_url = reverse_lazy('authentication:login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Iniciar sesión automáticamente después del registro
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = form.save()
        
        messages.success(
            self.request, 
            f'Cuenta creada exitosamente. ¡Bienvenido, {user.first_name}!'
        )
        
        # Login automático
        login(self.request, user)
        return redirect('/dashboard/')
    
    def form_invalid(self, form):
        messages.error(
            self.request, 
            'Por favor corrige los errores en el formulario.'
        )
        return super().form_invalid(form)

class CustomPasswordResetView(auth_views.PasswordResetView):
    """Vista personalizada para recuperación de contraseña"""
    template_name = 'authentication/password_reset.html'
    email_template_name = 'authentication/password_reset_email.html'
    subject_template_name = 'authentication/password_reset_subject.txt'
    success_url = reverse_lazy('authentication:password_reset_done')
    
    def form_valid(self, form):
        messages.success(
            self.request,
            'Se ha enviado un enlace de recuperación a tu correo electrónico.'
        )
        return super().form_valid(form)

class CustomPasswordResetDoneView(auth_views.PasswordResetDoneView):
    """Vista de confirmación de envío de email"""
    template_name = 'authentication/password_reset_done.html'

class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    """Vista para confirmar nueva contraseña"""
    template_name = 'authentication/password_reset_confirm.html'
    success_url = reverse_lazy('authentication:password_reset_complete')
    
    def form_valid(self, form):
        messages.success(
            self.request,
            '¡Tu contraseña ha sido cambiada exitosamente!'
        )
        return super().form_valid(form)

class CustomPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    """Vista de finalización de cambio de contraseña"""
    template_name = 'authentication/password_reset_complete.html'

class AdminCreateUserView(LoginRequiredMixin, CreateView):
    """Vista para que administradores creen nuevos usuarios"""
    form_class = AdminUserCreationForm
    template_name = 'authentication/admin_create_user.html'
    success_url = reverse_lazy('authentication:user_list')
    
    def dispatch(self, request, *args, **kwargs):
        # Solo administradores pueden acceder
        if not (request.user.is_authenticated and 
                (request.user.profile.is_admin or request.user.is_superuser)):
            raise PermissionDenied("Solo los administradores pueden crear usuarios.")
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        user = form.save()
        messages.success(
            self.request, 
            f'Usuario {user.username} creado exitosamente como {user.profile.get_role_display()}.'
        )
        return super().form_valid(form)

class AdminCreateStudentView(LoginRequiredMixin, CreateView):
    """Vista específica para que administradores creen estudiantes"""
    form_class = CustomUserCreationForm  # Usar el formulario de registro normal
    template_name = 'authentication/admin_create_student.html'
    success_url = reverse_lazy('authentication:user_list')
    
    def dispatch(self, request, *args, **kwargs):
        # Solo administradores pueden acceder
        if not (request.user.is_authenticated and 
                (request.user.profile.is_admin or request.user.is_superuser)):
            raise PermissionDenied("Solo los administradores pueden crear estudiantes.")
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        user = form.save()
        # Asegurar que el rol sea estudiante
        user.profile.role = 'student'
        user.profile.save()
        
        messages.success(
            self.request, 
            f'Estudiante {user.get_full_name() or user.username} creado exitosamente.'
        )
        return super().form_valid(form)

class UserListView(LoginRequiredMixin, ListView):
    """Vista para listar todos los usuarios (solo para administradores)"""
    model = User
    template_name = 'authentication/user_list.html'
    context_object_name = 'users'
    paginate_by = 20
    
    def dispatch(self, request, *args, **kwargs):
        # Solo administradores pueden acceder
        if not (request.user.is_authenticated and 
                (request.user.profile.is_admin or request.user.is_superuser)):
            raise PermissionDenied("Solo los administradores pueden ver la lista de usuarios.")
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return User.objects.select_related('profile').order_by('-date_joined')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_users'] = User.objects.count()
        context['total_students'] = UserProfile.objects.filter(role='student').count()
        context['total_teachers'] = UserProfile.objects.filter(role='teacher').count()
        context['total_admins'] = UserProfile.objects.filter(role='admin').count()
        return context

class AdminDashboardView(LoginRequiredMixin, ListView):
    """Dashboard específico para administradores"""
    template_name = 'authentication/admin_dashboard.html'
    context_object_name = 'recent_users'
    
    def dispatch(self, request, *args, **kwargs):
        # Solo administradores pueden acceder
        if not (request.user.is_authenticated and 
                (request.user.profile.is_admin or request.user.is_superuser)):
            raise PermissionDenied("Solo los administradores pueden acceder al panel de administración.")
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        # Obtener los 5 usuarios más recientes
        return User.objects.select_related('profile').order_by('-date_joined')[:5]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_users'] = User.objects.count()
        context['total_students'] = UserProfile.objects.filter(role='student').count()
        context['total_teachers'] = UserProfile.objects.filter(role='teacher').count()
        context['total_admins'] = UserProfile.objects.filter(role='admin').count()
        return context

class AdminDeleteUserView(LoginRequiredMixin, View):
    """Vista para eliminar usuarios (solo para administradores)"""
    
    def dispatch(self, request, *args, **kwargs):
        # Solo administradores pueden acceder
        if not (request.user.is_authenticated and 
                (request.user.profile.is_admin or request.user.is_superuser)):
            raise PermissionDenied("Solo los administradores pueden eliminar usuarios.")
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, user_id):
        try:
            user_to_delete = User.objects.get(id=user_id)
            
            # Prevenir que el admin se elimine a sí mismo
            if user_to_delete == request.user:
                messages.error(request, "No puedes eliminarte a ti mismo.")
                return redirect('authentication:user_list')
            
            # Prevenir eliminar el último administrador
            if user_to_delete.profile.is_admin:
                admin_count = UserProfile.objects.filter(role='admin').count()
                if admin_count <= 1:
                    messages.error(request, "No puedes eliminar el último administrador del sistema.")
                    return redirect('authentication:user_list')
            
            username = user_to_delete.username
            role = user_to_delete.profile.get_role_display()
            user_to_delete.delete()
            
            messages.success(
                request, 
                f'Usuario {username} ({role}) eliminado exitosamente.'
            )
            
        except User.DoesNotExist:
            messages.error(request, "El usuario no existe.")
        except Exception as e:
            messages.error(request, f"Error al eliminar usuario: {str(e)}")
            
        return redirect('authentication:user_list')


class ProfileView(LoginRequiredMixin, TemplateView):
    """Vista para mostrar y editar el perfil del usuario actual"""
    template_name = 'authentication/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Agregar el formulario apropiado según el rol
        if 'profile_form' not in context:
            if user.profile.is_admin:
                # Administradores pueden editar todo
                context['profile_form'] = UserProfileForm(
                    instance=user.profile, 
                    user=user
                )
                context['is_admin_edit'] = True
            else:
                # Usuarios normales solo pueden editar su foto
                context['profile_form'] = UserAvatarForm(
                    instance=user.profile
                )
                context['is_admin_edit'] = False
        
        # Información básica del usuario
        context['user_info'] = {
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'date_joined': user.date_joined,
            'last_login': user.last_login,
            'role': user.profile.get_role_display(),
            'role_key': user.profile.role,
        }
        
        # Estadísticas según el rol
        if user.profile.is_admin:
            # Para administradores: estadísticas del sistema
            context['stats'] = {
                'total_users': User.objects.count(),
                'total_admins': User.objects.filter(profile__role='admin').count(),
                'total_teachers': User.objects.filter(profile__role='teacher').count(),
                'total_students': User.objects.filter(profile__role='student').count(),
            }
        elif user.profile.is_teacher:
            # Para profesores: sus estadísticas
            assigned_students = user.profile.get_assigned_students()
            context['stats'] = {
                'assigned_students_count': assigned_students.count(),
                'total_students': User.objects.filter(profile__role='student').count(),
                'created_date': user.date_joined,
            }
            context['assigned_students'] = assigned_students
        else:
            # Para estudiantes: información básica
            context['stats'] = {
                'member_since': user.date_joined,
            }
            
        return context
    
    def post(self, request, *args, **kwargs):
        """Manejar la actualización del perfil"""
        user = request.user
        
        # Solo administradores pueden usar el POST de esta vista para perfil completo
        if user.profile.is_admin:
            profile_form = UserProfileForm(
                request.POST, 
                request.FILES, 
                instance=user.profile, 
                user=user
            )
            
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, '¡Perfil actualizado exitosamente!')
                return redirect('authentication:profile')
            else:
                messages.error(request, 'Por favor, corrige los errores en el formulario.')
                
            # Si hay errores, mostrar el formulario con errores
            context = self.get_context_data(**kwargs)
            context['profile_form'] = profile_form
            return self.render_to_response(context)
        else:
            # Usuarios normales usan la vista separada para avatar
            avatar_form = UserAvatarForm(
                request.POST, 
                request.FILES, 
                instance=user.profile
            )
            
            if avatar_form.is_valid():
                avatar_form.save()
                messages.success(request, '¡Foto de perfil actualizada exitosamente!')
                return redirect('authentication:profile')
            else:
                messages.error(request, 'Error al actualizar la foto. Verifica el formato del archivo.')
                return redirect('authentication:profile')


class AssignStudentsView(LoginRequiredMixin, FormView):
    """Vista para que los administradores asignen estudiantes a profesores"""
    template_name = 'authentication/assign_students.html'
    form_class = AssignStudentToTeacherForm
    success_url = reverse_lazy('authentication:assign_students')
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.profile.is_admin:
            raise PermissionDenied("Solo los administradores pueden asignar estudiantes.")
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        teacher = form.cleaned_data['teacher']
        students = form.cleaned_data['students']
        
        # Asignar los estudiantes al profesor
        for student in students:
            student.profile.teacher = teacher
            student.profile.save()
        
        messages.success(
            self.request, 
            f'{students.count()} estudiante(s) asignado(s) a {teacher.get_full_name() or teacher.username}'
        )
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Agregar información de asignaciones actuales
        context['assignments'] = []
        teachers = User.objects.filter(profile__role='teacher')
        
        for teacher in teachers:
            assigned_students = User.objects.filter(profile__teacher=teacher, profile__role='student')
            context['assignments'].append({
                'teacher': teacher,
                'students': assigned_students,
                'student_count': assigned_students.count()
            })
        
        # Estudiantes sin asignar
        context['unassigned_students'] = User.objects.filter(
            profile__role='student', 
            profile__teacher__isnull=True
        )
        
        return context


class UnassignStudentsView(LoginRequiredMixin, FormView):
    """Vista para desasignar estudiantes de un profesor específico"""
    template_name = 'authentication/unassign_students.html'
    form_class = UnassignStudentForm
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.profile.is_admin:
            raise PermissionDenied("Solo los administradores pueden desasignar estudiantes.")
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        teacher_id = self.kwargs.get('teacher_id')
        if teacher_id:
            try:
                teacher = User.objects.get(id=teacher_id, profile__role='teacher')
                kwargs['teacher'] = teacher
            except User.DoesNotExist:
                pass
        return kwargs
    
    def form_valid(self, form):
        students = form.cleaned_data['students']
        teacher_id = self.kwargs.get('teacher_id')
        
        try:
            teacher = User.objects.get(id=teacher_id, profile__role='teacher')
            
            # Desasignar los estudiantes
            for student in students:
                student.profile.teacher = None
                student.profile.save()
            
            messages.success(
                self.request, 
                f'{students.count()} estudiante(s) desasignado(s) de {teacher.get_full_name() or teacher.username}'
            )
        except User.DoesNotExist:
            messages.error(self.request, "Profesor no encontrado.")
        
        return redirect('authentication:assign_students')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher_id = self.kwargs.get('teacher_id')
        
        try:
            teacher = User.objects.get(id=teacher_id, profile__role='teacher')
            context['teacher'] = teacher
            context['assigned_students'] = User.objects.filter(
                profile__teacher=teacher, 
                profile__role='student'
            )
        except User.DoesNotExist:
            context['teacher'] = None
            context['assigned_students'] = User.objects.none()
        
        return context

# Usar las vistas personalizadas como alias
LoginView = CustomLoginView
LogoutView = CustomLogoutView
PasswordResetView = CustomPasswordResetView
PasswordResetDoneView = CustomPasswordResetDoneView
PasswordResetConfirmView = CustomPasswordResetConfirmView
PasswordResetCompleteView = CustomPasswordResetCompleteView



class AdminEditUserView(LoginRequiredMixin, TemplateView):
    """Vista para que administradores editen perfiles de otros usuarios"""
    template_name = 'authentication/admin_edit_user.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Solo administradores pueden acceder
        if not (request.user.profile.is_admin or request.user.is_superuser):
            raise PermissionDenied("No tienes permisos para editar perfiles de usuarios.")
        
        # Verificar si el usuario existe
        user_id = self.kwargs.get('user_id')
        try:
            User.objects.get(id=user_id)
        except User.DoesNotExist:
            messages.error(request, "Usuario no encontrado.")
            return redirect('authentication:user_list')
            
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs.get('user_id')
        
        # El usuario ya está validado en dispatch
        target_user = User.objects.get(id=user_id)
        context['target_user'] = target_user
        
        # Agregar formulario para editar el perfil
        if 'profile_form' not in context:
            context['profile_form'] = UserProfileForm(
                instance=target_user.profile,
                user=target_user
            )
            
        return context
    
    def post(self, request, *args, **kwargs):
        """Manejar la actualización del perfil del usuario"""
        user_id = self.kwargs.get('user_id')
        
        try:
            target_user = User.objects.get(id=user_id)
            profile_form = UserProfileForm(
                request.POST,
                request.FILES,
                instance=target_user.profile,
                user=target_user
            )
            
            if profile_form.is_valid():
                profile_form.save()
                messages.success(
                    request, 
                    f'¡Perfil de {target_user.get_full_name() or target_user.username} actualizado exitosamente!'
                )
                return redirect('authentication:user_list')
            else:
                messages.error(request, 'Por favor, corrige los errores en el formulario.')
                
        except User.DoesNotExist:
            messages.error(request, "Usuario no encontrado.")
            return redirect('authentication:user_list')
            
        # Si hay errores, mostrar el formulario con errores
        context = self.get_context_data(**kwargs)
        context['profile_form'] = profile_form
        return self.render_to_response(context)


# ============== SIGNALS PARA LOGGING DE SEGURIDAD ==============

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log cuando un usuario hace login exitoso"""
    ip = get_client_ip(request)
    logger.info(f'Usuario {user.username} inició sesión exitosamente desde IP {ip}')


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Log cuando un usuario hace logout"""
    if user:
        ip = get_client_ip(request)
        logger.info(f'Usuario {user.username} cerró sesión desde IP {ip}')


@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    """Log cuando falla un intento de login"""
    ip = get_client_ip(request)
    username = credentials.get('username', 'Usuario desconocido')
    logger.warning(f'Intento de login fallido para {username} desde IP {ip}')


def get_client_ip(request):
    """Función auxiliar para obtener la IP del cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
