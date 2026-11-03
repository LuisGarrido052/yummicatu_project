"""
Vistas del panel del vendedor (/vendedor/).
Acceso por permisos del grupo "Vendedores" (los superusuarios tienen todos los permisos):
- Resumen y bandeja de solicitudes: reposteria.view_solicitud
- Cambio de estado y fecha de entrega: reposteria.change_solicitud
- Productos: view_producto / add_producto / change_producto / delete_producto
  (un producto con pedidos no se elimina: Solicitud.id_producto es PROTECT)
- Clientes: view_cliente (solo lectura)
"""

from datetime import date
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import ProtectedError
from django.db.models import Case, Count, IntegerField, Q, Value, When
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.dateparse import parse_date
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from .forms import ProductoForm, SolicitudGestionForm
from .models import Cliente, Producto, Solicitud


class VendedorMixin(LoginRequiredMixin, PermissionRequiredMixin):
    """Anónimo -> login; autenticado sin el permiso -> 403"""


class ResumenView(VendedorMixin, TemplateView):
    permission_required = 'reposteria.view_solicitud'
    template_name = 'reposteria/vendedor/resumen.html'

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        # order_by() vacío: el ordering del Meta no debe entrar al GROUP BY
        conteo = {
            fila['estado']: fila['total']
            for fila in Solicitud.objects.order_by().values('estado').annotate(total=Count('id'))
        }
        contexto['estados'] = [
            {'clave': clave, 'nombre': nombre, 'total': conteo.get(clave, 0)}
            for clave, nombre in Solicitud.ESTADOS
        ]
        hoy = date.today()
        contexto['hoy'] = hoy
        contexto['pedidos_hoy'] = (
            Solicitud.objects.filter(fecha__date=hoy).select_related('run_cliente', 'id_producto')
        )
        contexto['entregas_hoy'] = (
            Solicitud.objects.filter(fecha_entrega=hoy).exclude(estado__in=['entregada', 'cancelada'])
            .select_related('run_cliente', 'id_producto')
        )
        return contexto


class SolicitudListView(VendedorMixin, ListView):
    permission_required = 'reposteria.view_solicitud'
    template_name = 'reposteria/vendedor/solicitudes.html'
    context_object_name = 'solicitudes'
    paginate_by = 15

    def get_queryset(self):
        qs = Solicitud.objects.select_related('run_cliente', 'id_producto')
        params = self.request.GET

        estado = params.get('estado', '')
        if estado in dict(Solicitud.ESTADOS):
            qs = qs.filter(estado=estado)

        desde = parse_date(params.get('desde', '') or '')
        if desde:
            qs = qs.filter(fecha__date__gte=desde)
        hasta = parse_date(params.get('hasta', '') or '')
        if hasta:
            qs = qs.filter(fecha__date__lte=hasta)

        categoria = params.get('categoria', '')
        if categoria:
            qs = qs.filter(id_producto__categoria=categoria)

        q = params.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(run_cliente__run_cliente__icontains=q)
                | Q(run_cliente__nombre_cliente__icontains=q)
                | Q(run_cliente__apellido__icontains=q)
                | Q(id_producto__nombre__icontains=q)
            )

        # Pendientes primero; dentro de cada grupo, las más recientes arriba
        return qs.annotate(
            prioridad=Case(When(estado=Solicitud.ESTADO_PENDIENTE, then=Value(0)), default=Value(1), output_field=IntegerField())
        ).order_by('prioridad', '-fecha')

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        filtros = self.request.GET.copy()
        filtros.pop('page', None)
        contexto['filtros'] = self.request.GET
        contexto['querystring'] = filtros.urlencode()
        contexto['estados'] = Solicitud.ESTADOS
        contexto['categorias'] = Producto.objects.order_by('categoria').values_list('categoria', flat=True).distinct()
        return contexto


class SolicitudDetailView(VendedorMixin, DetailView):
    permission_required = 'reposteria.view_solicitud'
    model = Solicitud
    template_name = 'reposteria/vendedor/solicitud_detalle.html'
    context_object_name = 'solicitud'

    def get_queryset(self):
        return Solicitud.objects.select_related('run_cliente', 'id_producto')

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        if self.request.user.has_perm('reposteria.change_solicitud'):
            contexto['form'] = SolicitudGestionForm(instance=self.object)
        contexto['otros_pedidos'] = (
            self.object.run_cliente.pedidos.exclude(pk=self.object.pk).select_related('id_producto')[:5]
        )
        return contexto


class SolicitudEstadoView(VendedorMixin, SuccessMessageMixin, UpdateView):
    """Recibe el POST del formulario de estado del detalle"""
    permission_required = 'reposteria.change_solicitud'
    model = Solicitud
    form_class = SolicitudGestionForm
    template_name = 'reposteria/vendedor/solicitud_detalle.html'
    context_object_name = 'solicitud'
    http_method_names = ['post']
    success_message = 'Solicitud #%(id)s actualizada: %(estado)s.'

    def get_success_url(self):
        return reverse('vendedor:solicitud_detalle', args=[self.object.pk])

    def get_success_message(self, cleaned_data):
        return self.success_message % {'id': self.object.pk, 'estado': self.object.get_estado_display()}

    def get_context_data(self, **kwargs):
        # Si el formulario tiene errores se vuelve a mostrar el detalle completo
        contexto = super().get_context_data(**kwargs)
        contexto['otros_pedidos'] = self.object.run_cliente.pedidos.exclude(pk=self.object.pk)[:5]
        return contexto


class ProductoListView(VendedorMixin, ListView):
    permission_required = 'reposteria.view_producto'
    model = Producto
    template_name = 'reposteria/vendedor/productos.html'
    context_object_name = 'productos'
    paginate_by = 20


class ProductoCreateView(VendedorMixin, SuccessMessageMixin, CreateView):
    permission_required = 'reposteria.add_producto'
    model = Producto
    form_class = ProductoForm
    template_name = 'reposteria/vendedor/producto_form.html'
    success_url = reverse_lazy('vendedor:productos')
    success_message = 'Producto "%(nombre)s" creado.'


class ProductoUpdateView(VendedorMixin, SuccessMessageMixin, UpdateView):
    permission_required = 'reposteria.change_producto'
    model = Producto
    form_class = ProductoForm
    template_name = 'reposteria/vendedor/producto_form.html'
    success_url = reverse_lazy('vendedor:productos')
    success_message = 'Producto "%(nombre)s" actualizado.'


class ProductoDeleteView(VendedorMixin, DeleteView):
    """
    Eliminación de productos con validación de integridad:
    - GET: página de confirmación que muestra cuántos pedidos tiene el producto.
    - POST: si tiene pedidos asociados, la BD lo impide (PROTECT -> ProtectedError)
      y se informa al vendedor sin borrar nada; si no tiene, se elimina.
    """
    permission_required = 'reposteria.delete_producto'
    model = Producto
    template_name = 'reposteria/vendedor/producto_confirmar_eliminar.html'
    context_object_name = 'producto'
    success_url = reverse_lazy('vendedor:productos')

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['total_pedidos'] = self.object.solicitudes.count()
        return contexto

    def form_valid(self, form):
        nombre = self.object.nombre
        try:
            self.object.delete()
        except ProtectedError:
            total = self.object.solicitudes.count()
            messages.error(
                self.request,
                f'No se puede eliminar "{nombre}": tiene {total} pedido{"s" if total != 1 else ""} asociado{"s" if total != 1 else ""}. '
                'Puedes editarlo y quitarlo de destacados en lugar de borrarlo.'
            )
            return redirect('vendedor:productos')
        messages.success(self.request, f'Producto "{nombre}" eliminado.')
        return redirect(self.success_url)


class ClienteListView(VendedorMixin, ListView):
    permission_required = 'reposteria.view_cliente'
    template_name = 'reposteria/vendedor/clientes.html'
    context_object_name = 'clientes'
    paginate_by = 20

    def get_queryset(self):
        qs = (
            Cliente.objects.annotate(total_pedidos=Count('pedidos'))
            .order_by('nombre_cliente', 'apellido')
        )
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(run_cliente__icontains=q) | Q(nombre_cliente__icontains=q)
                | Q(apellido__icontains=q) | Q(correo__icontains=q)
            )
        return qs

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        q = self.request.GET.get('q', '')
        contexto['q'] = q
        contexto['querystring'] = urlencode({'q': q}) if q else ''
        return contexto
