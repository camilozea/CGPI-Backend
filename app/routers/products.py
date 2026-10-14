from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.product import Product
from app.models.inventory import Inventory
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.dependencies import get_current_user, require_role
from app.models.user import User
from app.services.activity import log_activity

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=list[ProductResponse])
async def list_products(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Product).order_by(Product.id))
    return result.scalars().all()


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return product


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "propietario")),
):
    product = Product(**data.model_dump())
    db.add(product)
    await db.flush()

    inv = Inventory(
        fecha=date.today(),
        nombre=product.name_product,
        precio=product.Price_cliente,
        cantidad=product.cantidad,
        pago="Entrada",
    )
    db.add(inv)
    await db.commit()
    await db.refresh(product)

    await log_activity(
        db, current_user.id, f"{current_user.name} {current_user.apellido}",
        "create", "product", product.id,
        f"Producto creado: {product.name_product} (Mayor: ${product.Price_mayor}, Cliente: ${product.Price_cliente})",
    )
    return product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "propietario")),
):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)

    await db.commit()
    await db.refresh(product)

    await log_activity(
        db, current_user.id, f"{current_user.name} {current_user.apellido}",
        "update", "product", product_id,
        f"Producto actualizado: {product.name_product}",
    )
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "propietario")),
):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

    product_name = product.name_product
    await db.delete(product)
    await db.commit()

    await log_activity(
        db, current_user.id, f"{current_user.name} {current_user.apellido}",
        "delete", "product", product_id,
        f"Producto eliminado: {product_name}",
    )
