from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.database import Base


BUSINESS_TYPES = {"ventas", "reparacion"}

SUBCATEGORIES_VENTAS = ["ropa", "calzado", "electronica", "electrodomesticos", "tecnologia_celulares", "tecnologia_computo", "tecnologia_tablets", "hogar", "juguetes", "deportes", "alimentos", "belleza", "herramientas", "mascotas", "libros", "automotriz", "instrumentos_musicales", "otros"]

SUBCATEGORIES_REPARACION = ["tecnologia_celulares", "tecnologia_computo", "tecnologia_tablets", "electrodomesticos", "vehiculos_motos", "vehiculos_carros", "vehiculos_bicicletas", "herramientas", "audiovisual", "climatizacion", "joyeria_relojes", "instrumentos_musicales", "hogar_muebles", "otros"]


class Business(Base):
    __tablename__ = "businesses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    address = Column(String(300), nullable=True)
    nit = Column(String(50), nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(150), nullable=True)
    profit_margin = Column(Integer, nullable=False, default=30)
    type = Column(String(20), nullable=False, default="ventas")
    subcategories = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
