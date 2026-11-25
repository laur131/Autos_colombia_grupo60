# Autos Colombia · Control de Parqueadero (Iteración 2)

Sistema de información del parqueadero **Autos Colombia**: ingreso/salida de vehículos, gestión de usuarios
(titulares y personal), roles y permisos, gestión de celdas individuales y aforo.

**Stack:** FastAPI (router → servicios → repositorios) · SQLite · Angular 18 (standalone) · JWT.

## Ejecutar

### Backend (http://localhost:8000, docs en /docs)
```bash
cd backend
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
La primera ejecución crea `autos_colombia.db` con datos de demostración (70 celdas de carro, 10 de moto, titulares y movimientos).

### Frontend (http://localhost:4200)
```bash
cd frontend
npm install
npm start
```

### Pruebas
```bash
cd backend
python -m unittest -v      # lógica de negocio (no necesita servidor)
pytest                     # además corre las pruebas de la API
```

## Cuentas de demostración
| Rol | Documento | Contraseña |
|---|---|---|
| Administrador (Héctor Niño, ID 101) | 80123456 | Admin2026* |
| Operario (Laura Jaramillo, ID 102) | 1032987654 | Operario2026* |
| Operario (Arley Franco, ID 103) | 52741963 | Operario2026* |

Placas de prueba: `XYZ789` (válida), `INA404` (titular inactivo), `VEN999` (mensualidad vencida),
`ABC123` (ya está adentro), `MOT88A` (moto válida). El identificador de acceso es el **documento**.

## Trazabilidad requerimiento → código
| Requerimiento | Dónde |
|---|---|
| RF-01, RF-02, RF-03, RF-04, RF-05, RF-06, RF-29 | `services/movimientos.py::registrar_ingreso` (una transacción `BEGIN IMMEDIATE`) |
| RF-07 | `GET /api/v1/movimientos/ocupacion` |
| RF-08, RF-09, RN-06 | `buscar_abierto`, `registrar_salida` (guarda `operario_cierre_id`, libera la celda) |
| RF-11 | `GET /api/v1/movimientos` (filtros placa, fechas, estado) |
| RF-13 | `POST /api/v1/movimientos/{id}/novedades` |
| RF-15, RF-18 | `/api/v1/titulares` (+ `/inactivar`, `/reactivar`) |
| RF-16, RF-24, RN-02 | `/api/v1/usuarios` (solo permiso `usuarios.administrar`) |
| RF-19 | `/api/v1/vehiculos` (FK a titular) |
| RF-22 | `PUT /api/v1/celdas/configuracion` (409 si baja de la ocupación actual) |
| RF-23, RN-01 | `POST /api/v1/auth/login` (hash PBKDF2, bloqueo 15 min tras 5 intentos) |
| RF-25, RN-03 | `GET /roles`, `PUT /roles/{id}/permisos` + dependencia `requiere(permiso)` |
| RF-26, RF-27, RF-28, RN-04, RN-05, RN-07 | `/api/v1/celdas` (código único, no se inactiva una celda ocupada, nunca se borra) |
| RNF-01 | Triggers SQLite: apertura y cierre inmutables, no se borran movimientos |
| RNF-03 | `BEGIN IMMEDIATE` + índices únicos parciales (`ux_mov_abierto_*`) |
| RNF-05 | `PRAGMA foreign_keys = ON` en `db.connect` |
| RNF-08 | `routers/` → `services/` → `repositories.py` |

Errores de negocio: `{"detail": {"codigo": "...", "mensaje": "..."}}` con 409 para rechazos de ingreso.

## Subir a GitHub
```bash
git init && git add . && git commit -m "Iteración 2: gestión de usuarios, roles, celdas y arquitectura ejecutable"
git branch -M main
git remote add origin https://github.com/HGNA23/autos-colombia-parqueadero.git
git push -u origin main
```
