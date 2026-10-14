from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class QuoteItem(BaseModel):
    descripcion: str
    cantidad: int = 1
    precio_unitario: float = 0


class QuoteCreate(BaseModel):
    auto: str
    marca: str
    modelo: str
    nombres: str
    apellidos: str
    tipo_documento: str = "CC"
    numero_documento: str
    tipo_reparacion: str
    descripcion: Optional[str] = None
    items: str = "[]"
    total: float = 0
    validez_dias: int = 15
    notas: Optional[str] = None
    estado: str = "pendiente"


class QuoteUpdate(BaseModel):
    auto: Optional[str] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    tipo_documento: Optional[str] = None
    numero_documento: Optional[str] = None
    tipo_reparacion: Optional[str] = None
    descripcion: Optional[str] = None
    items: Optional[str] = None
    total: Optional[float] = None
    validez_dias: Optional[int] = None
    notas: Optional[str] = None
    estado: Optional[str] = None


class QuoteResponse(QuoteCreate):
    id: int
    created_at: Optional[datetime] = None
    user_id: int = 0

    model_config = {"from_attributes": True}
