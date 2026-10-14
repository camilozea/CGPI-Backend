from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text
from app.database import Base


class Quote(Base):
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, index=True)
    auto = Column(String(200), nullable=False)
    marca = Column(String(200), nullable=False)
    modelo = Column(String(100), nullable=False)
    nombres = Column(String(200), nullable=False)
    apellidos = Column(String(200), nullable=False)
    tipo_documento = Column(String(20), nullable=False, default="CC")
    numero_documento = Column(String(50), nullable=False)
    tipo_reparacion = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=True)
    items = Column(Text, nullable=True)
    total = Column(Float, nullable=False, default=0)
    validez_dias = Column(Integer, nullable=False, default=15)
    notas = Column(Text, nullable=True)
    estado = Column(String(30), nullable=False, default="pendiente")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    user_id = Column(Integer, nullable=False, default=0)
