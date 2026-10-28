"""
Vistas de cuentas de usuario y del área del comprador (/mi-cuenta/).
- PostLoginView: redirige tras el login según el rol del usuario.
- RegistroView: alta pública de compradores.
- Área del comprador: inicio, mis pedidos, detalle, repetir pedido y mis datos.
  Todas filtran por request.user.cliente: un comprador nunca ve datos de otro.
"""

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, RedirectView, TemplateView, UpdateView

from .forms import GRUPO_VENDEDORES, ClienteDatosForm, RegistroCompradorForm
from .models import Solicitud


class PostLoginView(LoginRequiredMixin, RedirectView):
    """Destino de LOGIN_REDIRECT_URL: superusuario -> admin, vendedor -> panel, resto -> mi cuenta"""

    def get_redirect_url(self, *args, **kwargs):
        user = self.request.user
        if user.is_superuser:
            return reverse('admin:index')
        if user.groups.filter(name=GRUPO_VENDEDORES).exists():
            return reverse('vendedor:resumen')
        return reverse('cuenta:inicio')


class RegistroView(CreateView):
    form_class = RegistroCompradorForm
    template_name = 'registration/registro.html'
    success_url = reverse_lazy('cuenta:inicio')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('post_login')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, f'¡Bienvenida/o a Yummi Catu, {self.object.first_name}! Tu cuenta quedó creada.')
        return response


class ClienteRequeridoMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Exige sesión iniciada y una ficha de Cliente vinculada al usuario"""

    def test_func(self):
        return hasattr(self.request.user, 'cliente')

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, 'Tu usuario no tiene una ficha de cliente. "Mi cuenta" es para compradores registrados.')
            return redirect('index')
        return super().handle_no_permission()

    @property
    def cliente(self):
        return self.request.user.cliente

    def pedidos_del_cliente(self):
        return Solicitud.objects.filter(run_cliente=self.cliente).select_related('id_producto')


class CuentaInicioView(ClienteRequeridoMixin, TemplateView):
    template_name = 'reposteria/cuenta/inicio.html'

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        pedidos = self.pedidos_del_cliente()
        contexto['cliente'] = self.cliente
        contexto['pedidos_en_curso'] = pedidos.filter(estado__in=Solicitud.ESTADOS_EN_CURSO)
        contexto['ultimos_pedidos'] = pedidos[:5]
        return contexto


class MisPedidosView(ClienteRequeridoMixin, ListView):
    template_name = 'reposteria/cuenta/pedidos.html'
    context_object_name = 'pedidos'
    paginate_by = 10

    def get_queryset(self):
        return self.pedidos_del_cliente()


class MiPedidoDetailView(ClienteRequeridoMixin, DetailView):
    template_name = 'reposteria/cuenta/pedido_detalle.html'
    context_object_name = 'pedido'

    def get_queryset(self):
        # Un pedido de otro cliente no está en este queryset -> 404
        return self.pedidos_del_cliente()


class RepetirPedidoView(ClienteRequeridoMixin, RedirectView):
    """Abre el formulario de encargo con el producto, la cantidad y el detalle de un pedido anterior"""

    def get_redirect_url(self, *args, **kwargs):
        pedido = get_object_or_404(self.pedidos_del_cliente(), pk=kwargs['pk'])
        return f"{reverse('formulario')}?producto={pedido.id_producto_id}&repetir={pedido.pk}"


class MisDatosView(ClienteRequeridoMixin, SuccessMessageMixin, UpdateView):
    form_class = ClienteDatosForm
    template_name = 'reposteria/cuenta/mis_datos.html'
    success_url = reverse_lazy('cuenta:mis_datos')
    success_message = 'Tus datos quedaron actualizados.'

    def get_object(self, queryset=None):
        return self.cliente

    def form_valid(self, form):
        response = super().form_valid(form)
        # Mantener sincronizados los datos del usuario (se usan en el correo de recuperación)
        user = self.request.user
        user.first_name = self.object.nombre_cliente
        user.last_name = self.object.apellido
        user.email = self.object.correo
        user.save(update_fields=['first_name', 'last_name', 'email'])
        return response
