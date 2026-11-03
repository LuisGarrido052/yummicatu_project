"""
Vistas de la aplicación Repostería - Negocio Yummi Catu.
Evaluación 1:
- Consumo y parseo de datos mock desde data/productos.json con la librería nativa json de Python.
- Vistas para Inicio, Quiénes Somos, Galería (catálogo dinámico) y Formulario de encargos.

Evaluación 2:
- Integración con modelos ORM (Cliente, Producto, Solicitud) al enviar el formulario.

Evaluación 3:
- La galería y el formulario leen los productos desde la BD (con productos.json como respaldo).
"""

import json
import logging
from pathlib import Path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.db import DatabaseError

# Modelos ORM para integración con BD (Evaluación 2 y 3)
from .models import Producto, Cliente, Solicitud

logger = logging.getLogger(__name__)


def _cargar_productos_json():
    """
    Función utilitaria que abre, lee y parsea el archivo productos.json
    utilizando el módulo 'json' nativo de Python (Requisito estricto Evaluación 1).
    """
    # Se busca el archivo en reposteria/data/productos.json o en BASE_DIR / data / productos.json
    ruta_json = Path(__file__).resolve().parent / 'data' / 'productos.json'
    if not ruta_json.exists():
        ruta_json = settings.BASE_DIR / 'data' / 'productos.json'

    with open(ruta_json, mode='r', encoding='utf-8') as archivo:
        productos = json.load(archivo)
    return productos


def index(request):
    """
    Página principal de Yummi Catu (index.html).
    Presenta banner de bienvenida (hero), especialidad de frutillas con crema,
    y productos estrella del día.
    """
    try:
        productos = _cargar_productos_json()
        # Seleccionar productos destacados para el inicio
        productos_destacados = [p for p in productos if p.get('destacado', True)][:3]
    except Exception as e:
        productos_destacados = []

    contexto = {
        'titulo': 'Inicio | Yummi Catu - Frutillas con Crema & Repostería',
        'productos_destacados': productos_destacados,
    }
    return render(request, 'reposteria/index.html', contexto)


def quienes_somos(request):
    """
    Página institucional de Yummi Catu (quienes_somos.html).
    Describe la historia, la pasión artesanal, selección de frutillas frescas
    y compromiso con la calidad.
    """
    contexto = {
        'titulo': 'Quiénes Somos | Yummi Catu Repostería',
    }
    return render(request, 'reposteria/quienes_somos.html', contexto)


def _cargar_productos():
    """
    Productos para las vistas públicas.
    Evaluación 3 (Read desde la BD): se leen con el ORM desde la tabla Producto, así lo que
    el vendedor crea, edita o elimina en /vendedor/ se refleja en la galería.
    Si la BD aún no tiene productos (o no está disponible) se usa productos.json (Evaluación 1).
    """
    try:
        productos = list(Producto.objects.all())
    except DatabaseError:
        productos = []
    if productos:
        return productos, 'bd'
    try:
        return _cargar_productos_json(), 'json'
    except (OSError, ValueError):
        return [], 'json'


def _campo(producto, nombre):
    """Lee un campo tanto de un objeto Producto como de un diccionario del JSON"""
    if isinstance(producto, dict):
        return producto.get(nombre)
    return getattr(producto, nombre, None)


def galeria(request):
    """
    Catálogo público (galeria.html).
    Lee los productos desde la base de datos (Evaluación 3) y, si está vacía,
    abre y parsea data/productos.json con la librería json (Evaluación 1).
    La lista se renderiza en galeria.html mediante {% for prod in productos %}.
    """
    productos, origen = _cargar_productos()

    # Filtrado simple por categoría si viene por parámetro GET
    categoria_filtro = request.GET.get('categoria', 'todas')
    if categoria_filtro != 'todas':
        productos_filtrados = [p for p in productos if _campo(p, 'categoria') == categoria_filtro]
    else:
        productos_filtrados = productos

    # Obtener categorías únicas para los botones de filtro
    categorias = sorted({_campo(p, 'categoria') for p in productos if _campo(p, 'categoria')})

    contexto = {
        'titulo': 'Galería de Repostería & Frutillas | Yummi Catu',
        'productos': productos_filtrados,
        'categorias': categorias,
        'categoria_activa': categoria_filtro,
        'total_productos': len(productos_filtrados),
        'origen_productos': origen,
    }
    return render(request, 'reposteria/galeria.html', contexto)


def _cliente_de_cuenta(request):
    """Cliente vinculado al usuario autenticado, o None (visitante anónimo, vendedor sin ficha, etc.)"""
    if request.user.is_authenticated:
        return getattr(request.user, 'cliente', None)
    return None


def _leer_cantidad(valor):
    try:
        return max(int(valor), 1)
    except (TypeError, ValueError):
        return 1


def formulario(request):
    """
    Formulario de contacto y encargo de pedidos personalizados (formulario.html).
    GET: Renderiza los campos de solicitud y lista de productos para elegir.
    POST: Procesa la solicitud, crea o actualiza Cliente y Solicitud en BD (Fase 2)
          y despliega mensajes informativos.
    Compradores con cuenta: sus datos personales se toman de su ficha de Cliente
    (no se piden en el formulario) y pueden repetir un pedido anterior con ?repetir=<id>.
    """
    cliente_cuenta = _cliente_de_cuenta(request)

    # Cargar productos disponibles para el selector del formulario (BD, o JSON si está vacía)
    productos, _ = _cargar_productos()

    contexto = {
        'titulo': 'Encargos y Pedidos Personalizados | Yummi Catu',
        'productos': productos,
        'cliente_cuenta': cliente_cuenta,
    }

    if request.method == 'POST':
        id_producto = request.POST.get('producto', '').strip()
        detalle = request.POST.get('detalle', '').strip()
        cantidad = _leer_cantidad(request.POST.get('cantidad'))

        if cliente_cuenta:
            run = cliente_cuenta.run_cliente
            nombre = cliente_cuenta.nombre_cliente
            apellido = cliente_cuenta.apellido
            correo = cliente_cuenta.correo
            telefono = cliente_cuenta.telefono
        else:
            run = request.POST.get('run', '').strip()
            nombre = request.POST.get('nombre', '').strip()
            apellido = request.POST.get('apellido', '').strip()
            correo = request.POST.get('correo', '').strip()
            telefono = request.POST.get('telefono', '').strip()

        # Validación básica de campos requeridos
        if not all([run, nombre, apellido, correo, telefono, detalle]):
            messages.error(request, 'Por favor, complete todos los campos requeridos del formulario.')
            return render(request, 'reposteria/formulario.html', {**contexto, 'form_data': request.POST})

        # Un RUN con cuenta solo puede encargar con su sesión iniciada:
        # el formulario anónimo no debe sobrescribir los datos de ese cliente.
        if not cliente_cuenta and Cliente.objects.filter(run_cliente=run, usuario__isnull=False).exists():
            messages.error(
                request,
                'Este RUN está asociado a una cuenta de Yummi Catu. Ingresa con tu usuario para hacer el encargo.'
            )
            return render(request, 'reposteria/formulario.html', {**contexto, 'form_data': request.POST})

        # Persistencia en Base de Datos (Evaluación 2 - Modelos Relacionales)
        try:
            # 1. Crear o actualizar Cliente identificado por RUN
            if cliente_cuenta:
                cliente = cliente_cuenta
            else:
                cliente, _ = Cliente.objects.update_or_create(
                    run_cliente=run,
                    defaults={
                        'nombre_cliente': nombre,
                        'apellido': apellido,
                        'correo': correo,
                        'telefono': telefono
                    }
                )

            # 2. Obtener producto de la BD (o crearlo si aún no existe en BD)
            producto_obj = None
            if id_producto:
                try:
                    producto_obj = Producto.objects.get(id=int(id_producto))
                except (Producto.DoesNotExist, ValueError):
                    # Fallback buscando por nombre o usando el primero
                    producto_obj = Producto.objects.first()

            if not producto_obj:
                # Si la BD no tiene productos cargados aún, creamos uno base
                producto_obj, _ = Producto.objects.get_or_create(
                    nombre="Frutillas con Crema Tradicionales",
                    defaults={
                        'categoria': 'Especialidad de la Casa',
                        'descripcion': 'Frutillas frescas con crema Chantilly artesanal.',
                        'foto': 'img/productos/frutillas_tradicionales.jpg'
                    }
                )

            # 3. Crear el registro Solicitud relacionado (el precio unitario se copia del producto)
            solicitud = Solicitud.objects.create(
                run_cliente=cliente,
                id_producto=producto_obj,
                detalle=detalle,
                cantidad=cantidad
            )

            messages.success(
                request,
                f'¡Muchas gracias {nombre}! Tu solicitud #{solicitud.id} para "{producto_obj.nombre}" ha sido registrada con éxito. Te contactaremos pronto al {telefono}.'
            )
            if cliente_cuenta:
                return redirect('cuenta:pedido_detalle', pk=solicitud.pk)
            return redirect('formulario')

        except DatabaseError:
            # No se informa un éxito falso: si la BD falla, el encargo NO quedó guardado
            logger.exception('No se pudo guardar la solicitud del formulario de encargos')
            messages.error(
                request,
                'No pudimos registrar tu solicitud por un problema técnico. Inténtalo nuevamente '
                'o escríbenos por WhatsApp.'
            )
            return render(request, 'reposteria/formulario.html', {**contexto, 'form_data': request.POST})

    # Repetir un pedido anterior del propio cliente
    if cliente_cuenta and request.GET.get('repetir', '').isdigit():
        pedido = Solicitud.objects.filter(pk=request.GET['repetir'], run_cliente=cliente_cuenta).first()
        if pedido:
            contexto['form_data'] = {
                'producto': str(pedido.id_producto_id),
                'detalle': pedido.detalle,
                'cantidad': pedido.cantidad,
            }

    return render(request, 'reposteria/formulario.html', contexto)
