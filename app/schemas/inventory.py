from pydantic import BaseModel
from typing import Optional
from datetime import date

from app.schemas.types import OptionalDate


class InventoryCreate(BaseModel):
    fecha: date
    nombre: str
    precio: float
    cantidad: int
    pago: str


class InventoryUpdate(BaseModel):
    fecha: OptionalDate = None
    nombre: Optional[str] = None
    precio: Optional[float] = None
    cantidad: Optional[int] = None
    pago: Optional[str] = None


class InventoryResponse(InventoryCreate):
    id: int

    model_config = {"from_attributes": True}


class StockResponse(BaseModel):
    nombre: str
    cantidad: int
    precio: float
    ultima_fecha: Optional[date] = None
