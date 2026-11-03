# Anexo: uso de herramientas de inteligencia artificial

Durante el desarrollo de la Evaluación 3 se usó **Claude** (Anthropic) dentro de un proyecto de Claude
conectado al repositorio de GitHub. A continuación se transcriben los prompts exactos, en orden
cronológico, con lo que se hizo con cada respuesta.

> La pauta acepta captura **o transcripción**. Todos los prompts están transcritos textualmente abajo.
> Las capturas de `docs/capturas/` son evidencia adicional de las conversaciones en Claude.

## Resumen

| N° | Fecha (hora de Chile) | Prompt (resumen) | Resultado |
| --- | --- | --- | --- |
| 1 | 28-10-2026, 15:01 | Leer el repo, sacar el modelo de negocio y generar un prompt para las vistas de vendedor y comprador | Documento con modelo de negocio, roles y el prompt N° 2 |
| 2 | 28-10-2026 | Prompt generado por Claude y pegado en el asistente de IA de VS Code para implementar las vistas | Áreas `/vendedor/` y `/mi-cuenta/`, registro, grupos y tests (commit 6d70e7b) |
| 3 | 02-11-2026, 21:52 | Revisar el repo contra la escala de apreciación | Informe por indicador con prioridades |
| 4 | 02-11-2026, 22:05 | Implementar las mejoras | Variables de entorno, eliminar productos con integridad, galería desde la BD, README y este anexo (PR #1) |
| 5 | 02-11-2026, 22:13 | Pedir el link para dar acceso al repositorio | Enlace de instalación de la app de GitHub |
| 6 | 02-11-2026, 22:14 | Confirmar la conexión y hacer los commits | Push de la rama y apertura del PR #1 |
| 7 | 02-11-2026, 22:18 | Completar el anexo con todos los prompts y no cambiar las claves | Este anexo actualizado |

## Prompts exactos

### Prompt 1 · 28-10-2026

> Rey me puedes ayudar necesito que leas el repo y saque es el modelo de negocio, ya que necesito un prompt para generar una nueva vista para el vendedor, y  para el usuario que solo va a comprar y que se registra para tener mas beneficios. Y que se mantenga la vista de administrador que sale con los superusuarios (puedes reutilizar alguna vista de django)

**Uso de la respuesta:** Claude entregó un documento con el modelo de negocio deducido del código
(una sola tienda que vende por encargo, sin pago en línea), una propuesta de roles con grupos y
permisos de Django, y el prompt N° 2.

Evidencia: `capturas/prompt1.png`

### Prompt 2 · 28-10-2026 · prompt generado por Claude y usado para implementar

**Herramienta:** se pegó tal cual en el asistente de IA de Visual Studio Code, que implementó los cambios sobre el repositorio.

<details>
<summary>Ver el prompt completo</summary>

```text
Eres un desarrollador Django senior. Trabajas sobre el repositorio yummicatu_project (Django 5, app "reposteria", MySQL vía PyMySQL, plantillas en templates/ que extienden base.html, CSS en static/css/yummicatu.css, idioma es-cl, zona America/Santiago).

CONTEXTO DEL NEGOCIO (tal como está implementado hoy)
- Yummi Catu es una sola tienda de repostería artesanal y frutillas con crema. Vende por encargo: no hay carrito ni pago en línea; el negocio confirma por WhatsApp o correo.
- Modelos en reposteria/models.py:
  - Producto: nombre, categoria (texto), descripcion, foto (ruta static), imagen_subida (ImageField opcional), precio (PositiveIntegerField, CLP), destacado (bool). Propiedad url_imagen.
  - Cliente: run_cliente (PK, RUN chileno "12345678-9"), nombre_cliente, apellido, correo, telefono. Hoy NO está ligado a auth.User.
  - Solicitud: run_cliente (FK Cliente, related_name="pedidos"), id_producto (FK Producto, related_name="solicitudes"), detalle (texto), fecha (auto_now_add).
- Vistas públicas (reposteria/views.py, funciones): index, quienes_somos, galeria y formulario. Inicio, galería y el selector del formulario leen data/productos.json, no la BD. El formulario hace update_or_create del Cliente por RUN y crea una Solicitud.
- El Django admin (/admin/) está personalizado en reposteria/admin.py y templates/admin/. Lo usan solo los superusuarios.

OBJETIVO
Agregar dos áreas nuevas con su propia vista y menú, reutilizando lo que Django ya ofrece:
1. Panel del VENDEDOR en /vendedor/ (personal de la tienda, no superusuario).
2. Área del COMPRADOR registrado en /mi-cuenta/ (cliente que crea cuenta para tener beneficios).
El panel de ADMINISTRADOR en /admin/ debe quedar exactamente como está.

RESTRICCIONES
- No modifiques reposteria/admin.py, templates/admin/ ni la ruta admin/ de yummicatu_project/urls.py.
- No cambies el comportamiento de las vistas públicas para visitantes anónimos.
- Usa django.contrib.auth: User, Group, Permission, las vistas de django.contrib.auth.urls, UserCreationForm, LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin y las vistas genéricas basadas en clases. No escribas tu propio sistema de login, sesiones ni permisos.
- Las vistas nuevas leen productos desde la BD (modelo Producto), no desde el JSON.
- Mantén el estilo visual de base.html y yummicatu.css. Textos de la interfaz en español.
- Toda migración debe aplicarse sobre datos existentes sin perderlos (campos nuevos con null=True o con default).

PASO 1. MODELOS Y MIGRACIONES
- Cliente.usuario = OneToOneField(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=SET_NULL, related_name="cliente").
- Solicitud.estado = CharField con choices: pendiente, confirmada, en_preparacion, lista, entregada, cancelada; default "pendiente".
- Solicitud.cantidad = PositiveIntegerField(default=1).
- Solicitud.fecha_entrega = DateField(null=True, blank=True).
- Solicitud.precio_unitario = PositiveIntegerField(null=True, blank=True), copiado de Producto.precio al crear la solicitud. Agrega una propiedad total.
- Migración de datos que cree los grupos "Vendedores" y "Compradores". Asigna a "Vendedores": reposteria.view_solicitud, change_solicitud, view_cliente, view_producto, add_producto, change_producto. "Compradores" queda sin permisos de modelo.

PASO 2. AUTENTICACIÓN Y REGISTRO
- Incluye path("cuentas/", include("django.contrib.auth.urls")) y crea las plantillas en templates/registration/ (login, logged_out, password_reset_*, password_change_*).
- Configura LOGIN_URL = "login" y LOGOUT_REDIRECT_URL = "index". Tras el login redirige según el rol: superusuario a /admin/, grupo Vendedores a /vendedor/, el resto a /mi-cuenta/.
- Vista de registro /cuentas/registro/ con un formulario que extiende UserCreationForm y pide RUN, nombre, apellido, correo y teléfono. Valida el RUN chileno (formato y dígito verificador). Si ya existe un Cliente con ese RUN y sin usuario, vincúlalo; si ya tiene usuario, muestra un error. Agrega el usuario al grupo Compradores e inicia sesión.
- Los vendedores los crea el superusuario desde /admin/ (usuario con is_staff=False dentro del grupo Vendedores). No hay registro público de vendedores.

PASO 3. ÁREA DEL COMPRADOR (/mi-cuenta/), con LoginRequiredMixin y acceso solo a sus propios datos
- Inicio: saludo, pedidos en curso con su estado y últimos pedidos.
- Mis pedidos: lista y detalle filtrados por request.user.cliente. Devuelve 404 si el pedido es de otro cliente.
- Repetir pedido: abre el formulario de encargo con el producto y el detalle del pedido elegido.
- Mis datos: UpdateView del Cliente (sin permitir cambiar el RUN) y enlace a cambio de contraseña.
- Formulario de encargo: si el usuario está autenticado y tiene Cliente, precarga y oculta RUN, nombre, apellido, correo y teléfono; no permitas que el formulario anónimo sobrescriba los datos de un Cliente que ya tiene usuario.

PASO 4. PANEL DEL VENDEDOR (/vendedor/), con LoginRequiredMixin + PermissionRequiredMixin
- Bandeja de solicitudes (view_solicitud): tabla paginada con filtros por estado, rango de fechas y categoría, y búsqueda por RUN, nombre o producto. Pendientes primero.
- Detalle de solicitud: datos del cliente con enlaces tel: y https://wa.me/ y un formulario para cambiar estado y fecha_entrega (change_solicitud).
- Productos: lista, crear y editar (add_producto / change_producto) con nombre, categoría, descripción, precio, destacado e imagen_subida. Sin borrar.
- Clientes: lista de solo lectura (view_cliente) con cantidad de pedidos por cliente.
- Resumen: contadores de solicitudes por estado y pedidos del día.
- Un superusuario también puede entrar a /vendedor/.

PASO 5. NAVEGACIÓN
- En base.html: anónimo ve "Ingresar" y "Crear cuenta"; comprador ve "Mi cuenta" y "Salir"; vendedor ve "Panel vendedor"; el botón "Admin" solo aparece si user.is_superuser. Usa {% if perms.reposteria.change_solicitud %} y user.is_authenticated.
- Crea templates/reposteria/vendedor/ y templates/reposteria/cuenta/ con una plantilla base por área que extienda base.html.

PASO 6. PRUEBAS (reposteria/tests.py, o un paquete tests/)
- Anónimo en /vendedor/ y /mi-cuenta/ redirige al login.
- Comprador en /vendedor/ recibe 403.
- Comprador no puede ver el pedido de otro cliente (404).
- Vendedor cambia el estado de una solicitud.
- Vendedor sin is_staff no entra a /admin/.
- Superusuario sigue entrando a /admin/ y ve Productos, Clientes y Solicitudes.
- El registro crea el User, lo agrega a Compradores y vincula o crea el Cliente.
- El formulario anónimo sigue creando Cliente y Solicitud como antes.
Las pruebas deben correr con SQLite (configura un settings de test o una variable de entorno) para no depender de MySQL.

FORMA DE TRABAJO
- Antes de escribir código, lee los archivos mencionados y propón la lista de archivos que vas a crear o cambiar.
- Implementa un paso a la vez y ejecuta makemigrations, migrate y test al final de cada paso.
- Al terminar, entrega el resumen de URLs nuevas, los grupos y permisos creados y cómo crear un vendedor desde /admin/.
```

</details>

**Uso de la respuesta:** con este prompt se generaron las áreas `/vendedor/` y `/mi-cuenta/`, el
registro de compradores, los grupos Vendedores y Compradores y las pruebas automatizadas.

Evidencia: transcripción textual (el historial del asistente de VS Code no se conservó). El mismo
texto está en el documento que Claude entregó en la conversación del prompt 1 (`capturas/prompt1.png`),
y su resultado es el commit 6d70e7b del repositorio.

### Prompt 3 · 02-11-2026 (se adjuntó la escala de apreciación en Excel)

> Hola rey, Hoy necesito que revises el repo como esta actualmente (https://github.com/LuisGarrido052/yummicatu_project.git) (revisa el repositorio, ya que le hice cambios luego de la ultima vez que hablamos por esta sesion rey), y me digas si cumple con la escala de apreciación  de la evaluación,que adjunte con este hilo

**Uso de la respuesta:** informe por indicador. Detectó que la conexión no usaba variables de entorno
(indicador 2) y que no existía la operación Delete fuera del admin (indicador 5).

Evidencia: `capturas/prompt3.png`

### Prompt 4 · 02-11-2026

> Perfecto si puedes implementar esas cosas porfavor. Avisame si necesitas que abra vscode para clonar el repo y  hacer los commits  o si puedes hacer todo desde aca

**Uso de la respuesta:** se implementó la lectura de `SECRET_KEY` y de las credenciales desde `.env`,
la eliminación de productos con `on_delete=PROTECT`, la galería desde la base de datos, el README y
este anexo.

Evidencia: `capturas/prompt4.png`

### Prompt 5 · 02-11-2026

> enviame el link directo para darte acceso al repo rey porfavor

Evidencia: `capturas/prompt5.png`

### Prompt 6 · 02-11-2026

> Listo, confirmame si esta lista la conexion rey y haces los commits

**Uso de la respuesta:** se subió la rama y se abrió el Pull Request #1.

Evidencia: `capturas/prompt6.png`

### Prompt 7 · 02-11-2026

> Rey el anexo de IA debe contener el primer prompt que te envie junto con los que estan en estas conversacion, y respecto a lo otro la idea es que me funcione en inacap por lo que espero no hayas cambiado las claves ni nada

**Uso de la respuesta:** se completó este anexo con todos los prompts.

Evidencia: `capturas/prompt7.png`

## Referencias (APA 7.ª edición)

Anthropic. (2026). *Claude* [Modelo de lenguaje de gran tamaño]. https://claude.ai

Django Software Foundation. (2025). *Using the Django authentication system*. Django documentation. https://docs.djangoproject.com/en/5.2/topics/auth/default/

Django Software Foundation. (2025). *Model field reference: ForeignKey.on_delete*. Django documentation. https://docs.djangoproject.com/en/5.2/ref/models/fields/#django.db.models.ForeignKey.on_delete
