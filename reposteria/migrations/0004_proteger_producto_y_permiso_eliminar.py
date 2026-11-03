"""
Evaluación 3 - Eliminación con integridad referencial:
- Solicitud.id_producto pasa de CASCADE a PROTECT: no se puede borrar un producto que tiene pedidos.
- El grupo Vendedores recibe el permiso delete_producto para eliminar productos desde /vendedor/.
"""

import django.db.models.deletion
from django.db import migrations, models


def dar_permiso_eliminar(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    permiso = Permission.objects.filter(content_type__app_label='reposteria', codename='delete_producto').first()
    grupo = Group.objects.filter(name='Vendedores').first()
    if permiso and grupo:
        grupo.permissions.add(permiso)


def quitar_permiso_eliminar(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    permiso = Permission.objects.filter(content_type__app_label='reposteria', codename='delete_producto').first()
    grupo = Group.objects.filter(name='Vendedores').first()
    if permiso and grupo:
        grupo.permissions.remove(permiso)


class Migration(migrations.Migration):

    dependencies = [
        ('reposteria', '0003_grupos_roles'),
    ]

    operations = [
        migrations.AlterField(
            model_name='solicitud',
            name='id_producto',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='solicitudes',
                to='reposteria.producto',
                verbose_name='Producto Solicitado',
            ),
        ),
        migrations.RunPython(dar_permiso_eliminar, quitar_permiso_eliminar),
    ]
