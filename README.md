# Tax SubManager (Asistente de Suscripciones y Deducciones)

Demo funcional del proyecto de **Ingeniería en Software II** (UACH, grupo 8cc2).
Aplicación local con espacios de trabajo aislados (Personal, Universitario y Negocio) para gestionar pagos
periódicos, con un motor de reglas (alertas de presupuesto y recomendaciones de deducibilidad) y un dashboard
por perfil.

> Las recomendaciones fiscales son **informativas**. No hay conexión con portales gubernamentales ni timbrado de facturas.

- **Frontend:** React 18 + Vite · **Backend:** Django 5 + Django REST Framework + JWT
- **Base de datos:** SQLite (local, por defecto) · PostgreSQL (opcional, con Docker)

## Requisitos
| Para… | Necesitas |
|---|---|
| Correr sin Docker (recomendado para desarrollar) | Python 3.10+ y Node.js 18+ |
| Correr con Docker (opcional) | Docker Desktop |

## Opción A — Sin Docker (la que usará el equipo)

Abre **dos terminales**.

**Terminal 1 — Backend**
```bash
cd backend
python -m venv venv
# Windows:      venv\Scripts\activate
# macOS/Linux:  source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo        # crea el usuario demo con datos de ejemplo
python manage.py runserver        # http://localhost:8000
```

**Terminal 2 — Frontend**
```bash
cd frontend
npm install
npm run dev                       # http://localhost:5173
```

Abre <http://localhost:5173> e inicia sesión con **demo / demo12345** (o crea tu propia cuenta).

## Opción B — Con Docker (un solo comando)
```bash
docker compose up --build
```
Levanta PostgreSQL, el backend (migra y carga el usuario demo) y el frontend.
Abre <http://localhost:5173>. Para detener: `Ctrl+C` y luego `docker compose down`
(agrega `-v` si quieres borrar también la base de datos).

## Estructura
```
tax-submanager/
├── backend/
│   ├── config/                 settings, urls, wsgi
│   ├── apps/
│   │   ├── accounts/           registro, login/logout JWT, comando seed_demo
│   │   ├── workspaces/         modelo Workspace (espacios aislados) y categorías
│   │   ├── expenses/           modelo Expense, CRUD de gastos (+ alertas al guardar)
│   │   ├── rules/              ★ motor de reglas (Python puro)
│   │   ├── dashboard/          ★ cálculos + endpoint del dashboard
│   │   └── backups/            backup manual (contingencia del riesgo R1)
│   └── tests/                  pruebas unittest del motor de reglas y cálculos
├── frontend/src/
│   ├── pages/                  Login, Register, Workspaces, Dashboard, Expenses, Backups
│   ├── components/             Layout, WorkspaceLayout, AlertList, Bars
│   ├── api.js · auth.jsx       cliente HTTP con JWT y contexto de sesión
├── docs/superpowers/specs/     especificación de diseño
└── docker-compose.yml
```

## Cómo funciona (resumen)
- **Aislamiento:** al registrarse se crean los tres espacios del usuario. Toda consulta filtra por dueño, así que un
  usuario nunca ve datos de otro y los espacios de un mismo usuario no se mezclan entre sí.
- **Reglas** (`backend/apps/rules/engine.py`):
  - *Universitario:* si el total mensual supera el presupuesto → «Presupuesto académico excedido».
  - *Negocio:* categoría deducible → «Solicite factura…»; si no → «Gasto no deducible».
  - *Personal:* sin reglas.
  - Las categorías deducibles se editan en `backend/apps/rules/catalog.py`.
- **Dashboard:** total mensual (los pagos anuales se dividen entre 12), gasto por categoría, próximos cortes
  (30 días), proyección a 12 meses y alertas, todo calculado con los datos del espacio activo.
- **Backup manual:** pantalla *Respaldos* → crea un JSON con tus espacios y pagos; restaurar guarda antes un respaldo
  de seguridad. Los archivos se guardan en `backend/backups/` (variable `BACKUP_DIR`).

## API principal
| Método | Ruta |
|---|---|
| POST | `/api/auth/register/` · `/api/auth/login/` · `/api/auth/refresh/` · `/api/auth/logout/` |
| GET | `/api/auth/me/` · `/api/workspaces/` · `/api/categories/` |
| GET/POST/PUT/PATCH/DELETE | `/api/workspaces/{id}/expenses/` y `/api/workspaces/{id}/expenses/{gasto}/` |
| GET | `/api/workspaces/{id}/dashboard/` |
| GET/POST | `/api/backups/` · POST `/api/backups/{nombre}/restore/` |

## Pruebas
```bash
cd backend
python -m unittest discover -s tests -t .   # reglas y cálculos (no requiere instalar nada)
python manage.py test                       # además, pruebas de API (requiere requirements.txt)
```

## Variables de entorno (opcionales)
| Variable | Por defecto | Uso |
|---|---|---|
| `POSTGRES_HOST` | *(vacío → SQLite)* | Si se define, se usa PostgreSQL |
| `POSTGRES_DB` / `POSTGRES_USER` / `POSTGRES_PASSWORD` | `taxsub` / `tax` / `tax` | Credenciales de PostgreSQL |
| `DJANGO_SECRET_KEY` | clave de desarrollo | Cámbiala fuera de la demo |
| `DJANGO_DEBUG` | `1` | `0` para producción |
| `BACKUP_DIR` | `backend/backups` | Carpeta de respaldos |
| `VITE_API_PROXY` | `http://localhost:8000` | A dónde proxea Vite las peticiones `/api` |

## Problemas frecuentes
- **«No se pudo conectar con el servidor»** → el backend no está corriendo (Terminal 1).
- **`ModuleNotFoundError: django`** → falta activar el entorno virtual o correr `pip install -r requirements.txt`.
- **Puerto ocupado** → `python manage.py runserver 8001` y `VITE_API_PROXY=http://localhost:8001 npm run dev`.
- Si `python manage.py makemigrations` detecta cambios tras editar un modelo, genera y **commitea** la nueva migración.

## Flujo de trabajo en equipo (sugerido)
1. `main` siempre debe correr. Cada quien trabaja en una rama (`feature/...`) y abre Pull Request.
2. Antes de subir: `python -m unittest discover -s tests -t .` y probar la pantalla que tocaste.
3. Commits pequeños y en español, p. ej. `feat(gastos): validar monto positivo`.
