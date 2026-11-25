import os
from datetime import datetime
try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("America/Bogota")
except Exception:  # sin tzdata (p. ej. Windows): hora local del servidor
    TZ = None

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.getenv("AUTOS_DB", os.path.join(BASE, "autos_colombia.db"))
SECRET = os.getenv("AUTOS_SECRET", "cambiar-esta-clave-en-produccion")
TOKEN_HORAS = 8
MAX_INTENTOS = 5
BLOQUEO_MIN = 15
PBKDF2_ITER = 120_000


def ahora() -> datetime:
    return datetime.now(TZ).replace(tzinfo=None, microsecond=0)


def ahora_str() -> str:
    return ahora().isoformat(timespec="seconds")


def hoy_str() -> str:
    return ahora().date().isoformat()
