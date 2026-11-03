"""
Settings para ejecutar las pruebas sin depender de MySQL/XAMPP.
Uso: python manage.py test --settings=yummicatu_project.settings_test
"""

import os

# Valores solo para las pruebas: no requieren un .env ni MySQL
os.environ.setdefault('SECRET_KEY', 'clave-solo-para-pruebas')
os.environ.setdefault('DB_NAME', 'pruebas')
os.environ.setdefault('DB_USER', 'pruebas')

from .settings import *  # noqa: E402,F401,F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Hash rápido: las pruebas crean varios usuarios
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
