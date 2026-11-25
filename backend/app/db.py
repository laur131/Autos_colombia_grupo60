import sqlite3
from contextlib import contextmanager
from .config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS rol(id INTEGER PRIMARY KEY, nombre TEXT UNIQUE NOT NULL, descripcion TEXT);
CREATE TABLE IF NOT EXISTS permiso(id INTEGER PRIMARY KEY, codigo TEXT UNIQUE NOT NULL, descripcion TEXT, modulo TEXT);
CREATE TABLE IF NOT EXISTS rol_permiso(
  rol_id INTEGER NOT NULL REFERENCES rol(id), permiso_id INTEGER NOT NULL REFERENCES permiso(id),
  PRIMARY KEY(rol_id, permiso_id));
CREATE TABLE IF NOT EXISTS usuario(
  id INTEGER PRIMARY KEY, nombre TEXT NOT NULL, documento TEXT UNIQUE NOT NULL, telefono TEXT,
  password_hash TEXT NOT NULL,
  estado_cuenta TEXT NOT NULL DEFAULT 'ACTIVO' CHECK(estado_cuenta IN ('ACTIVO','INACTIVO')),
  intentos_fallidos INTEGER NOT NULL DEFAULT 0, bloqueado_hasta TEXT, ultimo_acceso TEXT,
  rol_id INTEGER NOT NULL REFERENCES rol(id));
CREATE TABLE IF NOT EXISTS titular(
  id INTEGER PRIMARY KEY, nombres TEXT NOT NULL, apellidos TEXT NOT NULL, documento TEXT UNIQUE NOT NULL,
  telefono TEXT, estado TEXT NOT NULL DEFAULT 'ACTIVO' CHECK(estado IN ('ACTIVO','INACTIVO')));
CREATE TABLE IF NOT EXISTS vehiculo(
  id INTEGER PRIMARY KEY, placa TEXT UNIQUE NOT NULL, tipo TEXT NOT NULL CHECK(tipo IN ('CARRO','MOTO')),
  marca TEXT, color TEXT, titular_id INTEGER NOT NULL REFERENCES titular(id),
  estado TEXT NOT NULL DEFAULT 'ACTIVO' CHECK(estado IN ('ACTIVO','INACTIVO')));
CREATE TABLE IF NOT EXISTS mensualidad(
  id INTEGER PRIMARY KEY, vehiculo_id INTEGER NOT NULL REFERENCES vehiculo(id),
  fecha_inicio TEXT NOT NULL, fecha_fin TEXT NOT NULL, valor REAL NOT NULL DEFAULT 0,
  CHECK(fecha_fin >= fecha_inicio));
CREATE TABLE IF NOT EXISTS celda(
  id INTEGER PRIMARY KEY, codigo TEXT UNIQUE NOT NULL, categoria TEXT NOT NULL CHECK(categoria IN ('CARRO','MOTO')),
  estado_ocupacion TEXT NOT NULL DEFAULT 'LIBRE' CHECK(estado_ocupacion IN ('LIBRE','OCUPADA','BLOQUEADA')),
  activa INTEGER NOT NULL DEFAULT 1 CHECK(activa IN (0,1)));
CREATE TABLE IF NOT EXISTS configuracion(clave TEXT PRIMARY KEY, valor INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS movimiento(
  id INTEGER PRIMARY KEY, vehiculo_id INTEGER NOT NULL REFERENCES vehiculo(id),
  celda_id INTEGER NOT NULL REFERENCES celda(id),
  fecha_entrada TEXT NOT NULL, fecha_salida TEXT,
  operario_id INTEGER NOT NULL REFERENCES usuario(id),
  operario_cierre_id INTEGER REFERENCES usuario(id),
  observacion_entrada TEXT, observacion_salida TEXT,
  estado TEXT NOT NULL DEFAULT 'ABIERTO' CHECK(estado IN ('ABIERTO','CERRADO')));
CREATE UNIQUE INDEX IF NOT EXISTS ux_mov_abierto_vehiculo ON movimiento(vehiculo_id) WHERE estado='ABIERTO';
CREATE UNIQUE INDEX IF NOT EXISTS ux_mov_abierto_celda ON movimiento(celda_id) WHERE estado='ABIERTO';
CREATE TRIGGER IF NOT EXISTS mov_no_borrar BEFORE DELETE ON movimiento
  BEGIN SELECT RAISE(ABORT,'movimiento inmutable: no se puede borrar'); END;
CREATE TRIGGER IF NOT EXISTS mov_apertura_inmutable
  BEFORE UPDATE OF operario_id, vehiculo_id, fecha_entrada, observacion_entrada ON movimiento
  BEGIN SELECT RAISE(ABORT,'datos de apertura inmutables'); END;
CREATE TRIGGER IF NOT EXISTS mov_cierre_inmutable
  BEFORE UPDATE OF operario_cierre_id, fecha_salida ON movimiento WHEN OLD.estado='CERRADO'
  BEGIN SELECT RAISE(ABORT,'movimiento cerrado inmutable'); END;
CREATE TABLE IF NOT EXISTS novedad(
  id INTEGER PRIMARY KEY, movimiento_id INTEGER NOT NULL REFERENCES movimiento(id),
  descripcion TEXT NOT NULL, fecha TEXT NOT NULL, usuario_id INTEGER NOT NULL REFERENCES usuario(id));
CREATE TABLE IF NOT EXISTS pago(
  id INTEGER PRIMARY KEY, movimiento_id INTEGER NOT NULL UNIQUE REFERENCES movimiento(id),
  usuario_id INTEGER NOT NULL REFERENCES usuario(id), valor REAL NOT NULL CHECK(valor > 0), fecha TEXT NOT NULL);
"""


def connect(path: str | None = None) -> sqlite3.Connection:
    conn = sqlite3.connect(path or DB_PATH, isolation_level=None, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")  # RNF-05
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)


@contextmanager
def transaction(conn: sqlite3.Connection):
    """RNF-03: BEGIN IMMEDIATE toma el bloqueo de escritura desde el inicio."""
    conn.execute("BEGIN IMMEDIATE")
    try:
        yield conn
    except BaseException:
        conn.execute("ROLLBACK")
        raise
    else:
        conn.execute("COMMIT")
