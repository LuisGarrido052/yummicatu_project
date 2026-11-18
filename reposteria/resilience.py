"""Disponibilidad dual: MySQL principal, SQLite persistente y caché persistente."""

import json
import logging
import uuid
from pathlib import Path

from django.conf import settings
from django.core.cache import cache
from django.db import DatabaseError, connection, connections, transaction

from .models import Cliente, OperacionPendiente, Producto, Solicitud

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
        logger.exception('No fue posible comprobar MySQL')
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
        'id': producto.pk, 'nombre': producto.nombre, 'categoria': producto.categoria,
        'descripcion': producto.descripcion, 'foto': producto.foto,
        'imagen_subida': producto.imagen_subida.name if producto.imagen_subida else None,
        'precio': producto.precio, 'destacado': producto.destacado,
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


def leer_productos_sqlite():
    if 'sqlite_fallback' not in connections:
        return []
    try:
        productos = list(Producto.objects.using('sqlite_fallback').all())
        if productos:
            return [producto_a_publico(item) for item in productos]
    except Exception:
        logger.exception('No fue posible leer SQLite de respaldo')
    return []


def sync_mysql_to_sqlite():
    """Sincroniza catálogo y relaciones públicas MySQL → SQLite sin sobrescribir con vacíos."""
    if 'sqlite_fallback' not in connections:
        return False
    if not database_available():
        return False
    try:
        productos = list(Producto.objects.using('default').all())
        clientes = list(Cliente.objects.using('default').all())
        solicitudes = list(Solicitud.objects.using('default').select_related('run_cliente', 'id_producto'))
        if not productos:
            return False

        with transaction.atomic(using='sqlite_fallback'):
            for producto in productos:
                Producto.objects.using('sqlite_fallback').update_or_create(
                    id=producto.pk,
                    defaults={'nombre': producto.nombre, 'categoria': producto.categoria,
                              'descripcion': producto.descripcion, 'foto': producto.foto,
                              'imagen_subida': producto.imagen_subida.name if producto.imagen_subida else '',
                              'precio': producto.precio, 'destacado': producto.destacado},
                )
            for cliente in clientes:
                Cliente.objects.using('sqlite_fallback').update_or_create(
                    run_cliente=cliente.run_cliente,
                    defaults={'nombre_cliente': cliente.nombre_cliente, 'apellido': cliente.apellido,
                              'correo': cliente.correo, 'telefono': cliente.telefono, 'usuario': None},
                )
            for solicitud in solicitudes:
                Solicitud.objects.using('sqlite_fallback').update_or_create(
                    id=solicitud.pk,
                    defaults={'run_cliente_id': solicitud.run_cliente_id,
                              'id_producto_id': solicitud.id_producto_id,
                              'detalle': solicitud.detalle, 'fecha': solicitud.fecha,
                              'estado': solicitud.estado, 'cantidad': solicitud.cantidad,
                              'fecha_entrega': solicitud.fecha_entrega,
                              'precio_unitario': solicitud.precio_unitario},
                )
        return True
    except Exception:
        logger.exception('Falló la sincronización MySQL → SQLite')
        return False


def cargar_productos_publicos():
    """
    Obtiene productos desde MySQL; en éxito actualiza caché de disco.
    Si falla, usa caché persistente y nunca reemplaza datos válidos por una lista vacía.
    """
    if database_available():
        try:
            productos = list(Producto.objects.using('default').all())
            if productos:
                datos = [producto_a_publico(item) for item in productos]
                cache.set(PRODUCTS_CACHE_KEY, datos, PRODUCTS_CACHE_TIMEOUT)
                if sync_mysql_to_sqlite():
                    procesar_operaciones_pendientes()
                return datos, 'bd'
        except DatabaseError:
            logger.exception('Error de lectura de productos desde MySQL')
        else:
            datos_json = _leer_json_publico()
            if datos_json:
                return datos_json, 'json'
            return [], 'json'

    datos_sqlite = leer_productos_sqlite()
    if datos_sqlite:
        return datos_sqlite, 'sqlite_fallback'

    datos_cache = cache.get(PRODUCTS_CACHE_KEY)
    if isinstance(datos_cache, list) and datos_cache:
        return datos_cache, 'cache'

    datos_json = _leer_json_publico()
    if datos_json:
        return datos_json, 'json'
    return [], 'json'


def queue_encargo_fallback(*, run, nombre, apellido, correo, telefono, producto_id, detalle, cantidad):
    if 'sqlite_fallback' not in connections:
        raise RuntimeError('SQLite fallback no configurado')
    payload = {
        'run': run, 'nombre': nombre, 'apellido': apellido, 'correo': correo,
        'telefono': telefono, 'producto_id': int(producto_id), 'detalle': detalle,
        'cantidad': int(cantidad),
    }
    key = uuid.uuid5(uuid.NAMESPACE_URL, json.dumps(payload, sort_keys=True, ensure_ascii=False))
    operacion, created = OperacionPendiente.objects.using('sqlite_fallback').get_or_create(
        idempotency_key=key,
        defaults={'payload': payload, 'estado': 'pendiente'},
    )
    return operacion, created


def procesar_operaciones_pendientes():
    if 'sqlite_fallback' not in connections:
        return 0
    if not database_available():
        return 0
    procesadas = 0
    try:
        pendientes = list(OperacionPendiente.objects.using('sqlite_fallback').filter(estado='pendiente'))
        for operacion in pendientes:
            payload = operacion.payload or {}
            try:
                with transaction.atomic(using='default'):
                    cliente, _ = Cliente.objects.using('default').update_or_create(
                        run_cliente=payload['run'],
                        defaults={'nombre_cliente': payload['nombre'], 'apellido': payload['apellido'],
                                  'correo': payload['correo'], 'telefono': payload['telefono']},
                    )
                    producto = Producto.objects.using('default').get(pk=payload['producto_id'])
                    solicitud = Solicitud.objects.using('default').create(
                        run_cliente=cliente, id_producto=producto, detalle=payload['detalle'],
                        cantidad=payload['cantidad'],
                    )
                OperacionPendiente.objects.using('sqlite_fallback').filter(pk=operacion.pk).update(
                    estado='sincronizada',
                )
                procesadas += 1
            except Exception:
                logger.exception('Falló la sincronización de una operación pendiente')
                OperacionPendiente.objects.using('sqlite_fallback').filter(pk=operacion.pk).update(estado='fallida')
    except Exception:
        logger.exception('No fue posible procesar operaciones pendientes')
    return procesadas

def sincronizar_y_procesar():
    """Sincroniza MySQL a SQLite y procesa operaciones pendientes."""
    if not sync_mysql_to_sqlite():
        return False
    procesar_operaciones_pendientes()
    return True
