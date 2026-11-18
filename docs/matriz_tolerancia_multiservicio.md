# Matriz de tolerancia a fallos multiservicio

Fecha de ejecución: 2026-11-18

## Alcance y límites de prueba reales

- Se probaron realmente escenarios con MySQL/MariaDB y servidor Django local.
- En este entorno no se detectó servicio Apache/XAMPP administrable por `Get-Service` (solo puerto 80 abierto por otro proceso no identificado como Apache), por lo que no se forzó parada de Apache para no alterar infraestructura no autorizada.
- No se realizó desconexión física de Internet del equipo ni cambio de adaptadores de red por no tener autorización explícita para alterar conectividad del sistema operativo.

## Tabla de resultados

| Servicio / Escenario | Resultado esperado | Resultado obtenido | Funcionalidades disponibles | Funcionalidades afectadas | Recuperación |
|---|---|---|---|---|---|
| 1) MySQL detenido (MariaDB `Stopped`) | Sitio sigue operativo en lecturas compatibles usando SQLite | **Probado OK**: `/`, `/galeria/`, `/api/productos/` respondieron HTTP 200, `origen=sqlite_fallback` | Inicio, galería, catálogo API público, estáticos previamente cargados | Escrituras directas en MySQL; operaciones privadas dependientes de MySQL | `Start-Service MariaDB`, luego sincronización |
| 2) Apache detenido | Django debe seguir si su servidor está activo | **No probado totalmente** (Apache no administrable detectado) | N/A | N/A | N/A |
| 3) Internet desconectado | Acceso local y recursos cacheados deben seguir donde corresponda | **No probado totalmente** (sin desconexión física/autorizada) | Potencial: navegación local + Service Worker para páginas visitadas | Carga remota externa | Reconectar red |
| 4) Django detenido | Sin proceso Django, no hay respuesta en 8000 | **Probado OK**: puerto 8000 pasó a `False` tras detener servidor | Ninguna en `:8000` | Todas las rutas atendidas por Django | Reiniciar `python manage.py runserver` |
| 5) MySQL + Internet desconectados simultáneamente | Lecturas desde SQLite local y degradación controlada | **No probado totalmente** (faltó corte real de Internet) | N/A | N/A | Reanudar Internet y MySQL |
| 6) Apache detenido con Django activo | Django debe seguir atendiendo en su puerto | **Parcial**: con puerto 80 activo y Django en 8000, Django respondió normalmente | Django local en 8000 | Apache específico no validado por ausencia de control de servicio | Reiniciar Apache si aplica |
| 7) Recuperación individual por servicio | Cada servicio vuelve a estado operativo y se reduce degradación | **Probado OK** para MySQL y Django: estado volvió a `mysql=up`, `django=up`, `degraded=False` | Todo el flujo público y API de estado | Ninguna tras recuperación | Iniciar servicio y verificar endpoint |
| 8) Recuperación múltiple tras interrupción | Recuperación progresiva sin duplicados | **Probado OK**: al volver MySQL se sincronizó y procesó cola pendiente sin duplicar | Catálogo desde MySQL (`origen=bd`), cola marcada `sincronizada` | Durante caída, operaciones directas a MySQL | `sync_mysql_sqlite` + verificación de cola |

## Evidencia técnica resumida

- Con MySQL caído: `index=200 galeria=200 api=200 origen=sqlite_fallback mysql=down degraded=True`.
- Django detenido: `django_port8000_after_stop=False`.
- Recuperación: `status=200 mysql=up django=up degraded=False`.

## Mecanismos implementados usados en estas pruebas

- Detección de MySQL: `database_available()`.
- Fallback de lectura: MySQL -> SQLite -> caché persistente -> JSON.
- Sincronización controlada: `sync_mysql_sqlite`.
- Cola idempotente de encargos: `OperacionPendiente`.
- Estado multiservicio: `GET /api/estado-servicios/`.
- Timeouts de conexión MySQL: `connect_timeout=3`, `read_timeout=5`, `write_timeout=5`.
