"""
Enrutamiento de URLs para la aplicación Repostería de Yummi Catu.
Rutas exigidas por la pauta de Evaluación 1:
- /               -> Vista principal (index)
- /quienes-somos/ -> Vista institucional (quienes_somos)
- /galeria/       -> Vista de catálogo dinámico que consume JSON (galeria)
- /formulario/    -> Vista de contacto y encargo de pedidos (formulario)
"""

from django.urls import path
from . import views

urlpatterns = [
    # Ruta raíz / (Página de inicio)
    path('', views.index, name='index'),

    # Ruta institucional /quienes-somos/
    path('quienes-somos/', views.quienes_somos, name='quienes_somos'),

    # Ruta de catálogo /galeria/ (Consumo dinámico de productos.json)
    path('galeria/', views.galeria, name='galeria'),

    # Ruta de encargo /formulario/
    path('formulario/', views.formulario, name='formulario'),
]
