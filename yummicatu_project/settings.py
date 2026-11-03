"""
Django settings for yummicatu_project.
Proyecto: Yummi Catu - Repostería Artesanal y Frutillas con Crema
Asignatura: Programación Back End (Evaluación 1 y Evaluación 2)
"""

import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

# 1. Definición de directorios base
# BASE_DIR apunta a la raíz del proyecto (donde se ubica manage.py)
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. Variables de entorno (Evaluación 3 - configuración segura)
# Los valores sensibles (clave secreta, credenciales de la BD) se leen desde el archivo .env,
# que NO se sube al repositorio (.gitignore). La plantilla con los nombres de las variables
# está en .env.example.
load_dotenv(BASE_DIR / '.env')


def env(nombre, defecto=None):
    """Lee una variable de entorno; si no tiene valor por defecto y no existe, detiene el arranque."""
    valor = os.environ.get(nombre, defecto)
    if valor is None:
        raise ImproperlyConfigured(
            f'Falta la variable de entorno {nombre}. Copia .env.example como .env y complétalo.'
        )
    return valor


def env_bool(nombre, defecto='False'):
    return env(nombre, defecto).strip().lower() in ('1', 'true', 'yes', 'si', 'sí')


def env_lista(nombre, defecto=''):
    return [item.strip() for item in env(nombre, defecto).split(',') if item.strip()]


# La clave secreta es obligatoria: sin .env el proyecto no arranca
SECRET_KEY = env('SECRET_KEY')

# Por seguridad, DEBUG queda apagado salvo que el .env diga lo contrario
DEBUG = env_bool('DEBUG', 'False')

ALLOWED_HOSTS = env_lista('ALLOWED_HOSTS', 'localhost,127.0.0.1')


# 4. Registro de Aplicaciones (INSTALLED_APPS)
# REQUISITO EVALUACIÓN 1:
# Para que Django reconozca la aplicación 'reposteria' y pueda gestionar sus modelos,
# plantillas y migraciones, DEBE agregarse explícitamente en la lista INSTALLED_APPS.
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Aplicación principal del negocio Yummi Catu
    'reposteria.apps.ReposteriaConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'yummicatu_project.urls'

# 5. Configuración del motor de plantillas nativo (DTL)
# Se configura 'DIRS' con BASE_DIR / 'templates' para que Django busque allí
# la plantilla base (base.html) y las vistas compartidas o por aplicación.
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',  # Para acceder a MEDIA_URL en plantillas
            ],
        },
    },
]

WSGI_APPLICATION = 'yummicatu_project.wsgi.application'


# 6. Configuración de Base de Datos (Evaluación 2 - MySQL / MariaDB en XAMPP)
# Nombre, usuario, contraseña, host y puerto vienen del .env (nunca escritos en el código).
# Se utiliza el backend nativo mysql emulado vía PyMySQL en __init__.py

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD', ''),
        'HOST': env('DB_HOST', 'localhost'),
        'PORT': env('DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}


# 7. Validadores de contraseñas de Django
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# 8. Localización e Idioma (Adaptado a Chile)
LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
# Se establece en False para compatibilidad directa con MySQL/MariaDB en XAMPP (Windows),
# evitando fallos de funciones de zona horaria (CONVERT_TZ) cuando las tablas tz no están instaladas en MySQL.
USE_TZ = False


# 9. Configuración de Archivos Estáticos (CSS, JavaScript, Imágenes del sitio)
# STATIC_URL: Prefijo de URL para acceder a los archivos estáticos en el navegador.
# STATICFILES_DIRS: Directorios locales adicionales donde Django buscará archivos estáticos durante desarrollo.
# STATIC_ROOT: Directorio final al que se recopilan los estáticos en producción al ejecutar collectstatic.
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'


# 10. Configuración de Archivos Multimedia (Subidos por usuarios / Django Admin)
# MEDIA_URL: Prefijo de URL público para los archivos subidos.
# MEDIA_ROOT: Carpeta física en el disco duro donde se guardan las imágenes (ej. fotos de productos).
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# 11. Autenticación (cuentas de compradores y vendedores)
# Tras el login, la vista 'post_login' redirige según el rol: /admin/, /vendedor/ o /mi-cuenta/.
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'post_login'
LOGOUT_REDIRECT_URL = 'index'

# En desarrollo los correos de recuperación de contraseña se muestran en la consola
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'Yummi Catu <contacto@yummicatu.cl>'
