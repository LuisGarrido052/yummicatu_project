# Serialización, caché persistente y funcionamiento offline

## Archivos incorporados

- `reposteria/serializers.py`: serializadores públicos y privados autorizados.
- `reposteria/api_views.py`: endpoints JSON mediante Django REST Framework.
- `reposteria/resilience.py`: comprobación de MySQL, caché persistente y respaldo JSON.
- `reposteria/middleware.py`: bloqueo de operaciones de escritura sin MySQL.
- `static/sw.js`: caché offline del navegador para páginas públicas y recursos estáticos.

## Serialización

- `ProductoPublicSerializer`: serializa nombre, categoría, descripción, precio, destacado y imagen pública.
- `SolicitudPropiaSerializer`: expone únicamente el pedido mínimo propio o autorizado por el vendedor.
- No se serializan contraseñas, usuarios, correos privados ni datos personales de otros compradores.

## API

- `GET /api/estado/`: estado de MySQL y caché pública.
- `GET /api/productos/`: catálogo público desde MySQL, caché o JSON.
- `GET /api/productos/<id>/`: detalle público del catálogo.
- `GET /api/mis-solicitudes/`: solicitudes del comprador autenticado.
- `GET /api/solicitudes/`: solicitudes completas para usuarios con `reposteria.view_solicitud`.

Las rutas HTML existentes no fueron modificadas ni reemplazadas.

## Caché persistente

Se usa `django.core.cache.backends.filebased.FileBasedCache` en `data/cache/`, con expiración predeterminada de 24 horas. Cuando MySQL responde, el catálogo completo actualiza esta caché. Si la base cae o una consulta falla, se utiliza la última copia no vacía. Si MySQL está disponible pero el catálogo está vacío, se usa JSON sin reemplazar la caché anterior. La recuperación de MySQL actualiza nuevamente la caché en la siguiente consulta pública exitosa.

## Escrituras y operaciones protegidas

El middleware bloquea POST, PUT, PATCH y DELETE hacia administración, cuentas, área del comprador, panel del vendedor y formulario de encargos cuando MySQL no está disponible. Devuelve HTTP 503 o un mensaje de Django sin declarar éxito ni crear solicitudes duplicadas.

Inicio de sesión, registro, encargos, modificaciones de pedidos, CRUD de productos y administración continúan exigiendo MySQL. Las páginas públicas siguen disponibles desde caché o JSON.

## Offline del navegador

El Service Worker conserva páginas públicas previamente visitadas: inicio, quiénes somos, galería y formulario. También almacena CSS, JavaScript e imágenes solicitadas. No almacena páginas privadas, sesiones, credenciales ni respuestas de APIs privadas.

Esta capacidad solo funciona si el navegador pudo visitar previamente la página y descargar sus recursos. No permite usar el sitio cuando el servidor completo está apagado; tampoco convierte encargos o autenticación en operaciones offline.

## Seguridad

Los permisos existentes siguen activos. La caché no autoriza solicitudes ni modifica permisos. Los endpoints privados exigen autenticación y verifican permisos o propiedad del pedido. La caché solo contiene información pública del catálogo.

## Pruebas ejecutadas

Se ejecutó Django con SQLite aislado mediante:

`python manage.py test --settings=yummicatu_project.settings_test`

Resultado: 46 pruebas ejecutadas, todas exitosas. Se comprobó serialización pública, caché ante fallo simulado, aislamiento de solicitudes propias, permisos del vendedor y bloqueo de escritura sin base disponible.

## Base secundaria SQLite

MySQL continúa como alias `default`. Se añadió `sqlite_fallback` como base independiente persistente en `data/sqlite/yummicatu_fallback.sqlite3`. Ambos directorios de respaldo están excluidos de Git.

La migración `reposteria.0005_operacionpendiente` añadió una cola persistente con clave UUID de idempotencia. Las migraciones de datos 0003 y 0004 usan el alias real de conexión para evitar que migrar SQLite consulte MySQL.

## Sincronización

El comando `python manage.py sync_mysql_sqlite` sincroniza productos, clientes públicos necesarios y solicitudes desde MySQL hacia SQLite mediante `update_or_create`. No escribe datos vacíos si no existen productos válidos. También procesa encargos pendientes.

`reposteria/resilience.py` devuelve catálogo desde:

1. MySQL cuando está disponible.
2. SQLite persistente cuando MySQL cae.
3. Caché persistente como siguiente respaldo.
4. JSON cuando no existe ninguna copia dinámica.

La recuperación ejecuta la sincronización y procesa la cola. Las operaciones pendientes usan UUID determinístico basado en el payload, evitando duplicados al repetir la sincronización.

## Validación real realizada

Se creó `yummicatu_db`, se aplicaron migraciones existentes y se poblaron datos locales. Se ejecutó `sync_mysql_sqlite` con MySQL activo y se detuvo realmente el servicio Windows `MariaDB`.

Resultados observados:

- Django `runserver` inició mientras MariaDB estaba detenido.
- `/` respondió HTTP 200.
- `/galeria/` respondió HTTP 200.
- `/api/productos/` respondió HTTP 200 con origen `sqlite_fallback`.
- Se creó una operación pendiente con clave UUID mientras MySQL estaba caído.
- Al recuperar MariaDB, `sync_mysql_sqlite` procesó una operación pendiente.
- La segunda ejecución no creó duplicados; la cola quedó en estado `sincronizada`.
- MySQL recibió un cliente y una solicitud de prueba una sola vez.
- El API volvió a reportar origen `bd` después de recuperar MariaDB.

También se verificaron 46 pruebas Django exitosas con la configuración aislada existente. La prueba aislada no reemplaza la validación real realizada con MariaDB detenido.