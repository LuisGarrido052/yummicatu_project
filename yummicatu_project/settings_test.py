"""
Settings para ejecutar las pruebas sin depender de MySQL/XAMPP.
Uso: python manage.py test --settings=yummicatu_project.settings_test
"""

from .settings import *  # noqa: F401,F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Hash rápido: las pruebas crean varios usuarios
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
