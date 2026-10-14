from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    correo = Column(String(150), unique=True, nullable=False, index=True)
    usuario = Column(String(80), unique=True, nullable=False, index=True)
    contrasena = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="user")
    active = Column(Boolean, nullable=False, default=True)
    business_id = Column(Integer, nullable=True, default=None)
    created_at = Column(DateTime, default=datetime.utcnow)
