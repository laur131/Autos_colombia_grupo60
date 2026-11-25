from datetime import date
from typing import Literal, Optional
from pydantic import BaseModel, Field

Estado = Literal["ACTIVO", "INACTIVO"]
Categoria = Literal["CARRO", "MOTO"]


class LoginIn(BaseModel):
    documento: str = Field(min_length=3, max_length=20)
    password: str = Field(min_length=1, max_length=100)


class UsuarioIn(BaseModel):
    nombre: str = Field(min_length=3, max_length=80)
    documento: str = Field(min_length=5, max_length=15)
    telefono: Optional[str] = Field(None, max_length=20)
    password: str = Field(min_length=8, max_length=100)
    rol_id: int


class UsuarioUpd(BaseModel):
    nombre: Optional[str] = Field(None, min_length=3, max_length=80)
    telefono: Optional[str] = Field(None, max_length=20)
    rol_id: Optional[int] = None
    password: Optional[str] = Field(None, min_length=8, max_length=100)


class PermisosIn(BaseModel):
    permisos: list[str]


class TitularIn(BaseModel):
    nombres: str = Field(min_length=2, max_length=60)
    apellidos: str = Field(min_length=2, max_length=60)
    documento: str = Field(min_length=5, max_length=15)
    telefono: Optional[str] = Field(None, max_length=20)


class TitularUpd(BaseModel):
    nombres: Optional[str] = Field(None, min_length=2, max_length=60)
    apellidos: Optional[str] = Field(None, min_length=2, max_length=60)
    telefono: Optional[str] = Field(None, max_length=20)


class VehiculoIn(BaseModel):
    placa: str = Field(min_length=6, max_length=7)
    tipo: Categoria
    marca: Optional[str] = Field(None, max_length=40)
    color: Optional[str] = Field(None, max_length=30)
    titular_id: int


class VehiculoUpd(BaseModel):
    marca: Optional[str] = None
    color: Optional[str] = None
    titular_id: Optional[int] = None
    estado: Optional[Estado] = None


class MensualidadIn(BaseModel):
    vehiculo_id: int
    fecha_inicio: date
    fecha_fin: date
    valor: float = Field(0, ge=0)


class IngresoIn(BaseModel):
    placa: str = Field(min_length=6, max_length=7)
    observacion: Optional[str] = Field(None, max_length=500)


class SalidaIn(BaseModel):
    placa: str = Field(min_length=6, max_length=7)
    observacion: str = Field(min_length=1, max_length=500)


class NovedadIn(BaseModel):
    descripcion: str = Field(min_length=1, max_length=500)


class CeldaIn(BaseModel):
    codigo: str = Field(min_length=1, max_length=10)
    categoria: Categoria


class CeldaUpd(BaseModel):
    codigo: Optional[str] = Field(None, min_length=1, max_length=10)
    categoria: Optional[Categoria] = None


class CeldaEstadoIn(BaseModel):
    estado: Literal["LIBRE", "BLOQUEADA"]


class CapacidadIn(BaseModel):
    capacidad_carros: int = Field(ge=0, le=10000)
    capacidad_motos: int = Field(ge=0, le=10000)


class PagoIn(BaseModel):
    movimiento_id: int
    valor: float = Field(gt=0)
