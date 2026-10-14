"""
Configuración de inicio para yummicatu_project.
Integración del driver PyMySQL y compatibilidad total con MariaDB 10.4.x de XAMPP.
"""

import pymysql

# 1. Configurar PyMySQL como driver oficial MySQLdb
pymysql.install_as_MySQLdb()

# 2. Configurar compatibilidad con MariaDB 10.4.x (XAMPP)
from django.db.backends.mysql.base import DatabaseWrapper
from django.db.backends.mysql.features import DatabaseFeatures

# Bypass del chequeo estricto de versión de MariaDB (Django 5/6 exige 10.11+)
DatabaseWrapper.check_database_version_supported = lambda self: None

# MariaDB 10.4 en XAMPP no soporta la cláusula RETURNING en INSERT (introducida en 10.5+)
DatabaseFeatures.can_return_columns_from_insert = False
DatabaseFeatures.can_return_rows_from_bulk_insert = False
DatabaseFeatures.has_native_uuid_field = False
