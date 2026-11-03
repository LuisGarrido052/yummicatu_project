# Yummi Catu · Repostería artesanal y frutillas con crema

Aplicación web en Django para una tienda de repostería que recibe encargos sin pago en línea.
Proyecto de la asignatura Programación Back End (Evaluaciones 1, 2 y 3).

## Instalación

Requisitos: Python 3.12, XAMPP con MySQL/MariaDB encendido en el puerto 3306.

```bash
python -m venv venv
venv\Scripts\activate            # Windows  (Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt
```

### Variables de entorno

La clave secreta y las credenciales de la base de datos **no** están en el código.
Se leen desde un archivo `.env` que no se sube al repositorio (está en `.gitignore`).

1. Copia la plantilla: `copy .env.example .env` (Linux/Mac: `cp .env.example .env`).
2. Genera una clave secreta y pégala en `SECRET_KEY`:
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```
3. Completa `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST` y `DB_PORT` según tu MySQL.

Si falta una variable obligatoria, Django no arranca y muestra cuál falta.

### Base de datos

En phpMyAdmin crea la base `yummicatu_db` (utf8mb4) y luego:

```bash
python manage.py migrate          # crea tablas, grupos Vendedores/Compradores y sus permisos
python manage.py poblar_datos     # 6 productos, 6 clientes y 6 solicitudes de ejemplo
python manage.py createsuperuser
python manage.py runserver
```

## Roles y rutas

| Rol | Cómo se crea | Dónde trabaja | Puede |
| --- | --- | --- | --- |
| Visitante | — | `/`, `/galeria/`, `/formulario/` | Ver el catálogo y hacer un encargo |
| Comprador | `/cuentas/registro/` | `/mi-cuenta/` | Ver solo sus pedidos, repetirlos y editar sus datos |
| Vendedor | Usuario en el grupo **Vendedores** (desde `/admin/`) | `/vendedor/` | Gestionar solicitudes y crear, editar y eliminar productos |
| Administrador | `createsuperuser` | `/admin/` | Todo |

Login en `/cuentas/login/`; tras ingresar, cada rol es redirigido a su área.

## CRUD de productos (Evaluación 3)

| Operación | Ruta | Permiso |
| --- | --- | --- |
| Create | `/vendedor/productos/nuevo/` | `reposteria.add_producto` |
| Read | `/vendedor/productos/` y `/galeria/` (pública) | `reposteria.view_producto` (panel) |
| Update | `/vendedor/productos/<id>/editar/` | `reposteria.change_producto` |
| Delete | `/vendedor/productos/<id>/eliminar/` | `reposteria.delete_producto` |

**Integridad al eliminar:** `Solicitud.id_producto` usa `on_delete=PROTECT`. Un producto con pedidos
asociados no se puede borrar: la página de confirmación lo advierte y, si igual se envía el formulario,
la vista captura `ProtectedError` y avisa sin borrar nada. Así no se pierde el historial de encargos.

Las vistas sin sesión redirigen al login; un usuario con sesión pero sin el permiso recibe 403.

## Pruebas

```bash
python manage.py test --settings=yummicatu_project.settings_test
```

Usan SQLite en memoria, así que no necesitan XAMPP ni `.env`.

## Uso de inteligencia artificial

Ver [docs/anexo_ia.md](docs/anexo_ia.md).
