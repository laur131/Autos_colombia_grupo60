from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .db import connect, init_db
from .errors import DomainError
from .seed import seed
from .routers import auth, usuarios, titulares, celdas, movimientos


@asynccontextmanager
async def lifespan(_: FastAPI):
    conn = connect()
    init_db(conn)
    seed(conn)
    conn.close()
    yield


app = FastAPI(title="Autos Colombia - API", version="2.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:4200"], allow_methods=["*"], allow_headers=["*"])


@app.exception_handler(DomainError)
async def domain_error_handler(_, exc: DomainError):
    return JSONResponse(status_code=exc.status, content={"detail": {"codigo": exc.codigo, "mensaje": exc.mensaje}})


for r in (auth.router, usuarios.router, titulares.router, celdas.router, movimientos.router):
    app.include_router(r)


@app.get("/api/v1/salud", tags=["sistema"])
def salud():
    return {"estado": "ok"}
