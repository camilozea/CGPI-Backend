from sqlalchemy import Column, Integer, String, Date, Integer as IntColumn
from app.database import Base


class ReturnItem(Base):
    __tablename__ = "returns"

    id = Column(Integer, primary_key=True, index=True)
    producto = Column(String(200), nullable=False)
    cliente = Column(String(200), nullable=False)
    fecha = Column(Date, nullable=False)
    cantidad = Column(IntColumn, nullable=False)
    motivo = Column(String(500), nullable=False)
    estado = Column(String(20), nullable=False, default="pendiente")
    user_id = Column(Integer, nullable=False, default=0)
