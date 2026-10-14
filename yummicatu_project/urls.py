"""
Configuración de URLs principales para yummicatu_project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    # Panel de administración de Django (Evaluación 2)
    path('admin/', admin.site.urls),

    # Enrutamiento de la aplicación principal 'reposteria' (Evaluación 1 y 2)
    path('', include('reposteria.urls')),
]

# Configuración para servir archivos multimedia y estáticos en modo de desarrollo (DEBUG=True)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += staticfiles_urlpatterns()
