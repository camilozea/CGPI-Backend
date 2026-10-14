from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.sale import Sale
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.business import Business
from app.schemas.sale import SaleCreate, SaleUpdate, SaleResponse
from app.dependencies import get_current_user, require_role
from app.models.user import User
from app.services.activity import log_activity

router = APIRouter(prefix="/sales", tags=["sales"])


@router.get("/", response_model=list[SaleResponse])
async def list_sales(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Sale).order_by(Sale.date.desc()))
    return result.scalars().all()


@router.get("/{sale_id}", response_model=SaleResponse)
async def get_sale(
    sale_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Sale).where(Sale.id == sale_id))
    sale = result.scalar_one_or_none()
    if not sale:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venta no encontrada")
    return sale


@router.post("/", response_model=SaleResponse, status_code=status.HTTP_201_CREATED)
async def create_sale(
    data: SaleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "propietario", "vendedor")),
):
    result = await db.execute(select(Product).where(Product.name_product == data.name_product))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Producto no encontrado en inventario")

    if product.cantidad < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Stock insuficiente")

    product.cantidad -= 1

    inv = Inventory(
        fecha=data.date,
        nombre=product.name_product,
        precio=data.prise,
        cantidad=-1,
        pago="Venta",
    )
    db.add(inv)

    sale = Sale(**data.model_dump(), user_id=current_user.id)
    db.add(sale)
    await db.commit()
    await db.refresh(sale)

    await log_activity(
        db, current_user.id, f"{current_user.name} {current_user.apellido}",
        "create", "sale", sale.id,
        f"Venta: {data.name_product} a {data.name_cliente} - $ {data.prise}",
    )
    return sale


@router.put("/{sale_id}", response_model=SaleResponse)
async def update_sale(
    sale_id: int,
    data: SaleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "propietario")),
):
    result = await db.execute(select(Sale).where(Sale.id == sale_id))
    sale = result.scalar_one_or_none()
    if not sale:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venta no encontrada")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(sale, key, value)

    await db.commit()
    await db.refresh(sale)
    return sale


@router.delete("/{sale_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sale(
    sale_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "propietario")),
):
    result = await db.execute(select(Sale).where(Sale.id == sale_id))
    sale = result.scalar_one_or_none()
    if not sale:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venta no encontrada")

    sale_info = f"{sale.name_product} - {sale.name_cliente}"
    await db.delete(sale)
    await db.commit()

    await log_activity(
        db, current_user.id, f"{current_user.name} {current_user.apellido}",
        "delete", "sale", sale_id,
        f"Venta eliminada: {sale_info}",
    )


@router.get("/{sale_id}/invoice")
async def get_sale_invoice(
    sale_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Sale).where(Sale.id == sale_id))
    sale = result.scalar_one_or_none()
    if not sale:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venta no encontrada")

    business = None
    if current_user.business_id:
        result = await db.execute(select(Business).where(Business.id == current_user.business_id))
        business = result.scalar_one_or_none()

    return {
        "sale": {
            "id": sale.id,
            "name_product": sale.name_product,
            "date": sale.date.isoformat(),
            "prise": sale.prise,
            "name_cliente": sale.name_cliente,
            "documento": sale.documento,
            "discount_prise": sale.discount_prise,
            "user_id": sale.user_id,
        },
        "business": {
            "name": business.name if business else "",
            "address": business.address if business else "",
            "phone": business.phone if business else "",
            "email": business.email if business else "",
        } if business else None,
    }
