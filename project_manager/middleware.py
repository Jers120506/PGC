"""
Middleware de seguridad para forzar autenticación en todas las rutas
"""
from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user
from django.contrib import messages
from django.utils import timezone
import logging

logger = logging.getLogger('django.security')

class SecurityMiddleware:
    """
    Middleware que asegura que todos los usuarios estén autenticados
    antes de acceder a cualquier página del sistema
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # URLs que están permitidas sin autenticación
        self.allowed_paths = [
            '/auth/login/',
            '/auth/register/',
            '/auth/password-reset/',
            '/auth/password-reset/done/',
            '/auth/password-reset/confirm/',
            '/auth/password-reset/complete/',
            '/admin/',  # Django admin tiene su propia autenticación
        ]
        
        # Prefijos de URLs permitidas
        self.allowed_prefixes = [
            '/auth/password-reset/confirm/',
            '/admin/',
            '/static/',
            '/media/',
            '/academic-system/api/',  # APIs académicas permitidas
            '/academic-system/schedules/',  # Sistema de horarios completo
            '/academics_extended/api/',  # APIs del sistema académico extendido
            '/academics_extended/schedules/',  # URLs de horarios
        ]

    def __call__(self, request):
        # Obtener la ruta actual
        current_path = request.path
        
        # Verificar si la ruta está en las permitidas
        path_allowed = (
            current_path in self.allowed_paths or
            any(current_path.startswith(prefix) for prefix in self.allowed_prefixes)
        )
        
        # Si la ruta no está permitida y el usuario no está autenticado
        if not path_allowed and not request.user.is_authenticated:
            # Log del intento de acceso no autorizado
            ip = self.get_client_ip(request)
            logger.warning(f'Intento de acceso no autorizado a {current_path} desde IP {ip}')
            
            # Redirigir al login usando URL directa para evitar bucles
            return redirect('/auth/login/')
        
        # Si el usuario está autenticado pero no tiene perfil, redirigir a perfil
        if (request.user.is_authenticated and 
            hasattr(request.user, 'profile') and 
            not hasattr(request.user.profile, 'role') and
            current_path not in ['/auth/profile/', '/auth/logout/']):
            return redirect('authentication:profile')
        
        response = self.get_response(request)
        return response
    
    def get_client_ip(self, request):
        """Obtener la IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RoleRedirectMiddleware:
    """
    Middleware que redirige a los usuarios según su rol después del login
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Si el usuario acaba de hacer login y está en dashboard genérico
        if (request.user.is_authenticated and 
            request.path == '/dashboard/' and
            hasattr(request.user, 'profile')):
            
            # Redirigir según el rol usando URLs directas
            if request.user.profile.is_student:
                return redirect('/academic-system/')
            elif request.user.profile.is_teacher:
                return redirect('/academic-system/')
            elif request.user.profile.is_admin or request.user.is_superuser:
                return redirect('/auth/admin/')
        
        response = self.get_response(request)
        return response


class SessionSecurityMiddleware:
    """
    Middleware para mejorar la seguridad de las sesiones
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Si el usuario está autenticado, actualizar la actividad de sesión
        if request.user.is_authenticated:
            request.session['last_activity'] = str(request.user.last_login or '')
            
            # Regenerar session ID periódicamente para seguridad
            if not request.session.get('session_security_check'):
                request.session.cycle_key()
                request.session['session_security_check'] = True
        
        response = self.get_response(request)
        return response