from sqlalchemy import Column, Integer, String, Float, Date
from app.database import Base


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    name_product = Column(String(200), nullable=False)
    date = Column(Date, nullable=False)
    prise = Column(Float, nullable=False)
    name_cliente = Column(String(200), nullable=False)
    documento = Column(String(50), nullable=True)
    discount_prise = Column(Float, nullable=True)
    user_id = Column(Integer, nullable=False, default=0)
