from datetime import datetime, timedelta
from .. import repositories as repo, security
from ..config import ahora, ahora_str, MAX_INTENTOS, BLOQUEO_MIN
from ..errors import DomainError


def login(conn, documento: str, password: str) -> dict:
    """RF-23. Credenciales incorrectas o cuenta inactiva => acceso denegado y NO se genera token."""
    cred = DomainError(401, "CREDENCIALES_INVALIDAS", "Documento o contraseña incorrectos")
    u = repo.usuario_auth_por_documento(conn, documento.strip())
    if not u:
        raise cred
    if u["bloqueado_hasta"] and datetime.fromisoformat(u["bloqueado_hasta"]) > ahora():
        raise DomainError(403, "CUENTA_BLOQUEADA", f"Cuenta bloqueada {BLOQUEO_MIN} min por intentos fallidos")
    if not security.verificar(password, u["password_hash"]):
        n = u["intentos_fallidos"] + 1
        if n >= MAX_INTENTOS:
            hasta = (ahora() + timedelta(minutes=BLOQUEO_MIN)).isoformat(timespec="seconds")
            repo.actualizar(conn, "usuario", u["id"], {"intentos_fallidos": 0, "bloqueado_hasta": hasta})
        else:
            repo.actualizar(conn, "usuario", u["id"], {"intentos_fallidos": n})
        raise cred
    if u["estado_cuenta"] != "ACTIVO":
        raise DomainError(403, "CUENTA_INACTIVA", "La cuenta está inactiva")
    repo.actualizar(conn, "usuario", u["id"], {"intentos_fallidos": 0, "bloqueado_hasta": None, "ultimo_acceso": ahora_str()})
    return {"access_token": security.crear_token(u["id"], u["rol"]), "token_type": "bearer",
            "usuario": {"id": u["id"], "nombre": u["nombre"], "documento": u["documento"], "rol": u["rol"]},
            "permisos": repo.permisos_de_rol(conn, u["rol_id"])}


def usuario_actual(conn, usuario_id: int) -> dict:
    """Se consulta en cada petición: si se inactiva la cuenta o cambian los permisos, aplica de inmediato."""
    u = repo.usuario_por_id(conn, usuario_id)
    if not u or u["estado_cuenta"] != "ACTIVO":
        raise DomainError(401, "SESION_INVALIDA", "La sesión ya no es válida")
    u["permisos"] = repo.permisos_de_rol(conn, u["rol_id"])
    return u
