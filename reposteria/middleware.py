from django.http import JsonResponse

from .resilience import database_available


class DatabaseWriteProtectionMiddleware:
    """Impide operaciones que no pueden persistirse si MySQL está caído."""

    PREFIJOS_ESCRITURA = (
        '/admin/', '/cuentas/', '/mi-cuenta/', '/vendedor/',
        '/api/mis-solicitudes/', '/api/solicitudes/',
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            if request.path.startswith(self.PREFIJOS_ESCRITURA) and not database_available():
                mensaje = 'Operación temporalmente no disponible: no podemos confirmar una escritura sin acceso a MySQL.'
                if request.path.startswith('/api/'):
                    return JsonResponse({'detail': mensaje}, status=503)
                from django.contrib import messages
                messages.error(request, mensaje)
                from django.shortcuts import redirect
                return redirect(request.META.get('HTTP_REFERER') or '/')
        return self.get_response(request)
