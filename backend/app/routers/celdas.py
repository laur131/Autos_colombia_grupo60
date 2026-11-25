from typing import Optional
from fastapi import APIRouter, Depends
from ..deps import get_conn, requiere
from ..schemas import CeldaIn, CeldaUpd, CeldaEstadoIn, CapacidadIn
from ..services import celdas as svc

router = APIRouter(prefix="/api/v1/celdas", tags=["celdas"])
ver, gestionar, configurar = requiere("celdas.consultar"), requiere("celdas.gestionar"), requiere("celdas.configurar")


@router.get("")
def listar(categoria: Optional[str] = None, estado: Optional[str] = None, activa: Optional[bool] = None,
           conn=Depends(get_conn), _=Depends(ver)):
    return svc.listar(conn, categoria=categoria, estado=estado, activa=activa)


@router.post("", status_code=201)
def crear(d: CeldaIn, conn=Depends(get_conn), _=Depends(gestionar)):
    return svc.crear(conn, d.model_dump())


# las rutas fijas van antes de /{id_}
@router.get("/configuracion")
def ver_configuracion(conn=Depends(get_conn), _=Depends(ver)):
    return svc.obtener_capacidad(conn)


@router.put("/configuracion")
def configurar_capacidad(d: CapacidadIn, conn=Depends(get_conn), _=Depends(configurar)):
    return svc.configurar_capacidad(conn, d.capacidad_carros, d.capacidad_motos)


@router.get("/{id_}")
def obtener(id_: int, conn=Depends(get_conn), _=Depends(ver)):
    return svc.obtener(conn, id_)


@router.put("/{id_}")
def actualizar(id_: int, d: CeldaUpd, conn=Depends(get_conn), _=Depends(gestionar)):
    return svc.actualizar(conn, id_, d.model_dump())


@router.patch("/{id_}/estado")
def estado(id_: int, d: CeldaEstadoIn, conn=Depends(get_conn), _=Depends(gestionar)):
    return svc.cambiar_estado(conn, id_, d.estado)


@router.patch("/{id_}/inactivar")
def inactivar(id_: int, conn=Depends(get_conn), _=Depends(gestionar)):
    return svc.cambiar_activa(conn, id_, False)


@router.patch("/{id_}/reactivar")
def reactivar(id_: int, conn=Depends(get_conn), _=Depends(gestionar)):
    return svc.cambiar_activa(conn, id_, True)
