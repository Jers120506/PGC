"""
Utilidades de seguridad para el sistema de gestión de proyectos
"""
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger('django.security')

class SecurityUtils:
    """Utilidades para verificaciones de seguridad"""
    
    @staticmethod
    def check_user_session_security(user):
        """
        Verificar la seguridad de la sesión del usuario
        """
        checks = {
            'is_active': user.is_active,
            'has_profile': hasattr(user, 'profile'),
            'profile_complete': False,
            'last_login_recent': False,
        }
        
        if checks['has_profile']:
            profile = user.profile
            checks['profile_complete'] = bool(profile.role)
            
        if user.last_login:
            # Verificar si el último login fue en las últimas 24 horas
            last_login_limit = timezone.now() - timedelta(hours=24)
            checks['last_login_recent'] = user.last_login > last_login_limit
            
        return checks
    
    @staticmethod
    def get_security_recommendations(user):
        """
        Obtener recomendaciones de seguridad para el usuario
        """
        recommendations = []
        
        # Verificar contraseña
        if hasattr(user, 'profile') and hasattr(user.profile, 'password_changed_at'):
            if not user.profile.password_changed_at:
                recommendations.append({
                    'type': 'warning',
                    'message': 'Considera cambiar tu contraseña regularmente para mantener tu cuenta segura.'
                })
        
        # Verificar información de perfil
        if not user.first_name or not user.last_name:
            recommendations.append({
                'type': 'info',
                'message': 'Completa tu información de perfil para mejorar la experiencia.'
            })
        
        # Verificar email
        if not user.email:
            recommendations.append({
                'type': 'warning',
                'message': 'Agrega un email válido para recuperar tu contraseña si es necesario.'
            })
        
        return recommendations
    
    @staticmethod
    def log_security_event(event_type, user, message, ip_address=None):
        """
        Registrar eventos de seguridad
        """
        log_message = f'[{event_type}] Usuario: {user.username if user else "Anónimo"}'
        if ip_address:
            log_message += f' | IP: {ip_address}'
        log_message += f' | {message}'
        
        if event_type in ['WARNING', 'ERROR']:
            logger.warning(log_message)
        else:
            logger.info(log_message)
    
    @staticmethod
    def validate_user_access(user, required_role=None):
        """
        Validar el acceso del usuario según su rol
        """
        if not user.is_authenticated:
            return False, "Usuario no autenticado"
        
        if not user.is_active:
            return False, "Cuenta de usuario desactivada"
        
        if not hasattr(user, 'profile'):
            return False, "Perfil de usuario no encontrado"
        
        if required_role and user.profile.role != required_role:
            return False, f"Rol requerido: {required_role}, rol actual: {user.profile.role}"
        
        return True, "Acceso válido"


class SessionSecurity:
    """Manejo de seguridad de sesiones"""
    
    @staticmethod
    def is_session_valid(request):
        """
        Verificar si la sesión es válida
        """
        if not request.user.is_authenticated:
            return False
        
        # Verificar tiempo de sesión
        session_start = request.session.get('session_start_time')
        if session_start:
            session_duration = timezone.now().timestamp() - float(session_start)
            # Sesión máxima de 4 horas
            if session_duration > 14400:  # 4 horas en segundos
                return False
        
        return True
    
    @staticmethod
    def refresh_session_security(request):
        """
        Refrescar la seguridad de la sesión
        """
        if request.user.is_authenticated:
            # Actualizar tiempo de última actividad
            request.session['last_activity'] = timezone.now().timestamp()
            
            # Si no existe, establecer tiempo de inicio de sesión
            if not request.session.get('session_start_time'):
                request.session['session_start_time'] = timezone.now().timestamp()
            
            # Rotar session key cada cierto tiempo para seguridad
            last_rotation = request.session.get('last_key_rotation', 0)
            current_time = timezone.now().timestamp()
            
            # Rotar cada 30 minutos
            if current_time - float(last_rotation) > 1800:
                request.session.cycle_key()
                request.session['last_key_rotation'] = current_time