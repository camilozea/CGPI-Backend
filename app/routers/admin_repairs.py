from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_admin_user
from app.models.user import User
from app.models.repair import Repair
from app.schemas.repair import RepairCreate, RepairUpdate, RepairResponse
from app.services.activity import log_activity

router = APIRouter(prefix="/admin/repairs", tags=["admin"], dependencies=[Depends(get_admin_user)])


@router.post("", response_model=RepairResponse, status_code=status.HTTP_201_CREATED)
async def create_repair(
    data: RepairCreate,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    repair = Repair(
        **data.model_dump(),
        user_id=current_user.id,
        business_id=current_user.business_id or 0,
    )
    db.add(repair)
    await db.commit()
    await db.refresh(repair)

    await log_activity(
        db, current_user.id, f"{current_user.name} {current_user.apellido}",
        "create", "repair", repair.id,
        f"Orden de reparación creada: {repair.client_name} - {repair.device_type}",
    )
    return repair


@router.get("")
async def list_repairs(
    business_id: int | None = Query(None),
    status: str | None = Query(None),
    search: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    query = select(Repair)

    if business_id:
        query = query.where(Repair.business_id == business_id)
    if status:
        query = query.where(Repair.status == status)
    if search:
        q = f"%{search}%"
        query = query.where(
            Repair.client_name.ilike(q) |
            Repair.device_type.ilike(q) |
            Repair.device_brand.ilike(q) |
            Repair.description.ilike(q)
        )

    total = await db.scalar(select(func.count()).select_from(query.subquery()))
    result = await db.execute(query.order_by(desc(Repair.created_at)).offset(offset).limit(limit))
    repairs = result.scalars().all()

    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "data": repairs,
    }


@router.get("/{repair_id}", response_model=RepairResponse)
async def get_repair(repair_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Repair).where(Repair.id == repair_id))
    repair = result.scalar_one_or_none()
    if not repair:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Orden de reparación no encontrada")
    return repair


@router.put("/{repair_id}", response_model=RepairResponse)
async def update_repair(
    repair_id: int,
    data: RepairUpdate,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Repair).where(Repair.id == repair_id))
    repair = result.scalar_one_or_none()
    if not repair:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Orden de reparación no encontrada")

    update_data = data.model_dump(exclude_unset=True)
    changes = []
    for field, value in update_data.items():
        old = getattr(repair, field, "")
        if str(old) != str(value):
            changes.append(f"{field}: {old} -> {value}")
        setattr(repair, field, value)

    await db.commit()
    await db.refresh(repair)

    await log_activity(
        db, current_user.id, f"{current_user.name} {current_user.apellido}",
        "update", "repair", repair_id,
        f"Orden reparación {repair.client_name}: {'; '.join(changes)}" if changes else "Sin cambios",
    )
    return repair


@router.delete("/{repair_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_repair(
    repair_id: int,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Repair).where(Repair.id == repair_id))
    repair = result.scalar_one_or_none()
    if not repair:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Orden de reparación no encontrada")

    info = f"{repair.client_name} - {repair.device_type}"
    await db.delete(repair)
    await db.commit()

    await log_activity(
        db, current_user.id, f"{current_user.name} {current_user.apellido}",
        "delete", "repair", repair_id,
        f"Orden reparación eliminada: {info}",
    )


@router.get("/stats/summary")
async def get_repairs_summary(
    business_id: int | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(Repair)
    if business_id:
        query = query.where(Repair.business_id == business_id)

    total = await db.scalar(select(func.count()).select_from(query.subquery()))

    pending = await db.scalar(
        select(func.count()).select_from(query.where(Repair.status == "pendiente").subquery())
    ) or 0
    in_progress = await db.scalar(
        select(func.count()).select_from(query.where(Repair.status == "en_progreso").subquery())
    ) or 0
    completed = await db.scalar(
        select(func.count()).select_from(query.where(Repair.status == "completado").subquery())
    ) or 0
    delivered = await db.scalar(
        select(func.count()).select_from(query.where(Repair.status == "entregado").subquery())
    ) or 0

    revenue = await db.scalar(
        select(func.coalesce(func.sum(Repair.charge), 0)).select_from(
            query.where(Repair.status.in_(["completado", "entregado"])).subquery()
        )
    ) or 0

    return {
        "total": total,
        "pendiente": pending,
        "en_progreso": in_progress,
        "completado": completed,
        "entregado": delivered,
        "total_revenue": float(revenue),
    }
