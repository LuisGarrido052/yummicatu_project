"""
Enrutamiento de URLs para la aplicación Repostería de Yummi Catu.
Rutas exigidas por la pauta de Evaluación 1:
- /               -> Vista principal (index)
- /quienes-somos/ -> Vista institucional (quienes_somos)
- /galeria/       -> Vista de catálogo dinámico que consume JSON (galeria)
- /formulario/    -> Vista de contacto y encargo de pedidos (formulario)

Áreas con cuenta de usuario:
- /cuentas/registro/ -> Alta de compradores
- /cuentas/inicio/   -> Redirección tras el login según el rol
- /mi-cuenta/        -> Área del comprador (urls_cuenta.py)
- /vendedor/         -> Panel del vendedor (urls_vendedor.py)
"""

from django.urls import include, path
from . import views, views_cuenta

urlpatterns = [
    # Ruta raíz / (Página de inicio)
    path('', views.index, name='index'),

    # Ruta institucional /quienes-somos/
    path('quienes-somos/', views.quienes_somos, name='quienes_somos'),

    # Ruta de catálogo /galeria/ (Consumo dinámico de productos.json)
    path('galeria/', views.galeria, name='galeria'),

    # Ruta de encargo /formulario/
    path('formulario/', views.formulario, name='formulario'),

    # Cuentas de usuario
    path('cuentas/registro/', views_cuenta.RegistroView.as_view(), name='registro'),
    path('cuentas/inicio/', views_cuenta.PostLoginView.as_view(), name='post_login'),

    # Áreas privadas
    path('mi-cuenta/', include('reposteria.urls_cuenta')),
    path('vendedor/', include('reposteria.urls_vendedor')),
]
