import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func, desc, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_admin_user
from app.models.user import User
from app.models.business import Business
from app.models.sale import Sale
from app.models.return_item import ReturnItem
from app.schemas.business import BusinessCreate, BusinessUpdate, BusinessResponse
from app.services.activity import log_activity

router = APIRouter(prefix="/admin/businesses", tags=["admin"], dependencies=[Depends(get_admin_user)])


@router.post("", response_model=BusinessResponse, status_code=status.HTTP_201_CREATED)
async def create_business(
    data: BusinessCreate,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    existing = await db.execute(select(Business).where(Business.name == data.name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya existe un negocio con ese nombre")

    dump = data.model_dump()
    if dump.get("subcategories") is not None:
        dump["subcategories"] = json.dumps(dump["subcategories"])
    business = Business(**dump)
    db.add(business)
    await db.flush()
    await db.refresh(business)

    current_user.business_id = business.id
    await db.commit()
    await db.refresh(business)

    await log_activity(
        db, current_user.id, f"{current_user.name} {current_user.apellido}",
        "create", "business", business.id,
        f"Negocio creado: {business.name}",
    )
    return business


@router.get("", response_model=list[BusinessResponse])
async def list_businesses(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Business).order_by(Business.name))
    return result.scalars().all()


@router.get("/summary")
async def get_businesses_summary(db: AsyncSession = Depends(get_db)):
    businesses = await db.execute(select(Business).order_by(Business.name))
    businesses = businesses.scalars().all()

    summary = []
    for business in businesses:
        user_ids = await db.execute(
            select(User.id).where(User.business_id == business.id)
        )
        user_ids = [row[0] for row in user_ids.fetchall()]
        total_users = len(user_ids)
        active_users = await db.scalar(
            select(func.count(User.id)).where(
                User.business_id == business.id, User.active == True
            )
        ) or 0

        total_sales = 0
        total_revenue = 0.0
        total_returns = 0
        if user_ids:
            sales_result = await db.execute(
                select(func.count(Sale.id), func.coalesce(func.sum(Sale.prise), 0))
                .where(Sale.user_id.in_(user_ids))
            )
            row = sales_result.one()
            total_sales = row[0] or 0
            total_revenue = float(row[1] or 0)

            returns_count = await db.scalar(
                select(func.count(ReturnItem.id))
                .where(ReturnItem.user_id.in_(user_ids))
            ) or 0
            total_returns = returns_count

        last_sale = None
        return_rate = 0.0
        if user_ids and total_sales > 0:
            last_sale_result = await db.execute(
                select(Sale.date).where(Sale.user_id.in_(user_ids)).order_by(desc(Sale.date)).limit(1)
            )
            row = last_sale_result.scalar_one_or_none()
            if row:
                last_sale = row.isoformat() if hasattr(row, "isoformat") else str(row)
            return_rate = round((total_returns / total_sales) * 100, 1) if total_sales > 0 else 0.0

        summary.append({
            "id": business.id,
            "name": business.name,
            "total_users": total_users,
            "active_users": active_users,
            "total_sales": total_sales,
            "total_revenue": total_revenue,
            "total_returns": total_returns,
            "return_rate": return_rate,
            "last_sale_date": last_sale,
        })

    users_without_business = await db.scalar(
        select(func.count(User.id)).where(User.business_id == None)
    ) or 0

    return {
        "businesses": summary,
        "meta": {
            "users_without_business": users_without_business,
        },
    }


@router.get("/{business_id}", response_model=BusinessResponse)
async def get_business(business_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Business).where(Business.id == business_id))
    business = result.scalar_one_or_none()
    if not business:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Negocio no encontrado")
    return business


@router.put("/{business_id}", response_model=BusinessResponse)
async def update_business(
    business_id: int,
    data: BusinessUpdate,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Business).where(Business.id == business_id))
    business = result.scalar_one_or_none()
    if not business:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Negocio no encontrado")

    update_data = data.model_dump(exclude_unset=True)
    if "subcategories" in update_data and update_data["subcategories"] is not None:
        update_data["subcategories"] = json.dumps(update_data["subcategories"])
    if "name" in update_data and update_data["name"] != business.name:
        dup = await db.execute(select(Business).where(Business.name == update_data["name"]))
        if dup.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya existe un negocio con ese nombre")

    changes = []
    for field, value in update_data.items():
        old = getattr(business, field, "")
        if str(old) != str(value):
            changes.append(f"{field}: {old} -> {value}")
        setattr(business, field, value)

    await db.commit()
    await db.refresh(business)

    await log_activity(
        db, current_user.id, f"{current_user.name} {current_user.apellido}",
        "update", "business", business_id,
        f"Negocio {business.name}: {'; '.join(changes)}" if changes else "Sin cambios",
    )
    return business


@router.delete("/{business_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_business(
    business_id: int,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Business).where(Business.id == business_id))
    business = result.scalar_one_or_none()
    if not business:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Negocio no encontrado")

    users_in_business = await db.execute(select(func.count(User.id)).where(User.business_id == business_id))
    count = users_in_business.scalar() or 0
    if count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede eliminar el negocio porque tiene {count} usuario(s) asignado(s)",
        )

    name = business.name
    await db.delete(business)
    await db.commit()

    await log_activity(
        db, current_user.id, f"{current_user.name} {current_user.apellido}",
        "delete", "business", business_id,
        f"Negocio eliminado: {name}",
    )


@router.get("/{business_id}/users")
async def get_business_users(business_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Business).where(Business.id == business_id))
    business = result.scalar_one_or_none()
    if not business:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Negocio no encontrado")

    users_result = await db.execute(
        select(User).where(User.business_id == business_id).order_by(User.name)
    )
    users = users_result.scalars().all()

    return [
        {
            "id": u.id,
            "name": u.name,
            "apellido": u.apellido,
            "correo": u.correo,
            "usuario": u.usuario,
            "role": u.role,
            "active": u.active,
        }
        for u in users
    ]
