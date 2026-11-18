"""
Migración de datos: crea los grupos de roles de Yummi Catu.
- Vendedores: personal de la tienda que gestiona solicitudes y productos en /vendedor/.
- Compradores: clientes con cuenta en /mi-cuenta/ (sin permisos de modelo).
También completa precio_unitario en las solicitudes existentes con el precio actual del producto.
"""

from django.contrib.auth.management import create_permissions
from django.db import migrations

PERMISOS_VENDEDORES = [
    'view_solicitud',
    'change_solicitud',
    'view_cliente',
    'view_producto',
    'add_producto',
    'change_producto',
]


def crear_grupos(apps, schema_editor):
    using = schema_editor.connection.alias
    # Los permisos se crean normalmente en post_migrate (después de todas las migraciones);
    # en una BD nueva aún no existen, así que se generan aquí.
    for app_config in apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, apps=apps, verbosity=0, using=using)
        app_config.models_module = None

    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    vendedores, _ = Group.objects.using(using).get_or_create(name='Vendedores')
    permisos = Permission.objects.using(using).filter(
        content_type__app_label='reposteria',
        codename__in=PERMISOS_VENDEDORES,
    )
    vendedores.permissions.add(*permisos)

    Group.objects.using(using).get_or_create(name='Compradores')


def eliminar_grupos(apps, schema_editor):
    using = schema_editor.connection.alias
    Group = apps.get_model('auth', 'Group')
    Group.objects.using(using).filter(name__in=['Vendedores', 'Compradores']).delete()


def completar_precios(apps, schema_editor):
    using = schema_editor.connection.alias
    Solicitud = apps.get_model('reposteria', 'Solicitud')
    for solicitud in Solicitud.objects.using(using).filter(precio_unitario__isnull=True).select_related('id_producto'):
        solicitud.precio_unitario = solicitud.id_producto.precio
        solicitud.save(using=using, update_fields=['precio_unitario'])


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('reposteria', '0002_roles_estado_pedido'),
    ]

    operations = [
        migrations.RunPython(crear_grupos, eliminar_grupos),
        migrations.RunPython(completar_precios, migrations.RunPython.noop),
    ]
