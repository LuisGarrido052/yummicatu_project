"""
Filtros de plantilla para las áreas de cuenta y vendedor.
"""

from django import template

register = template.Library()


@register.filter
def clp(valor):
    """Formatea un entero como pesos chilenos: 18900 -> $18.900"""
    if valor in (None, ''):
        return '—'
    return f"${int(valor):,}".replace(',', '.')
