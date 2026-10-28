"""
Validación del RUN chileno (formato y dígito verificador, módulo 11).
"""

import re

from django.core.exceptions import ValidationError

RUN_REGEX = re.compile(r'^(\d{7,8})-([\dK])$')


def normalizar_run(valor):
    """Quita puntos y espacios y deja la K en mayúscula: '12.345.678-k' -> '12345678-K'"""
    return (valor or '').replace('.', '').replace(' ', '').strip().upper()


def calcular_dv(cuerpo):
    suma = 0
    factor = 2
    for digito in reversed(cuerpo):
        suma += int(digito) * factor
        factor = 2 if factor == 7 else factor + 1
    resto = 11 - (suma % 11)
    if resto == 11:
        return '0'
    if resto == 10:
        return 'K'
    return str(resto)


def validar_run(valor):
    run = normalizar_run(valor)
    coincidencia = RUN_REGEX.match(run)
    if not coincidencia:
        raise ValidationError('El RUN debe tener el formato 12345678-9 (sin puntos y con guion).')
    cuerpo, dv = coincidencia.groups()
    if calcular_dv(cuerpo) != dv:
        raise ValidationError('El dígito verificador del RUN no es válido.')
    return run
