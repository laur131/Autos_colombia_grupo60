from fastapi import APIRouter, Depends
from ..deps import get_conn, usuario_actual
from ..schemas import LoginIn
from ..services import auth

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login")
def login(datos: LoginIn, conn=Depends(get_conn)):
    return auth.login(conn, datos.documento, datos.password)


@router.get("/me")
def me(u=Depends(usuario_actual)):
    return u
