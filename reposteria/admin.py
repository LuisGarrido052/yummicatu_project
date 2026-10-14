"""
Configuración del Panel de Administración de Django para Yummi Catu.
Requisito Evaluación 2:
Registro de modelos Producto, Cliente y Solicitud con ModelAdmin personalizados.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Producto, Cliente, Solicitud


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    """
    Gestión administrativa de los productos y especialidades de Yummi Catu.
    """
    list_display = ('id', 'miniatura', 'nombre', 'categoria', 'precio', 'destacado')
    list_filter = ('categoria', 'destacado')
    search_fields = ('nombre', 'categoria', 'descripcion')
    list_editable = ('precio', 'destacado')
    list_per_page = 10

    def miniatura(self, obj):
        """Muestra una vista previa de la foto en la tabla del Admin"""
        url = obj.url_imagen
        return format_html(
            '<img src="{}" style="width: 48px; height: 48px; object-fit: cover; border-radius: 8px; border: 1px solid #ddd;" />',
            url
        )
    miniatura.short_description = "Vista Previa"


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    """
    Gestión administrativa de los clientes de Yummi Catu.
    """
    list_display = ('run_cliente', 'nombre_cliente', 'apellido', 'correo', 'telefono')
    search_fields = ('run_cliente', 'nombre_cliente', 'apellido', 'correo', 'telefono')
    list_per_page = 15


@admin.register(Solicitud)
class SolicitudAdmin(admin.ModelAdmin):
    """
    Gestión administrativa de las solicitudes y pedidos personalizados.
    """
    list_display = ('id', 'run_cliente', 'id_producto', 'fecha_formateada', 'resumen_detalle')
    list_filter = ('fecha', 'id_producto__categoria')
    search_fields = ('run_cliente__run_cliente', 'run_cliente__nombre_cliente', 'run_cliente__apellido', 'id_producto__nombre', 'detalle')
    date_hierarchy = 'fecha'
    list_per_page = 15

    def fecha_formateada(self, obj):
        return obj.fecha.strftime("%d/%m/%Y %H:%M")
    fecha_formateada.short_description = "Fecha de Encargo"

    def resumen_detalle(self, obj):
        if len(obj.detalle) > 50:
            return f"{obj.detalle[:50]}..."
        return obj.detalle
    resumen_detalle.short_description = "Detalle"


# Personalización estética de los títulos del Django Admin
admin.site.site_header = "Yummi Catu - Panel de Administración"
admin.site.site_title = "Yummi Catu Admin"
admin.site.index_title = "Gestión de Repostería, Clientes y Encargos"
