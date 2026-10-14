from sqlalchemy import Column, Integer, String, Float
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name_product = Column(String(200), nullable=False)
    Marca = Column(String(100), nullable=False)
    Tipo = Column(String(50), nullable=True)
    Description = Column(String(500), nullable=True)
    Price_mayor = Column(Float, nullable=False, default=0)
    Price_cliente = Column(Float, nullable=False, default=0)
    cantidad = Column(Integer, nullable=False, default=0)
