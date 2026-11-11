# Tax SubManager — Diseño de la demo

Fecha: 2026-11-11 · Materia: Ingeniería en Software II (UACH, grupo 8cc2)

## Objetivo
Demo casi completa de Tax SubManager que cubra lo pedido en la documentación (AI_1_Equipo1_1) a escala pequeña,
que cualquier integrante pueda correr **sin Docker**, y de la que luego se reparta el trabajo del equipo.

## Alcance (según la documentación)
- Registro, login y cierre de sesión con JWT.
- Tres espacios de trabajo aislados por usuario: Personal, Universitario, Negocio.
- CRUD de pagos: nombre, monto, fecha de corte, categoría (+ periodicidad mensual/anual).
- Motor de reglas: presupuesto excedido (Universitario); "solicite factura" / "gasto no deducible" (Negocio).
- Dashboard por perfil activo: total mensual, categorías, próximos cortes, proyección a 12 meses, alertas.
- Backup manual (contingencia del riesgo R1) con listado y restauración.
- Docker Compose (PostgreSQL + backend + frontend) como camino opcional.

## Fuera de alcance
Conexión al SAT, timbrado de facturas, sincronización con VPS, recuperación de contraseña, roles.

## Arquitectura
- `backend/` Django 5 + Django REST Framework + SimpleJWT. SQLite por defecto; PostgreSQL si existe `POSTGRES_HOST`.
- `frontend/` React 18 + Vite + React Router, sin librerías de gráficas (barras con CSS).
- Aislamiento: toda consulta filtra por `workspace.owner = request.user`.
- Motor de reglas y cálculos del dashboard son **Python puro** (`apps/rules`, `apps/dashboard/calculations.py`),
  sin dependencia de Django, para poder probarlos con `unittest` sin instalar nada.

## API
| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/auth/register/` | Crea usuario + 3 espacios; devuelve tokens |
| POST | `/api/auth/login/`, `/api/auth/refresh/`, `/api/auth/logout/` | JWT |
| GET | `/api/auth/me/` | Usuario actual |
| GET | `/api/workspaces/`, `/api/workspaces/{id}/` (PATCH) | Espacios (presupuesto editable) |
| GET | `/api/categories/` | Categorías sugeridas por tipo |
| CRUD | `/api/workspaces/{id}/expenses/` | Gastos; create/update devuelven `alerts` |
| GET | `/api/workspaces/{id}/dashboard/` | Datos del dashboard |
| GET/POST | `/api/backups/` | Listar / crear respaldo |
| POST | `/api/backups/{nombre}/restore/` | Restaurar (hace respaldo de seguridad antes) |

## Decisión de diseño: formato del backup
El diseño en chat proponía `dumpdata`. Se cambió a un **JSON por usuario** (sus espacios y gastos), porque un
`dumpdata` global expondría hashes de contraseña y datos de otros usuarios a cualquiera con sesión.
Sigue siendo portable entre SQLite y PostgreSQL.

## Pruebas
- `backend/tests/` — `unittest` puro (reglas y cálculos): `python -m unittest discover -s tests -t .`
- `backend/apps/expenses/tests.py` — API (aislamiento entre usuarios, alertas): `python manage.py test`
