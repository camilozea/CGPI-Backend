from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import auth, products, sales, returns, inventory, admin, reports, admin_businesses, business_settings, repairs, quotes


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="CGPI - Control de Gestión (Punto de Inventario)",
    description="Backend API para el sistema de control de inventario y ventas",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(sales.router)
app.include_router(returns.router)
app.include_router(inventory.router)
app.include_router(admin.router)
app.include_router(admin_businesses.router)
app.include_router(reports.router)
app.include_router(business_settings.router)
app.include_router(repairs.router)
app.include_router(quotes.router)


@app.get("/")
async def root():
    return {"message": "CGPI API - Control de Gestión de Punto de Inventario"}
