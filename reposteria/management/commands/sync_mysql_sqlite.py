from django.core.management.base import BaseCommand

from reposteria.resilience import (
    procesar_operaciones_pendientes,
    sync_mysql_to_sqlite,
)


class Command(BaseCommand):
    help = 'Sincroniza MySQL hacia SQLite y procesa encargos pendientes.'

    def handle(self, *args, **options):
        sincronizado = sync_mysql_to_sqlite()
        procesadas = procesar_operaciones_pendientes()
        if sincronizado:
            self.stdout.write(self.style.SUCCESS('Sincronización MySQL → SQLite completada.'))
        else:
            self.stdout.write(self.style.WARNING('MySQL no disponible o sincronización incompleta.'))
        self.stdout.write(self.style.SUCCESS(f'Operaciones pendientes procesadas: {procesadas}'))
