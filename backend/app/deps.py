from fastapi import Depends, Header
from .db import connect
from .errors import DomainError
from . import security
from .services import auth as auth_svc


def get_conn():
    conn = connect()
    try:
        yield conn
    finally:
        conn.close()


def usuario_actual(authorization: str | None = Header(None), conn=Depends(get_conn)) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise DomainError(401, "NO_AUTENTICADO", "Debes iniciar sesión")
    datos = security.leer_token(authorization[7:])
    return auth_svc.usuario_actual(conn, int(datos["sub"]))


def requiere(permiso: str):
    """RF-25 / RN-02 / RN-03: las operaciones disponibles dependen de los permisos del rol."""
    def dependencia(u: dict = Depends(usuario_actual)) -> dict:
        if permiso not in u["permisos"]:
            raise DomainError(403, "SIN_PERMISO", "Tu rol no tiene permiso para esta operación")
        return u
    return dependencia
