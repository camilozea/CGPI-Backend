from pydantic import BaseModel
from typing import Optional
from datetime import date

from app.schemas.types import OptionalDate


class ReturnCreate(BaseModel):
    producto: str
    cliente: str
    fecha: date
    cantidad: int
    motivo: str
    estado: str = "pendiente"


class ReturnUpdate(BaseModel):
    producto: Optional[str] = None
    cliente: Optional[str] = None
    fecha: OptionalDate = None
    cantidad: Optional[int] = None
    motivo: Optional[str] = None
    estado: Optional[str] = None


class ReturnResponse(ReturnCreate):
    id: int
    user_id: int = 0

    model_config = {"from_attributes": True}
