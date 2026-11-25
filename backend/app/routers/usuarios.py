from typing import Optional
from fastapi import APIRouter, Depends
from ..deps import get_conn, requiere
from ..schemas import UsuarioIn, UsuarioUpd, PermisosIn
from ..services import usuarios as svc

router = APIRouter(prefix="/api/v1", tags=["usuarios, roles y permisos"])
admin_u, admin_r = requiere("usuarios.administrar"), requiere("roles.administrar")


@router.get("/usuarios")
def listar(estado: Optional[str] = None, rol_id: Optional[int] = None, q: Optional[str] = None,
           conn=Depends(get_conn), _=Depends(admin_u)):
    return svc.listar(conn, estado=estado, rol_id=rol_id, q=q)


@router.post("/usuarios", status_code=201)
def crear(d: UsuarioIn, conn=Depends(get_conn), _=Depends(admin_u)):
    return svc.crear(conn, d.model_dump())


@router.get("/usuarios/{id_}")
def obtener(id_: int, conn=Depends(get_conn), _=Depends(admin_u)):
    return svc.obtener(conn, id_)


@router.put("/usuarios/{id_}")
def actualizar(id_: int, d: UsuarioUpd, conn=Depends(get_conn), u=Depends(admin_u)):
    return svc.actualizar(conn, id_, d.model_dump(), u["id"])


@router.patch("/usuarios/{id_}/inactivar")
def inactivar(id_: int, conn=Depends(get_conn), u=Depends(admin_u)):
    return svc.cambiar_estado(conn, id_, "INACTIVO", u["id"])


@router.patch("/usuarios/{id_}/reactivar")
def reactivar(id_: int, conn=Depends(get_conn), u=Depends(admin_u)):
    return svc.cambiar_estado(conn, id_, "ACTIVO", u["id"])


@router.get("/roles")
def roles(conn=Depends(get_conn), _=Depends(admin_r)):
    return svc.listar_roles(conn)


@router.get("/permisos")
def permisos(conn=Depends(get_conn), _=Depends(admin_r)):
    from .. import repositories as repo
    return repo.permisos_listar(conn)


@router.put("/roles/{rol_id}/permisos")
def asignar(rol_id: int, d: PermisosIn, conn=Depends(get_conn), _=Depends(admin_r)):
    return svc.asignar_permisos(conn, rol_id, d.permisos)
