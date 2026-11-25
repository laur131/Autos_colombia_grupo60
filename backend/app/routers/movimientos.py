from typing import Optional
from fastapi import APIRouter, Depends
from ..deps import get_conn, requiere
from ..schemas import IngresoIn, SalidaIn, NovedadIn, PagoIn
from ..services import movimientos as svc, pagos as pagos_svc

router = APIRouter(prefix="/api/v1", tags=["movimientos y pagos"])
operar = requiere("movimientos.registrar")


@router.get("/movimientos/ocupacion")
def ocupacion(conn=Depends(get_conn), _=Depends(requiere("tablero.ver"))):
    return svc.ocupacion(conn)


@router.post("/movimientos/ingresos", status_code=201)
def ingreso(d: IngresoIn, conn=Depends(get_conn), u=Depends(operar)):
    return svc.registrar_ingreso(conn, d.placa, d.observacion, u["id"])


@router.get("/movimientos/abiertos/{placa}")
def abierto(placa: str, conn=Depends(get_conn), _=Depends(operar)):
    return svc.buscar_abierto(conn, placa)


@router.post("/movimientos/salidas")
def salida(d: SalidaIn, conn=Depends(get_conn), u=Depends(operar)):
    return svc.registrar_salida(conn, d.placa, d.observacion, u["id"])


@router.get("/movimientos")
def historial(placa: Optional[str] = None, desde: Optional[str] = None, hasta: Optional[str] = None,
              estado: Optional[str] = None, conn=Depends(get_conn), _=Depends(requiere("historial.consultar"))):
    return svc.historial(conn, placa=placa, desde=desde, hasta=hasta, estado=estado)


@router.post("/movimientos/{mov_id}/novedades", status_code=201)
def novedad(mov_id: int, d: NovedadIn, conn=Depends(get_conn), u=Depends(requiere("novedades.registrar"))):
    return svc.agregar_novedad(conn, mov_id, d.descripcion, u["id"])


@router.get("/movimientos/{mov_id}/novedades")
def novedades(mov_id: int, conn=Depends(get_conn), _=Depends(requiere("novedades.registrar"))):
    return svc.listar_novedades(conn, mov_id)


@router.post("/pagos", status_code=201)
def pago(d: PagoIn, conn=Depends(get_conn), u=Depends(requiere("pagos.registrar"))):
    return pagos_svc.registrar(conn, d.movimiento_id, d.valor, u["id"])


@router.get("/pagos")
def pagos(conn=Depends(get_conn), _=Depends(requiere("pagos.registrar"))):
    return pagos_svc.listar(conn)
