"""Utilidades de disponibilidad de MySQL y caché persistente de datos públicos."""

import json
import logging
from pathlib import Path

from django.conf import settings
from django.core.cache import cache
from django.db import DatabaseError, connection

from .models import Producto

logger = logging.getLogger(__name__)

PRODUCTS_CACHE_KEY = 'yummi:public-products:v1'
PRODUCTS_CACHE_TIMEOUT = 60 * 60 * 24


def database_available():
    """Comprueba la conectividad real sin sustituir ni modificar la configuración MySQL."""
    try:
        connection.ensure_connection()
        return True
    except DatabaseError:
        return False
    except Exception:
        logger.exception('No fue posible comprobar la conexión a la base de datos')
        return False


def producto_a_publico(producto):
    if isinstance(producto, dict):
        data = dict(producto)
        data.setdefault('id', None)
        data.setdefault('imagen_subida', None)
        data.setdefault('url_imagen', data.get('foto'))
        return data

    try:
        url_imagen = producto.url_imagen
    except Exception:
        url_imagen = producto.foto

    return {
        'id': producto.pk,
        'nombre': producto.nombre,
        'categoria': producto.categoria,
        'descripcion': producto.descripcion,
        'foto': producto.foto,
        'imagen_subida': producto.imagen_subida.name if producto.imagen_subida else None,
        'precio': producto.precio,
        'destacado': producto.destacado,
        'url_imagen': url_imagen,
    }


def _leer_json_publico():
    ruta = Path(__file__).resolve().parent / 'data' / 'productos.json'
    if not ruta.exists():
        ruta = settings.BASE_DIR / 'data' / 'productos.json'
    try:
        with open(ruta, 'r', encoding='utf-8') as archivo:
            datos = json.load(archivo)
        return datos if isinstance(datos, list) else []
    except (OSError, json.JSONDecodeError, TypeError):
        return []


def cargar_productos_publicos():
    """
    Obtiene productos desde MySQL; en éxito actualiza caché de disco.
    Si falla, usa caché persistente y nunca reemplaza datos válidos por una lista vacía.
    """
    if database_available():
        try:
            queryset = list(Producto.objects.all())
            if queryset:
                datos = [producto_a_publico(item) for item in queryset]
                cache.set(PRODUCTS_CACHE_KEY, datos, PRODUCTS_CACHE_TIMEOUT)
                return datos, 'bd'
        except DatabaseError:
            logger.exception('Error de lectura de productos desde MySQL')
            datos_cache = cache.get(PRODUCTS_CACHE_KEY)
            if isinstance(datos_cache, list) and datos_cache:
                return datos_cache, 'cache'

        # Base disponible pero sin catálogo: respaldo JSON, sin sobrescribir caché válida.
        datos_json = _leer_json_publico()
        if datos_json:
            return datos_json, 'json'
        return [], 'json'

    datos_cache = cache.get(PRODUCTS_CACHE_KEY)
    if isinstance(datos_cache, list) and datos_cache:
        return datos_cache, 'cache'

    datos_json = _leer_json_publico()
    if datos_json:
        return datos_json, 'json'
    return [], 'json'
