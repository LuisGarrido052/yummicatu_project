from django.core.management.commands.runserver import Command as DjangoRunserverCommand

from reposteria.resilience import database_available


class Command(DjangoRunserverCommand):
    """Permite iniciar runserver aunque MySQL esté caído; el chequeo de migraciones se pospone."""

    def check_migrations(self):
        if database_available():
            return super().check_migrations()
        self.stdout.write(self.style.WARNING('MySQL no disponible: inicio sin comprobar migraciones de la base principal.'))
