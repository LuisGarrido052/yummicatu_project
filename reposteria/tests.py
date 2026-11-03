"""
Pruebas de roles y áreas de Yummi Catu.
Ejecutar sin MySQL: python manage.py test --settings=yummicatu_project.settings_test
"""

from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import Cliente, Producto, Solicitud
from .validators import validar_run

CLAVE = 'FrutillaCrema#2026'


class BaseRolesTestCase(TestCase):
    """Usuarios y datos comunes: un superusuario, un vendedor y dos compradores con un pedido cada uno"""

    @classmethod
    def setUpTestData(cls):
        cls.producto = Producto.objects.create(
            nombre='Torta Tres Leches Catu', categoria='Tortas',
            descripcion='Bizcocho tres leches', precio=18900,
        )
        cls.otro_producto = Producto.objects.create(
            nombre='Frutillas con Crema', categoria='Frutillas con crema',
            descripcion='Frutillas frescas', precio=4500,
        )

        cls.admin = User.objects.create_superuser('admin', 'admin@yummicatu.cl', CLAVE)

        cls.vendedor = User.objects.create_user('vendedora', 'venta@yummicatu.cl', CLAVE)
        cls.vendedor.groups.add(Group.objects.get(name='Vendedores'))

        cls.comprador = cls._crear_comprador('ana', '11111111-1', 'Ana')
        cls.otro_comprador = cls._crear_comprador('beto', '22222222-2', 'Beto')

        cls.pedido = Solicitud.objects.create(
            run_cliente=cls.comprador.cliente, id_producto=cls.producto, detalle='Para 20 personas', cantidad=2,
        )
        cls.pedido_ajeno = Solicitud.objects.create(
            run_cliente=cls.otro_comprador.cliente, id_producto=cls.otro_producto, detalle='Sin azúcar',
        )

    @staticmethod
    def _crear_comprador(username, run, nombre):
        user = User.objects.create_user(username, f'{username}@correo.cl', CLAVE, first_name=nombre)
        user.groups.add(Group.objects.get(name='Compradores'))
        Cliente.objects.create(
            run_cliente=run, nombre_cliente=nombre, apellido='Pérez',
            correo=f'{username}@correo.cl', telefono='+56912345678', usuario=user,
        )
        return user


class GruposYModelosTests(BaseRolesTestCase):
    def test_grupos_creados_por_migracion(self):
        vendedores = Group.objects.get(name='Vendedores')
        self.assertEqual(
            set(vendedores.permissions.values_list('codename', flat=True)),
            {'view_solicitud', 'change_solicitud', 'view_cliente', 'view_producto', 'add_producto', 'change_producto',
             'delete_producto'},
        )
        self.assertFalse(Group.objects.get(name='Compradores').permissions.exists())

    def test_solicitud_copia_precio_y_calcula_total(self):
        self.assertEqual(self.pedido.estado, Solicitud.ESTADO_PENDIENTE)
        self.assertEqual(self.pedido.precio_unitario, 18900)
        self.assertEqual(self.pedido.total, 37800)

        # Cambiar el precio del producto no altera pedidos ya creados
        self.producto.precio = 20000
        self.producto.save()
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.precio_unitario, 18900)

    def test_whatsapp_url(self):
        self.assertEqual(self.comprador.cliente.whatsapp_url, 'https://wa.me/56912345678')


class RunValidatorTests(TestCase):
    def test_runs_validos(self):
        self.assertEqual(validar_run('11.111.111-1'), '11111111-1')
        self.assertEqual(validar_run('12345678-5'), '12345678-5')
        self.assertEqual(validar_run('10000013-k'), '10000013-K')

    def test_runs_invalidos(self):
        for run in ['12345678-9', '1234-5', '12345678', 'abc']:
            with self.subTest(run=run), self.assertRaises(ValidationError):
                validar_run(run)


class AutenticacionTests(BaseRolesTestCase):
    def _login(self, username):
        return self.client.post(reverse('login'), {'username': username, 'password': CLAVE})

    def test_paginas_de_cuentas_responden(self):
        for nombre in ['login', 'registro', 'password_reset']:
            with self.subTest(nombre=nombre):
                respuesta = self.client.get(reverse(nombre))
                self.assertEqual(respuesta.status_code, 200)
                self.assertTemplateUsed(respuesta, 'base.html')

    def test_redireccion_tras_login_segun_rol(self):
        self.assertRedirects(self._login('admin'), reverse('post_login'), target_status_code=302)
        self.assertRedirects(self.client.get(reverse('post_login')), reverse('admin:index'))

        self.client.logout()
        self._login('vendedora')
        self.assertRedirects(self.client.get(reverse('post_login')), reverse('vendedor:resumen'), fetch_redirect_response=False)

        self.client.logout()
        self._login('ana')
        self.assertRedirects(self.client.get(reverse('post_login')), reverse('cuenta:inicio'), fetch_redirect_response=False)

    def test_cambio_de_contrasena_del_sitio_y_del_admin(self):
        self.client.force_login(self.comprador)
        respuesta = self.client.get(reverse('password_change'))
        self.assertTemplateUsed(respuesta, 'registration/yummi/password_change_form.html')
        self.assertTemplateUsed(respuesta, 'base.html')

        # El admin mantiene su propia plantilla
        self.client.force_login(self.admin)
        respuesta = self.client.get(reverse('admin:password_change'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateNotUsed(respuesta, 'base.html')
        self.assertTemplateUsed(respuesta, 'admin/base_site.html')

    def test_logout_redirige_al_inicio(self):
        # LOGOUT_REDIRECT_URL aplica tanto al sitio como al logout del admin
        for url in [reverse('logout'), reverse('admin:logout')]:
            with self.subTest(url=url):
                self.client.force_login(self.admin)
                self.assertRedirects(self.client.post(url), reverse('index'))
                self.assertNotIn('_auth_user_id', self.client.session)

    def test_registro_rechaza_run_invalido(self):
        respuesta = self.client.post(reverse('registro'), {
            'run': '12345678-9', 'nombre': 'Carla', 'apellido': 'Soto', 'correo': 'carla@correo.cl',
            'telefono': '+56987654321', 'username': 'carla', 'password1': CLAVE, 'password2': CLAVE,
        })
        self.assertEqual(respuesta.status_code, 200)
        self.assertFormError(respuesta.context['form'], 'run', 'El dígito verificador del RUN no es válido.')
        self.assertFalse(User.objects.filter(username='carla').exists())

    def test_registro_rechaza_run_con_cuenta(self):
        respuesta = self.client.post(reverse('registro'), {
            'run': '11111111-1', 'nombre': 'Ana', 'apellido': 'Pérez', 'correo': 'otra@correo.cl',
            'telefono': '+56987654321', 'username': 'ana2', 'password1': CLAVE, 'password2': CLAVE,
        })
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn('run', respuesta.context['form'].errors)
        self.assertFalse(User.objects.filter(username='ana2').exists())


class RegistroTests(TestCase):
    datos = {
        'run': '12.345.678-5', 'nombre': 'Carla', 'apellido': 'Soto', 'correo': 'carla@correo.cl',
        'telefono': '+56987654321', 'username': 'carla', 'password1': CLAVE, 'password2': CLAVE,
    }

    def test_registro_crea_usuario_cliente_y_grupo(self):
        respuesta = self.client.post(reverse('registro'), self.datos)
        self.assertRedirects(respuesta, reverse('cuenta:inicio'))

        user = User.objects.get(username='carla')
        self.assertTrue(user.groups.filter(name='Compradores').exists())
        self.assertEqual(user.cliente.run_cliente, '12345678-5')
        self.assertEqual(user.email, 'carla@correo.cl')
        # Queda con la sesión iniciada
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

    def test_registro_vincula_cliente_existente_sin_usuario(self):
        producto = Producto.objects.create(nombre='Pie de Limón', categoria='Tartas', descripcion='Pie')
        cliente = Cliente.objects.create(
            run_cliente='12345678-5', nombre_cliente='Carla', apellido='S.', correo='viejo@correo.cl', telefono='+56911111111',
        )
        Solicitud.objects.create(run_cliente=cliente, id_producto=producto, detalle='Encargo previo sin cuenta')

        self.client.post(reverse('registro'), self.datos)

        cliente.refresh_from_db()
        self.assertEqual(cliente.usuario.username, 'carla')
        self.assertEqual(cliente.correo, 'carla@correo.cl')
        self.assertEqual(Cliente.objects.count(), 1)
        # Sus pedidos anteriores aparecen en su cuenta
        respuesta = self.client.get(reverse('cuenta:pedidos'))
        self.assertContains(respuesta, 'Pie de Limón')


class AreaCompradorTests(BaseRolesTestCase):
    def test_anonimo_redirige_al_login(self):
        for url in [reverse('cuenta:inicio'), reverse('cuenta:pedidos'), reverse('cuenta:mis_datos')]:
            with self.subTest(url=url):
                self.assertRedirects(self.client.get(url), f"{reverse('login')}?next={url}")

    def test_inicio_muestra_pedidos_propios(self):
        self.client.force_login(self.comprador)
        respuesta = self.client.get(reverse('cuenta:inicio'))
        self.assertContains(respuesta, 'Hola, Ana')
        self.assertContains(respuesta, 'Torta Tres Leches Catu')
        self.assertEqual(list(respuesta.context['pedidos_en_curso']), [self.pedido])
        self.assertEqual(list(respuesta.context['ultimos_pedidos']), [self.pedido])

    def test_no_puede_ver_pedido_de_otro_cliente(self):
        self.client.force_login(self.comprador)
        self.assertEqual(self.client.get(reverse('cuenta:pedido_detalle', args=[self.pedido.pk])).status_code, 200)
        self.assertEqual(self.client.get(reverse('cuenta:pedido_detalle', args=[self.pedido_ajeno.pk])).status_code, 404)
        self.assertEqual(self.client.get(reverse('cuenta:repetir_pedido', args=[self.pedido_ajeno.pk])).status_code, 404)

    def test_repetir_pedido_precarga_formulario(self):
        self.client.force_login(self.comprador)
        respuesta = self.client.get(reverse('cuenta:repetir_pedido', args=[self.pedido.pk]), follow=True)
        self.assertEqual(respuesta.context['form_data']['producto'], str(self.producto.pk))
        self.assertEqual(respuesta.context['form_data']['detalle'], 'Para 20 personas')
        self.assertEqual(respuesta.context['form_data']['cantidad'], 2)
        self.assertContains(respuesta, 'Para 20 personas</textarea>')

    def test_mis_datos_actualiza_sin_cambiar_run(self):
        self.client.force_login(self.comprador)
        respuesta = self.client.post(reverse('cuenta:mis_datos'), {
            'run_cliente': '99999999-9', 'nombre_cliente': 'Ana María', 'apellido': 'Pérez',
            'correo': 'ana.maria@correo.cl', 'telefono': '+56900000000',
        })
        self.assertRedirects(respuesta, reverse('cuenta:mis_datos'))
        cliente = Cliente.objects.get(usuario=self.comprador)
        self.assertEqual(cliente.run_cliente, '11111111-1')
        self.assertEqual(cliente.nombre_cliente, 'Ana María')
        self.comprador.refresh_from_db()
        self.assertEqual(self.comprador.email, 'ana.maria@correo.cl')

    def test_vendedor_sin_ficha_no_entra_a_mi_cuenta(self):
        self.client.force_login(self.vendedor)
        self.assertRedirects(self.client.get(reverse('cuenta:inicio')), reverse('index'))


class FormularioEncargoTests(BaseRolesTestCase):
    def test_formulario_anonimo_crea_cliente_y_solicitud(self):
        respuesta = self.client.post(reverse('formulario'), {
            'run': '33333333-3', 'nombre': 'Daniela', 'apellido': 'Rojas', 'correo': 'dani@correo.cl',
            'telefono': '+56955555555', 'producto': str(self.producto.pk), 'detalle': 'Torta para 15',
        })
        self.assertRedirects(respuesta, reverse('formulario'))
        cliente = Cliente.objects.get(run_cliente='33333333-3')
        self.assertIsNone(cliente.usuario)
        solicitud = cliente.pedidos.get()
        self.assertEqual(solicitud.id_producto, self.producto)
        self.assertEqual(solicitud.cantidad, 1)
        self.assertEqual(solicitud.estado, Solicitud.ESTADO_PENDIENTE)
        self.assertEqual(solicitud.precio_unitario, 18900)

    def test_formulario_anonimo_actualiza_cliente_sin_cuenta(self):
        Cliente.objects.create(
            run_cliente='33333333-3', nombre_cliente='Dani', apellido='R', correo='a@a.cl', telefono='+56911111111',
        )
        self.client.post(reverse('formulario'), {
            'run': '33333333-3', 'nombre': 'Daniela', 'apellido': 'Rojas', 'correo': 'dani@correo.cl',
            'telefono': '+56955555555', 'producto': str(self.producto.pk), 'detalle': 'Otra torta',
        })
        self.assertEqual(Cliente.objects.get(run_cliente='33333333-3').nombre_cliente, 'Daniela')

    def test_formulario_anonimo_no_sobrescribe_cliente_con_cuenta(self):
        respuesta = self.client.post(reverse('formulario'), {
            'run': '11111111-1', 'nombre': 'Impostor', 'apellido': 'X', 'correo': 'x@x.cl',
            'telefono': '+56900000000', 'producto': str(self.producto.pk), 'detalle': 'Pedido falso',
        })
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Este RUN está asociado a una cuenta')
        cliente = Cliente.objects.get(run_cliente='11111111-1')
        self.assertEqual(cliente.nombre_cliente, 'Ana')
        self.assertEqual(cliente.pedidos.count(), 1)

    def test_formulario_con_cuenta_usa_ficha_del_cliente(self):
        self.client.force_login(self.comprador)
        respuesta = self.client.get(reverse('formulario'))
        self.assertContains(respuesta, 'Encargando como')
        self.assertNotContains(respuesta, 'name="run"')

        respuesta = self.client.post(reverse('formulario'), {
            'run': '22222222-2', 'nombre': 'Otro', 'producto': str(self.otro_producto.pk),
            'detalle': 'Frutillas para la oficina', 'cantidad': '3',
        })
        nueva = Solicitud.objects.latest('id')
        self.assertRedirects(respuesta, reverse('cuenta:pedido_detalle', args=[nueva.pk]))
        self.assertEqual(nueva.run_cliente_id, '11111111-1')
        self.assertEqual(nueva.cantidad, 3)
        self.assertEqual(nueva.total, 13500)
        self.assertEqual(Cliente.objects.get(run_cliente='22222222-2').nombre_cliente, 'Beto')


class PanelVendedorTests(BaseRolesTestCase):
    def urls_panel(self):
        return [
            reverse('vendedor:resumen'),
            reverse('vendedor:solicitudes'),
            reverse('vendedor:solicitud_detalle', args=[self.pedido.pk]),
            reverse('vendedor:productos'),
            reverse('vendedor:producto_crear'),
            reverse('vendedor:producto_editar', args=[self.producto.pk]),
            reverse('vendedor:producto_eliminar', args=[self.producto.pk]),
            reverse('vendedor:clientes'),
        ]

    def test_anonimo_redirige_al_login(self):
        for url in self.urls_panel():
            with self.subTest(url=url):
                self.assertRedirects(self.client.get(url), f"{reverse('login')}?next={url}")

    def test_comprador_recibe_403(self):
        self.client.force_login(self.comprador)
        for url in self.urls_panel():
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 403)
        respuesta = self.client.post(reverse('vendedor:solicitud_estado', args=[self.pedido.pk]), {'estado': 'cancelada'})
        self.assertEqual(respuesta.status_code, 403)
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.estado, Solicitud.ESTADO_PENDIENTE)

    def test_vendedor_y_superusuario_entran_al_panel(self):
        for user in [self.vendedor, self.admin]:
            self.client.force_login(user)
            for url in self.urls_panel():
                with self.subTest(user=user.username, url=url):
                    self.assertEqual(self.client.get(url).status_code, 200)

    def test_vendedor_cambia_estado_de_solicitud(self):
        self.client.force_login(self.vendedor)
        url = reverse('vendedor:solicitud_estado', args=[self.pedido.pk])
        respuesta = self.client.post(url, {'estado': 'confirmada', 'fecha_entrega': '2026-11-05'})
        self.assertRedirects(respuesta, reverse('vendedor:solicitud_detalle', args=[self.pedido.pk]))
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.estado, Solicitud.ESTADO_CONFIRMADA)
        self.assertEqual(str(self.pedido.fecha_entrega), '2026-11-05')

        # El comprador ve el nuevo estado en su cuenta
        self.client.force_login(self.comprador)
        self.assertContains(self.client.get(reverse('cuenta:pedido_detalle', args=[self.pedido.pk])), 'Confirmada')

    def test_detalle_muestra_enlaces_de_contacto(self):
        self.client.force_login(self.vendedor)
        respuesta = self.client.get(reverse('vendedor:solicitud_detalle', args=[self.pedido.pk]))
        self.assertContains(respuesta, 'href="tel:+56912345678"')
        self.assertContains(respuesta, 'href="https://wa.me/56912345678"')
        self.assertContains(respuesta, 'name="estado"')

    def test_bandeja_pendientes_primero_y_filtros(self):
        self.pedido_ajeno.estado = Solicitud.ESTADO_CONFIRMADA
        self.pedido_ajeno.save()
        # Más reciente, pero confirmada: debe quedar después de la pendiente
        Solicitud.objects.create(
            run_cliente=self.otro_comprador.cliente, id_producto=self.otro_producto, detalle='x', estado='lista',
        )
        self.client.force_login(self.vendedor)
        url = reverse('vendedor:solicitudes')

        solicitudes = list(self.client.get(url).context['solicitudes'])
        self.assertEqual(solicitudes[0], self.pedido)

        def ids(params):
            return {s.pk for s in self.client.get(url, params).context['solicitudes']}

        self.assertEqual(ids({'estado': 'pendiente'}), {self.pedido.pk})
        self.assertEqual(ids({'categoria': 'Tortas'}), {self.pedido.pk})
        self.assertEqual(ids({'q': '22222222'}), {self.pedido_ajeno.pk, Solicitud.objects.latest('id').pk})
        self.assertEqual(ids({'q': 'tres leches'}), {self.pedido.pk})
        self.assertEqual(ids({'q': 'Beto', 'estado': 'confirmada'}), {self.pedido_ajeno.pk})
        self.assertEqual(ids({'hasta': '2000-01-01'}), set())

    def test_resumen_cuenta_por_estado(self):
        self.client.force_login(self.vendedor)
        respuesta = self.client.get(reverse('vendedor:resumen'))
        estados = {e['clave']: e['total'] for e in respuesta.context['estados']}
        self.assertEqual(estados['pendiente'], 2)
        self.assertEqual(estados['entregada'], 0)
        self.assertEqual(len(respuesta.context['pedidos_hoy']), 2)

    def test_vendedor_crea_y_edita_producto(self):
        self.client.force_login(self.vendedor)
        respuesta = self.client.post(reverse('vendedor:producto_crear'), {
            'nombre': 'Kuchen de Frambuesa', 'categoria': 'Tartas', 'descripcion': 'Kuchen sureño', 'precio': 12000,
        })
        self.assertRedirects(respuesta, reverse('vendedor:productos'))
        kuchen = Producto.objects.get(nombre='Kuchen de Frambuesa')
        self.assertFalse(kuchen.destacado)

        self.client.post(reverse('vendedor:producto_editar', args=[kuchen.pk]), {
            'nombre': 'Kuchen de Frambuesa', 'categoria': 'Tartas', 'descripcion': 'Kuchen sureño',
            'precio': 12500, 'destacado': 'on',
        })
        kuchen.refresh_from_db()
        self.assertEqual(kuchen.precio, 12500)
        self.assertTrue(kuchen.destacado)

    def test_vendedor_elimina_producto_sin_pedidos(self):
        sin_pedidos = Producto.objects.create(nombre='Alfajor', categoria='Dulces', descripcion='Manjar', precio=1500)
        self.client.force_login(self.vendedor)
        confirmacion = self.client.get(reverse('vendedor:producto_eliminar', args=[sin_pedidos.pk]))
        self.assertContains(confirmacion, 'Sí, eliminar')
        respuesta = self.client.post(reverse('vendedor:producto_eliminar', args=[sin_pedidos.pk]))
        self.assertRedirects(respuesta, reverse('vendedor:productos'))
        self.assertFalse(Producto.objects.filter(pk=sin_pedidos.pk).exists())

    def test_no_se_elimina_producto_con_pedidos(self):
        self.client.force_login(self.vendedor)
        confirmacion = self.client.get(reverse('vendedor:producto_eliminar', args=[self.producto.pk]))
        self.assertContains(confirmacion, 'No se puede eliminar este producto')
        self.assertNotContains(confirmacion, 'Sí, eliminar')
        respuesta = self.client.post(reverse('vendedor:producto_eliminar', args=[self.producto.pk]), follow=True)
        self.assertRedirects(respuesta, reverse('vendedor:productos'))
        self.assertContains(respuesta, 'tiene 1 pedido asociado')
        self.assertTrue(Producto.objects.filter(pk=self.producto.pk).exists())
        self.assertTrue(Solicitud.objects.filter(pk=self.pedido.pk).exists())

    def test_comprador_y_anonimo_no_eliminan_productos(self):
        url = reverse('vendedor:producto_eliminar', args=[self.otro_producto.pk])
        self.assertRedirects(self.client.post(url), f"{reverse('login')}?next={url}")
        self.client.force_login(self.comprador)
        self.assertEqual(self.client.post(url).status_code, 403)
        self.assertTrue(Producto.objects.filter(pk=self.otro_producto.pk).exists())

    def test_clientes_con_cantidad_de_pedidos(self):
        self.client.force_login(self.vendedor)
        respuesta = self.client.get(reverse('vendedor:clientes'))
        totales = {c.run_cliente: c.total_pedidos for c in respuesta.context['clientes']}
        self.assertEqual(totales, {'11111111-1': 1, '22222222-2': 1})


class GaleriaTests(BaseRolesTestCase):
    def test_galeria_lee_productos_desde_la_bd(self):
        respuesta = self.client.get(reverse('galeria'))
        self.assertEqual(respuesta.context['origen_productos'], 'bd')
        self.assertContains(respuesta, 'Torta Tres Leches Catu')
        self.assertContains(respuesta, '$18.900')

    def test_galeria_usa_json_si_la_bd_esta_vacia(self):
        Solicitud.objects.all().delete()
        Producto.objects.all().delete()
        respuesta = self.client.get(reverse('galeria'))
        self.assertEqual(respuesta.context['origen_productos'], 'json')
        self.assertTrue(respuesta.context['productos'])


class NavegacionTests(BaseRolesTestCase):
    def menu(self, user=None):
        if user:
            self.client.force_login(user)
        return self.client.get(reverse('index')).content.decode()

    def test_menu_segun_rol(self):
        casos = [
            (None, ['Ingresar', 'Crear cuenta'], ['Mi cuenta', 'Panel vendedor', '>\n              Admin', 'Salir']),
            (self.comprador, ['Mi cuenta', 'Salir'], ['Ingresar', 'Panel vendedor', '>\n              Admin']),
            (self.vendedor, ['Panel vendedor', 'Salir'], ['Ingresar', 'Mi cuenta', '>\n              Admin']),
            (self.admin, ['Panel vendedor', '>\n              Admin', 'Salir'], ['Ingresar', 'Mi cuenta']),
        ]
        for user, visibles, ocultos in casos:
            with self.subTest(user=user and user.username):
                self.client.logout()
                html = self.menu(user)
                for texto in visibles:
                    self.assertIn(texto, html)
                for texto in ocultos:
                    self.assertNotIn(texto, html)


class AdminTests(BaseRolesTestCase):
    def test_vendedor_sin_is_staff_no_entra_al_admin(self):
        self.client.force_login(self.vendedor)
        respuesta = self.client.get(reverse('admin:index'))
        self.assertRedirects(respuesta, f"{reverse('admin:login')}?next={reverse('admin:index')}")
        self.assertEqual(self.client.get(reverse('admin:reposteria_solicitud_changelist')).status_code, 302)

    def test_superusuario_entra_al_admin_y_ve_modelos(self):
        self.client.force_login(self.admin)
        respuesta = self.client.get(reverse('admin:index'))
        self.assertEqual(respuesta.status_code, 200)
        modelos = {m['object_name'] for app in respuesta.context['app_list'] for m in app['models']}
        self.assertTrue({'Producto', 'Cliente', 'Solicitud'} <= modelos)
        for modelo in ['producto', 'cliente', 'solicitud']:
            with self.subTest(modelo=modelo):
                self.assertEqual(self.client.get(reverse(f'admin:reposteria_{modelo}_changelist')).status_code, 200)
