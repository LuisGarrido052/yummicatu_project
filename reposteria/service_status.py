"""Comprobaciones de disponibilidad de servicios para tolerancia multiservicio."""

import socket
from contextlib import closing

from .resilience import database_available


def _tcp_open(host, port, timeout=1.5):
    try:
        with closing(socket.create_connection((host, port), timeout=timeout)):
            return True
    except OSError:
        return False


def internet_available(timeout=1.5):
    """Chequeo simple de salida a Internet sin depender de DNS local."""
    return _tcp_open('1.1.1.1', 53, timeout=timeout) or _tcp_open('8.8.8.8', 53, timeout=timeout)


def apache_available(timeout=1.5):
    """Chequeo de servicio HTTP local típico de Apache/XAMPP."""
    return _tcp_open('127.0.0.1', 80, timeout=timeout)


def django_dev_available(timeout=1.5):
    """Chequeo del servidor de desarrollo de Django."""
    return _tcp_open('127.0.0.1', 8000, timeout=timeout)


def collect_service_status():
    mysql_ok = database_available()
    internet_ok = internet_available()
    apache_ok = apache_available()
    django_ok = django_dev_available()

    return {
        'mysql': 'up' if mysql_ok else 'down',
        'apache': 'up' if apache_ok else 'down',
        'internet': 'up' if internet_ok else 'down',
        'django_dev': 'up' if django_ok else 'down',
        'degraded_mode': not mysql_ok,
        'read_source_when_mysql_down': 'sqlite_fallback',
    }
