"""
Rutas del área del comprador (/mi-cuenta/).
"""

from django.urls import path

from . import views_cuenta

app_name = 'cuenta'

urlpatterns = [
    path('', views_cuenta.CuentaInicioView.as_view(), name='inicio'),
    path('pedidos/', views_cuenta.MisPedidosView.as_view(), name='pedidos'),
    path('pedidos/<int:pk>/', views_cuenta.MiPedidoDetailView.as_view(), name='pedido_detalle'),
    path('pedidos/<int:pk>/repetir/', views_cuenta.RepetirPedidoView.as_view(), name='repetir_pedido'),
    path('mis-datos/', views_cuenta.MisDatosView.as_view(), name='mis_datos'),
]
