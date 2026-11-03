"""
Rutas del panel del vendedor (/vendedor/).
"""

from django.urls import path

from . import views_vendedor

app_name = 'vendedor'

urlpatterns = [
    path('', views_vendedor.ResumenView.as_view(), name='resumen'),
    path('solicitudes/', views_vendedor.SolicitudListView.as_view(), name='solicitudes'),
    path('solicitudes/<int:pk>/', views_vendedor.SolicitudDetailView.as_view(), name='solicitud_detalle'),
    path('solicitudes/<int:pk>/estado/', views_vendedor.SolicitudEstadoView.as_view(), name='solicitud_estado'),
    path('productos/', views_vendedor.ProductoListView.as_view(), name='productos'),
    path('productos/nuevo/', views_vendedor.ProductoCreateView.as_view(), name='producto_crear'),
    path('productos/<int:pk>/editar/', views_vendedor.ProductoUpdateView.as_view(), name='producto_editar'),
    path('productos/<int:pk>/eliminar/', views_vendedor.ProductoDeleteView.as_view(), name='producto_eliminar'),
    path('clientes/', views_vendedor.ClienteListView.as_view(), name='clientes'),
]
