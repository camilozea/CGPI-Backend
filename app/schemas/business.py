from datetime import datetime
from pydantic import BaseModel, field_validator
import json


class BusinessCreate(BaseModel):
    name: str
    description: str | None = None
    nit: str | None = None
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    type: str = "ventas"
    subcategories: list[str] | None = None

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        from app.models.business import BUSINESS_TYPES
        if v not in BUSINESS_TYPES:
            raise ValueError(f"Tipo inválido. Debe ser uno de: {', '.join(sorted(BUSINESS_TYPES))}")
        return v

    @field_validator("subcategories")
    @classmethod
    def validate_subcategories(cls, v, info):
        if v is None:
            return v
        from app.models.business import SUBCATEGORIES_VENTAS, SUBCATEGORIES_REPARACION
        business_type = info.data.get("type", "ventas")
        valid = SUBCATEGORIES_VENTAS if business_type == "ventas" else SUBCATEGORIES_REPARACION
        for s in v:
            if s not in valid:
                raise ValueError(f"Subcategoría '{s}' no válida para tipo '{business_type}'")
        return v


class BusinessUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    nit: str | None = None
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    profit_margin: int | None = None
    type: str | None = None
    subcategories: list[str] | None = None


class BusinessResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    nit: str | None = None
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    profit_margin: int = 30
    type: str = "ventas"
    subcategories: list[str] | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}

    @field_validator("subcategories", mode="before")
    @classmethod
    def parse_subcategories(cls, v):
        if isinstance(v, str):
            return json.loads(v) if v else None
        return v
