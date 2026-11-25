import sqlite3
from .. import repositories as repo
from ..db import transaction
from ..errors import DomainError

CAT = {"CARRO": "capacidad_carros", "MOTO": "capacidad_motos"}


def _norm(codigo: str) -> str:
    return codigo.strip().upper()


def obtener(conn, id_: int) -> dict:
    c = repo.celda_por_id(conn, id_)
    if not c:
        raise DomainError(404, "CELDA_NO_ENCONTRADA", "Celda no encontrada")
    return c


def listar(conn, **f):  # RF-27
    return repo.celdas_listar(conn, **f)


def crear(conn, d: dict) -> dict:  # RF-26 / RN-04
    codigo = _norm(d["codigo"])
    try:
        id_ = repo.insertar(conn, "celda", {"codigo": codigo, "categoria": d["categoria"]})
    except sqlite3.IntegrityError:
        raise DomainError(409, "CODIGO_DUPLICADO", "El código de la celda ya existe")
    return repo.celda_por_id(conn, id_)


def actualizar(conn, id_: int, d: dict) -> dict:  # RF-27
    c = obtener(conn, id_)
    if c["estado_ocupacion"] == "OCUPADA":
        raise DomainError(409, "CELDA_OCUPADA", "No se puede modificar una celda ocupada")
    campos = {}
    if d.get("codigo"):
        campos["codigo"] = _norm(d["codigo"])
    if d.get("categoria"):
        campos["categoria"] = d["categoria"]
    try:
        with transaction(conn):
            repo.actualizar(conn, "celda", id_, campos)
    except sqlite3.IntegrityError:
        raise DomainError(409, "CODIGO_DUPLICADO", "El código de la celda ya existe")
    return obtener(conn, id_)


def cambiar_estado(conn, id_: int, estado: str) -> dict:
    """Bloqueo manual (mantenimiento) o liberación. OCUPADA solo la fija el sistema al registrar el ingreso."""
    with transaction(conn):
        c = obtener(conn, id_)
        if not c["activa"]:
            raise DomainError(409, "CELDA_INACTIVA", "La celda está inactiva")
        if c["estado_ocupacion"] == "OCUPADA":
            raise DomainError(409, "CELDA_OCUPADA", "La celda tiene un vehículo asignado")
        repo.actualizar(conn, "celda", id_, {"estado_ocupacion": estado})
    return obtener(conn, id_)


def cambiar_activa(conn, id_: int, activa: bool) -> dict:
    """RF-28 / RN-05 / RN-07: no se inactiva una celda ocupada y nunca se elimina."""
    with transaction(conn):
        c = obtener(conn, id_)
        if not activa and c["estado_ocupacion"] == "OCUPADA":
            raise DomainError(409, "CELDA_OCUPADA", "No se puede inactivar una celda con vehículo asignado")
        repo.actualizar(conn, "celda", id_, {"activa": 1 if activa else 0})
    return obtener(conn, id_)


def obtener_capacidad(conn) -> dict:
    return {"capacidad_carros": repo.config_get(conn, "capacidad_carros"),
            "capacidad_motos": repo.config_get(conn, "capacidad_motos")}


def configurar_capacidad(conn, carros: int, motos: int) -> dict:  # RF-22 / HU-09
    with transaction(conn):
        for cat, nuevo in (("CARRO", carros), ("MOTO", motos)):
            en_uso = repo.contar_abiertos(conn, cat)
            if nuevo < en_uso:
                raise DomainError(409, "CAPACIDAD_MENOR_OCUPACION",
                                  f"No se permite un valor inferior a {en_uso} ({cat.lower()}s en uso)")
        repo.config_set(conn, "capacidad_carros", carros)
        repo.config_set(conn, "capacidad_motos", motos)
    return obtener_capacidad(conn)
