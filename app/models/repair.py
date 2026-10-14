from datetime import date, datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text
from app.database import Base


class Repair(Base):
    __tablename__ = "repairs"

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
    fotos = Column(Text, nullable=True)
    costo = Column(Float, nullable=False, default=0)
    metodo_pago = Column(String(50), nullable=True)
    fecha_entrega = Column(Date, nullable=False)
    estado = Column(String(30), nullable=False, default="pendiente")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    user_id = Column(Integer, nullable=False, default=0)


class RepairPart(Base):
    __tablename__ = "repair_parts"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=True)
    cantidad = Column(Integer, nullable=False, default=0)
    precio_costo = Column(Float, nullable=False, default=0)
    precio_venta = Column(Float, nullable=False, default=0)
    proveedor = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    user_id = Column(Integer, nullable=False, default=0)
