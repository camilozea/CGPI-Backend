from pydantic import BaseModel
from typing import Optional
from datetime import date

from app.schemas.types import OptionalDate


class SaleCreate(BaseModel):
    name_product: str
    date: date
    prise: float
    name_cliente: str
    documento: Optional[str] = None
    discount_prise: Optional[float] = None


class SaleUpdate(BaseModel):
    name_product: Optional[str] = None
    date: OptionalDate = None
    prise: Optional[float] = None
    name_cliente: Optional[str] = None
    documento: Optional[str] = None
    discount_prise: Optional[float] = None


class SaleResponse(SaleCreate):
    id: int
    user_id: int = 0

    model_config = {"from_attributes": True}
