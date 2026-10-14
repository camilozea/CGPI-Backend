from sqlalchemy import Column, Integer, String, Float, Date
from app.database import Base


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, nullable=False)
    nombre = Column(String(200), nullable=False)
    precio = Column(Float, nullable=False)
    cantidad = Column(Integer, nullable=False)
    pago = Column(String(50), nullable=False)
