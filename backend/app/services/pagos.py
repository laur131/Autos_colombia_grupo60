import sqlite3
from .. import repositories as repo
from ..config import ahora_str
from ..errors import DomainError


def registrar(conn, movimiento_id: int, valor: float, usuario_id: int) -> dict:
    if not repo.mov_por_id(conn, movimiento_id):
        raise DomainError(404, "MOVIMIENTO_NO_ENCONTRADO", "Movimiento no encontrado")
    try:
        id_ = repo.insertar(conn, "pago", {"movimiento_id": movimiento_id, "usuario_id": usuario_id,
                                           "valor": valor, "fecha": ahora_str()})
    except sqlite3.IntegrityError:
        raise DomainError(409, "PAGO_DUPLICADO", "El movimiento ya tiene un pago registrado")
    return {"id": id_, "movimiento_id": movimiento_id, "valor": valor}


def listar(conn):
    return repo.pagos_listar(conn)
