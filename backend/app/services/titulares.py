import re, sqlite3
from .. import repositories as repo
from ..config import hoy_str
from ..db import transaction
from ..errors import DomainError

PLACA = {"CARRO": re.compile(r"^[A-Z]{3}\d{3}$"), "MOTO": re.compile(r"^[A-Z]{3}\d{2}[A-Z]$")}


def norm_placa(p: str) -> str:
    return p.strip().upper().replace("-", "").replace(" ", "")


# ---------- titulares (RF-15, RF-18, HU-06) ----------
def crear_titular(conn, d: dict) -> dict:
    try:
        id_ = repo.insertar(conn, "titular", {"nombres": d["nombres"].strip(), "apellidos": d["apellidos"].strip(),
                                              "documento": d["documento"].strip(), "telefono": d.get("telefono")})
    except sqlite3.IntegrityError:
        raise DomainError(409, "DOCUMENTO_DUPLICADO", "El documento ya está registrado")  # HU-06 criterio 1
    return repo.titular_por_id(conn, id_)


def obtener_titular(conn, id_: int) -> dict:
    t = repo.titular_por_id(conn, id_)
    if not t:
        raise DomainError(404, "TITULAR_NO_ENCONTRADO", "Titular no encontrado")
    return t


def actualizar_titular(conn, id_: int, d: dict) -> dict:
    obtener_titular(conn, id_)
    with transaction(conn):
        repo.actualizar(conn, "titular", id_, {k: v for k, v in d.items() if v is not None})
    return obtener_titular(conn, id_)


def cambiar_estado_titular(conn, id_: int, estado: str) -> dict:
    """Baja lógica: un titular INACTIVO bloquea el ingreso de todos sus vehículos (HU-06 criterio 2)."""
    obtener_titular(conn, id_)
    with transaction(conn):
        repo.actualizar(conn, "titular", id_, {"estado": estado})
    return obtener_titular(conn, id_)


def listar_titulares(conn, **f):
    return repo.titulares_listar(conn, **f)


# ---------- vehículos (RF-19, HU-08) ----------
def crear_vehiculo(conn, d: dict) -> dict:
    placa, tipo = norm_placa(d["placa"]), d["tipo"]
    if not PLACA[tipo].match(placa):
        raise DomainError(422, "PLACA_INVALIDA", "Formato de placa inválido (carro: ABC123, moto: ABC12D)")
    t = obtener_titular(conn, d["titular_id"])
    if t["estado"] != "ACTIVO":
        raise DomainError(409, "TITULAR_INACTIVO", "No se puede vincular un vehículo a un titular inactivo")
    try:
        id_ = repo.insertar(conn, "vehiculo", {"placa": placa, "tipo": tipo, "marca": d.get("marca"),
                                               "color": d.get("color"), "titular_id": t["id"]})
    except sqlite3.IntegrityError:
        raise DomainError(409, "PLACA_DUPLICADA", "La placa ya está registrada")
    return repo.vehiculo_por_id(conn, id_)


def consultar_vehiculo(conn, placa: str) -> dict:  # RF-01
    v = repo.vehiculo_por_placa(conn, norm_placa(placa))
    if not v:
        raise DomainError(404, "VEHICULO_NO_ENCONTRADO", "No existe un vehículo con esa placa")
    v["mensualidad"] = repo.mensualidad_vigente(conn, v["id"], hoy_str())
    return v


def actualizar_vehiculo(conn, id_: int, d: dict) -> dict:
    v = repo.vehiculo_por_id(conn, id_)
    if not v:
        raise DomainError(404, "VEHICULO_NO_ENCONTRADO", "Vehículo no encontrado")
    campos = {k: d[k] for k in ("marca", "color", "estado") if d.get(k) is not None}
    if d.get("titular_id") is not None:
        campos["titular_id"] = obtener_titular(conn, d["titular_id"])["id"]
    with transaction(conn):
        repo.actualizar(conn, "vehiculo", id_, campos)
    return repo.vehiculo_por_id(conn, id_)


def listar_vehiculos(conn, titular_id=None):
    return repo.vehiculos_listar(conn, titular_id)


def crear_mensualidad(conn, d: dict) -> dict:
    v = repo.vehiculo_por_id(conn, d["vehiculo_id"])
    if not v:
        raise DomainError(404, "VEHICULO_NO_ENCONTRADO", "Vehículo no encontrado")
    ini, fin = str(d["fecha_inicio"]), str(d["fecha_fin"])
    if fin < ini:
        raise DomainError(422, "FECHAS_INVALIDAS", "fecha_fin no puede ser anterior a fecha_inicio")
    id_ = repo.insertar(conn, "mensualidad", {"vehiculo_id": v["id"], "fecha_inicio": ini, "fecha_fin": fin,
                                              "valor": d.get("valor", 0)})
    return {"id": id_, "vehiculo_id": v["id"], "fecha_inicio": ini, "fecha_fin": fin, "valor": d.get("valor", 0)}
