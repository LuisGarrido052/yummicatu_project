from django.db import DatabaseError
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Solicitud
from .resilience import cargar_productos_publicos, database_available
from .serializers import ProductoPublicSerializer, SolicitudPropiaSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def productos_api(request):
    """Catálogo público: MySQL primero, caché persistente como fallback."""
    datos, origen = cargar_productos_publicos()
    serializados = ProductoPublicSerializer(datos, many=True)
    return Response({'origen': origen, 'resultados': serializados.data})


@api_view(['GET'])
@permission_classes([AllowAny])
def producto_api(request, pk):
    datos, origen = cargar_productos_publicos()
    producto = next((item for item in datos if str(item.get('id')) == str(pk)), None)
    if producto is None:
        return Response({'detail': 'Producto no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
    return Response({'origen': origen, 'producto': ProductoPublicSerializer(producto).data})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mis_solicitudes_api(request):
    if not hasattr(request.user, 'cliente'):
        return Response({'detail': 'No tienes una ficha de comprador.'}, status=status.HTTP_403_FORBIDDEN)
    if not database_available():
        return Response({'detail': 'El servicio temporalmente requiere acceso a MySQL.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    try:
        solicitudes = Solicitud.objects.filter(run_cliente=request.user.cliente).select_related('id_producto')
        return Response(SolicitudPropiaSerializer(solicitudes, many=True).data)
    except DatabaseError:
        return Response({'detail': 'El servicio temporalmente requiere acceso a MySQL.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['GET'])
def solicitudes_vendedor_api(request):
    if not request.user.is_authenticated:
        return Response({'detail': 'Autenticación requerida.'}, status=status.HTTP_401_UNAUTHORIZED)
    if not request.user.has_perm('reposteria.view_solicitud'):
        return Response({'detail': 'No tienes permiso para consultar solicitudes.'}, status=status.HTTP_403_FORBIDDEN)
    if not database_available():
        return Response({'detail': 'El servicio temporalmente requiere acceso a MySQL.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    try:
        solicitudes = Solicitud.objects.select_related('run_cliente', 'id_producto').all()
        return Response(SolicitudPropiaSerializer(solicitudes, many=True).data)
    except DatabaseError:
        return Response({'detail': 'El servicio temporalmente requiere acceso a MySQL.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['GET'])
@permission_classes([AllowAny])
def estado_api(request):
    disponible = database_available()
    return Response({'database': 'available' if disponible else 'unavailable', 'public_catalog_cache': 'enabled'})
