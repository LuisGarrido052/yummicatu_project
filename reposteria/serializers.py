from rest_framework import serializers

from .models import Producto, Solicitud


class ProductoPublicSerializer(serializers.ModelSerializer):
    """Contrato público: no expone información ajena al catálogo."""
    url_imagen = serializers.ReadOnlyField()

    class Meta:
        model = Producto
        fields = ('id', 'nombre', 'categoria', 'descripcion', 'precio', 'destacado', 'foto', 'url_imagen')
        read_only_fields = fields


class SolicitudPropiaSerializer(serializers.ModelSerializer):
    """Datos mínimos de una solicitud visible únicamente a su comprador o vendedor autorizado."""
    producto = serializers.CharField(source='id_producto.nombre', read_only=True)
    total = serializers.ReadOnlyField()

    class Meta:
        model = Solicitud
        fields = ('id', 'producto', 'detalle', 'cantidad', 'fecha', 'estado', 'fecha_entrega', 'precio_unitario', 'total')
        read_only_fields = fields
