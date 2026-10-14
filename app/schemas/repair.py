from datetime import date
from pydantic import BaseModel
from typing import Optional


class RepairCreate(BaseModel):
    auto: str
    marca: str
    modelo: str
    nombres: str
    apellidos: str
    tipo_documento: str = "CC"
    numero_documento: str
    tipo_reparacion: str
    descripcion: Optional[str] = None
    fotos: Optional[str] = None
    costo: float = 0
    metodo_pago: Optional[str] = None
    fecha_entrega: date
    estado: str = "pendiente"


class RepairUpdate(BaseModel):
    auto: Optional[str] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    tipo_documento: Optional[str] = None
    numero_documento: Optional[str] = None
    tipo_reparacion: Optional[str] = None
    descripcion: Optional[str] = None
    fotos: Optional[str] = None
    costo: Optional[float] = None
    metodo_pago: Optional[str] = None
    fecha_entrega: Optional[date] = None
    estado: Optional[str] = None


class RepairResponse(RepairCreate):
    id: int
    user_id: int = 0

    model_config = {"from_attributes": True}


class RepairPartCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    cantidad: int = 0
    precio_costo: float = 0
    precio_venta: float = 0
    proveedor: Optional[str] = None


class RepairPartUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    cantidad: Optional[int] = None
    precio_costo: Optional[float] = None
    precio_venta: Optional[float] = None
    proveedor: Optional[str] = None


class RepairPartResponse(RepairPartCreate):
    id: int
    user_id: int = 0

    model_config = {"from_attributes": True}
