from datetime import datetime
from typing import Optional
from pydantic import BaseModel


VALID_ROLES = {"admin", "propietario", "vendedor", "reparador"}


class UserRegister(BaseModel):
    name: str
    apellido: str
    correo: str
    usuario: str
    contrasena: str
    role: str = "vendedor"
    business_id: int | None = None


class UserLogin(BaseModel):
    usuario: str
    contrasena: str


class UserResponse(BaseModel):
    id: int
    name: str
    apellido: str
    correo: str
    usuario: str
    role: str
    active: bool
    business_id: int | None = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    name: str | None = None
    apellido: str | None = None
    correo: str | None = None
    usuario: str | None = None
    role: str | None = None
    active: bool | None = None
    business_id: int | None = None
    contrasena: str | None = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
