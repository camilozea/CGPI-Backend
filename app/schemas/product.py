from pydantic import BaseModel
from typing import Optional


class ProductCreate(BaseModel):
    name_product: str
    Marca: str
    Tipo: Optional[str] = None
    Description: Optional[str] = None
    Price_mayor: float = 0
    Price_cliente: float = 0
    cantidad: int = 0


class ProductUpdate(BaseModel):
    name_product: Optional[str] = None
    Marca: Optional[str] = None
    Tipo: Optional[str] = None
    Description: Optional[str] = None
    Price_mayor: Optional[float] = None
    Price_cliente: Optional[float] = None
    cantidad: Optional[int] = None


class ProductResponse(ProductCreate):
    id: int

    model_config = {"from_attributes": True}
