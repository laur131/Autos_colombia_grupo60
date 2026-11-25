import sqlite3
from .. import repositories as repo
from ..config import ahora_str, hoy_str
from ..db import transaction
from ..errors import DomainError
from .titulares import norm_placa
from .celdas import CAT


def ocupacion(conn) -> dict:  # RF-07 / HU-03
    res = {}
    for cat, key in (("CARRO", "carros"), ("MOTO", "motos")):
        oc, cap = repo.contar_abiertos(conn, cat), repo.config_get(conn, CAT[cat])
        res[key] = {"ocupados": oc, "capacidad": cap, "libres": max(cap - oc, 0),
                    "porcentaje": round(100 * oc / cap, 1) if cap else 100.0, "lleno": oc >= cap}
    res["estancias"] = repo.mov_abiertos(conn)
    return res


def registrar_ingreso(conn, placa: str, observacion: str | None, operario_id: int) -> dict:
    """RF-01..06 (HU-01). Todas las validaciones y la escritura ocurren en una sola transacción."""
    placa = norm_placa(placa)
    with transaction(conn):
        v = repo.vehiculo_por_placa(conn, placa)
        if not v:
            raise DomainError(404, "VEHICULO_NO_ENCONTRADO", "No existe un vehículo con esa placa")
        if v["titular_estado"] != "ACTIVO" or v["estado"] != "ACTIVO":  # RF-02
            raise DomainError(409, "TITULAR_INACTIVO", "El titular o el vehículo están inactivos")
        if not repo.mensualidad_vigente(conn, v["id"], hoy_str()):  # RF-03
            raise DomainError(409, "MENSUALIDAD_VENCIDA", "La mensualidad está vencida o no existe")
        if repo.mov_abierto_por_vehiculo(conn, v["id"]):  # RF-06
            raise DomainError(409, "MOVIMIENTO_DUPLICADO", "El vehículo ya tiene un movimiento abierto")
        if repo.contar_abiertos(conn, v["tipo"]) >= repo.config_get(conn, CAT[v["tipo"]]):  # RF-04
            raise DomainError(409, "SOBRECUPO", f"No hay cupo disponible para {v['tipo'].lower()}s")
        celda = repo.celda_libre(conn, v["tipo"])  # RF-29
        if not celda:
            raise DomainError(409, "SIN_CELDA_DISPONIBLE", "No hay una celda libre y compatible")
        try:
            mid = repo.insertar(conn, "movimiento", {  # RF-05
                "vehiculo_id": v["id"], "celda_id": celda["id"], "fecha_entrada": ahora_str(),
                "operario_id": operario_id, "observacion_entrada": (observacion or "").strip() or None})
        except sqlite3.IntegrityError:
            raise DomainError(409, "MOVIMIENTO_DUPLICADO", "El vehículo ya tiene un movimiento abierto")
        repo.actualizar(conn, "celda", celda["id"], {"estado_ocupacion": "OCUPADA"})
    return repo.mov_por_id(conn, mid)


def buscar_abierto(conn, placa: str) -> dict:  # RF-08
    m = repo.mov_abierto_por_placa(conn, norm_placa(placa))
    if not m:
        raise DomainError(404, "SIN_ENTRADA_ABIERTA", "No hay una estancia abierta para esa placa")
    return m


def registrar_salida(conn, placa: str, observacion: str, operario_cierre_id: int) -> dict:  # RF-09 (HU-02)
    if not observacion or not observacion.strip():
        raise DomainError(400, "OBSERVACION_REQUERIDA", "Debes registrar la novedad de entrega")
    with transaction(conn):
        m = repo.mov_abierto_por_placa(conn, norm_placa(placa))
        if not m:
            raise DomainError(404, "SIN_ENTRADA_ABIERTA", "No hay una estancia abierta para esa placa")
        repo.actualizar(conn, "movimiento", m["id"], {
            "fecha_salida": ahora_str(), "operario_cierre_id": operario_cierre_id,
            "observacion_salida": observacion.strip(), "estado": "CERRADO"})
        repo.actualizar(conn, "celda", m["celda_id"], {"estado_ocupacion": "LIBRE"})  # RN-06
    return repo.mov_por_id(conn, m["id"])


def historial(conn, **f) -> list[dict]:  # RF-11 / HU-04
    return repo.mov_historial(conn, **f)


def agregar_novedad(conn, mov_id: int, descripcion: str, usuario_id: int) -> dict:  # RF-13
    if not repo.mov_por_id(conn, mov_id):
        raise DomainError(404, "MOVIMIENTO_NO_ENCONTRADO", "Movimiento no encontrado")
    id_ = repo.insertar(conn, "novedad", {"movimiento_id": mov_id, "descripcion": descripcion.strip(),
                                          "fecha": ahora_str(), "usuario_id": usuario_id})
    return {"id": id_, "movimiento_id": mov_id, "descripcion": descripcion.strip()}


def listar_novedades(conn, mov_id: int):
    return repo.novedades_de(conn, mov_id)
