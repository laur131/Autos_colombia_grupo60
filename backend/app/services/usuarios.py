import sqlite3
from .. import repositories as repo, security
from ..db import transaction
from ..errors import DomainError


def crear(conn, d: dict) -> dict:  # RF-16 / RF-24 (RN-02: solo el administrador, validado por permiso)
    if not repo.rol_por_id(conn, d["rol_id"]):
        raise DomainError(404, "ROL_NO_ENCONTRADO", "El rol no existe")
    try:
        id_ = repo.insertar(conn, "usuario", {
            "nombre": d["nombre"].strip(), "documento": d["documento"].strip(), "telefono": d.get("telefono"),
            "password_hash": security.hash_password(d["password"]), "rol_id": d["rol_id"]})
    except sqlite3.IntegrityError:
        raise DomainError(409, "DOCUMENTO_DUPLICADO", "Ya existe una cuenta con ese documento")
    return repo.usuario_por_id(conn, id_)


def obtener(conn, id_: int) -> dict:
    u = repo.usuario_por_id(conn, id_)
    if not u:
        raise DomainError(404, "USUARIO_NO_ENCONTRADO", "Cuenta no encontrada")
    return u


def actualizar(conn, id_: int, d: dict, actor_id: int) -> dict:
    u = obtener(conn, id_)
    campos = {k: d[k] for k in ("nombre", "telefono") if d.get(k) is not None}
    if d.get("rol_id") is not None:
        if not repo.rol_por_id(conn, d["rol_id"]):
            raise DomainError(404, "ROL_NO_ENCONTRADO", "El rol no existe")
        _proteger_ultimo_admin(conn, u, d["rol_id"])
        campos["rol_id"] = d["rol_id"]
    if d.get("password"):
        campos.update(password_hash=security.hash_password(d["password"]), intentos_fallidos=0, bloqueado_hasta=None)
    with transaction(conn):
        repo.actualizar(conn, "usuario", id_, campos)
    return obtener(conn, id_)


def cambiar_estado(conn, id_: int, estado: str, actor_id: int) -> dict:
    """Baja lógica (RN-07): nunca se borra, se conserva la trazabilidad."""
    u = obtener(conn, id_)
    if estado == "INACTIVO":
        if id_ == actor_id:
            raise DomainError(409, "AUTO_INACTIVACION", "No puedes inactivar tu propia cuenta")
        _proteger_ultimo_admin(conn, u, None)
    with transaction(conn):
        repo.actualizar(conn, "usuario", id_, {"estado_cuenta": estado})
    return obtener(conn, id_)


def _proteger_ultimo_admin(conn, u, nuevo_rol_id):
    es_admin = u["rol"] == "ADMINISTRADOR" and u["estado_cuenta"] == "ACTIVO"
    deja_de_serlo = nuevo_rol_id is None or repo.rol_por_id(conn, nuevo_rol_id)["nombre"] != "ADMINISTRADOR"
    if es_admin and deja_de_serlo and repo.contar_admins_activos(conn) <= 1:
        raise DomainError(409, "ULTIMO_ADMIN", "Debe existir al menos un administrador activo")


def listar(conn, **f):
    return repo.usuarios_listar(conn, **f)


# ---------- roles y permisos (RF-25) ----------
def listar_roles(conn):
    return repo.roles_listar(conn)


def asignar_permisos(conn, rol_id: int, codigos: list[str]) -> dict:
    rol = repo.rol_por_id(conn, rol_id)
    if not rol:
        raise DomainError(404, "ROL_NO_ENCONTRADO", "El rol no existe")
    validos = {p["codigo"] for p in repo.permisos_listar(conn)}
    desconocidos = set(codigos) - validos
    if desconocidos:
        raise DomainError(422, "PERMISO_DESCONOCIDO", f"Permisos inexistentes: {', '.join(sorted(desconocidos))}")
    if rol["nombre"] == "ADMINISTRADOR" and not {"roles.administrar", "usuarios.administrar"} <= set(codigos):
        raise DomainError(409, "ADMIN_SIN_ACCESO", "El administrador debe conservar la gestión de roles y usuarios")
    with transaction(conn):
        repo.asignar_permisos(conn, rol_id, sorted(set(codigos)))
    return next(r for r in repo.roles_listar(conn) if r["id"] == rol_id)
