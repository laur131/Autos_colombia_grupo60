from typing import Optional
from fastapi import APIRouter, Depends
from ..deps import get_conn, requiere
from ..schemas import TitularIn, TitularUpd, VehiculoIn, VehiculoUpd, MensualidadIn
from ..services import titulares as svc

router = APIRouter(prefix="/api/v1", tags=["titulares y vehículos"])
gestion = requiere("titulares.gestionar")


@router.get("/titulares")
def listar(estado: Optional[str] = None, q: Optional[str] = None, conn=Depends(get_conn), _=Depends(gestion)):
    return svc.listar_titulares(conn, estado=estado, q=q)


@router.post("/titulares", status_code=201)
def crear(d: TitularIn, conn=Depends(get_conn), _=Depends(gestion)):
    return svc.crear_titular(conn, d.model_dump())


@router.get("/titulares/{id_}")
def obtener(id_: int, conn=Depends(get_conn), _=Depends(gestion)):
    return svc.obtener_titular(conn, id_)


@router.put("/titulares/{id_}")
def actualizar(id_: int, d: TitularUpd, conn=Depends(get_conn), _=Depends(gestion)):
    return svc.actualizar_titular(conn, id_, d.model_dump())


@router.patch("/titulares/{id_}/inactivar")
def inactivar(id_: int, conn=Depends(get_conn), _=Depends(gestion)):
    return svc.cambiar_estado_titular(conn, id_, "INACTIVO")


@router.patch("/titulares/{id_}/reactivar")
def reactivar(id_: int, conn=Depends(get_conn), _=Depends(gestion)):
    return svc.cambiar_estado_titular(conn, id_, "ACTIVO")


@router.get("/vehiculos")
def vehiculos(titular_id: Optional[int] = None, conn=Depends(get_conn), _=Depends(gestion)):
    return svc.listar_vehiculos(conn, titular_id)


@router.post("/vehiculos", status_code=201)
def crear_vehiculo(d: VehiculoIn, conn=Depends(get_conn), _=Depends(gestion)):
    return svc.crear_vehiculo(conn, d.model_dump())


@router.get("/vehiculos/{placa}")
def consultar(placa: str, conn=Depends(get_conn), _=Depends(requiere("vehiculos.consultar"))):
    return svc.consultar_vehiculo(conn, placa)


@router.put("/vehiculos/{id_}")
def actualizar_vehiculo(id_: int, d: VehiculoUpd, conn=Depends(get_conn), _=Depends(gestion)):
    return svc.actualizar_vehiculo(conn, id_, d.model_dump())


@router.post("/mensualidades", status_code=201)
def mensualidad(d: MensualidadIn, conn=Depends(get_conn), _=Depends(gestion)):
    return svc.crear_mensualidad(conn, d.model_dump())
