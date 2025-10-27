"""
URL configuration for project_manager project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/administration/', permanent=False), name='home'),
    path('login/', RedirectView.as_view(url='/auth/login/', permanent=False), name='login_redirect'),
    path('auth/', include('authentication.urls', namespace='authentication')),
    path('academics/', include('academics.urls', namespace='academics')),
    path('academic-system/', include('academics_extended.urls', namespace='academics_extended')),
    path('administration/', include('administration.urls', namespace='administration')),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
