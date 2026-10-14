from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.repair import Repair, RepairPart
from app.models.business import Business
from app.schemas.repair import (
    RepairCreate, RepairUpdate, RepairResponse,
    RepairPartCreate, RepairPartUpdate, RepairPartResponse,
)
from app.dependencies import get_current_user, require_role
from app.models.user import User

router = APIRouter(prefix="/repairs", tags=["repairs"])

# ── Reparaciones CRUD ──

@router.get("/", response_model=list[RepairResponse])
async def list_repairs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Repair).order_by(Repair.created_at.desc()))
    return result.scalars().all()


@router.post("/", response_model=RepairResponse, status_code=status.HTTP_201_CREATED)
async def create_repair(
    data: RepairCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repair = Repair(**data.model_dump(), user_id=current_user.id)
    db.add(repair)
    await db.commit()
    await db.refresh(repair)
    return repair


@router.put("/{repair_id}", response_model=RepairResponse)
async def update_repair(
    repair_id: int,
    data: RepairUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Repair).where(Repair.id == repair_id))
    repair = result.scalar_one_or_none()
    if not repair:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reparación no encontrada")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(repair, key, value)

    await db.commit()
    await db.refresh(repair)
    return repair


@router.delete("/{repair_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_repair(
    repair_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Repair).where(Repair.id == repair_id))
    repair = result.scalar_one_or_none()
    if not repair:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reparación no encontrada")
    await db.delete(repair)
    await db.commit()


@router.get("/report")
async def repairs_report(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Repair).order_by(Repair.created_at.desc()))
    repairs = result.scalars().all()
    pendientes = sum(1 for r in repairs if r.estado == "pendiente")
    completadas = sum(1 for r in repairs if r.estado in ("completado", "entregado"))

    return {
        "total_reparaciones": len(repairs),
        "pendientes": pendientes,
        "completadas": completadas,
        "reparaciones": [
            {
                "id": r.id,
                "auto": r.auto,
                "marca": r.marca,
                "nombres": r.nombres,
                "apellidos": r.apellidos,
                "tipo_reparacion": r.tipo_reparacion,
                "estado": r.estado,
                "fecha_entrega": r.fecha_entrega.isoformat(),
            }
            for r in repairs
        ],
    }


@router.get("/{repair_id}/invoice")
async def get_repair_invoice(
    repair_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Repair).where(Repair.id == repair_id))
    repair = result.scalar_one_or_none()
    if not repair:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reparación no encontrada")

    business = None
    if current_user.business_id:
        result = await db.execute(select(Business).where(Business.id == current_user.business_id))
        business = result.scalar_one_or_none()

    return {
        "repair": {
            "id": repair.id,
            "auto": repair.auto,
            "marca": repair.marca,
            "modelo": repair.modelo,
            "nombres": repair.nombres,
            "apellidos": repair.apellidos,
            "tipo_documento": repair.tipo_documento,
            "numero_documento": repair.numero_documento,
            "tipo_reparacion": repair.tipo_reparacion,
            "descripcion": repair.descripcion,
            "costo": repair.costo,
            "metodo_pago": repair.metodo_pago,
            "fecha_entrega": repair.fecha_entrega.isoformat(),
            "estado": repair.estado,
            "created_at": repair.created_at.isoformat() if repair.created_at else None,
        },
        "business": {
            "name": business.name if business else "",
            "address": business.address if business else "",
            "phone": business.phone if business else "",
            "email": business.email if business else "",
        } if business else None,
    }


# ── Repuestos CRUD ──

@router.get("/parts", response_model=list[RepairPartResponse])
async def list_parts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(RepairPart).order_by(RepairPart.nombre))
    return result.scalars().all()


@router.post("/parts", response_model=RepairPartResponse, status_code=status.HTTP_201_CREATED)
async def create_part(
    data: RepairPartCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    part = RepairPart(**data.model_dump(), user_id=current_user.id)
    db.add(part)
    await db.commit()
    await db.refresh(part)
    return part


@router.put("/parts/{part_id}", response_model=RepairPartResponse)
async def update_part(
    part_id: int,
    data: RepairPartUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(RepairPart).where(RepairPart.id == part_id))
    part = result.scalar_one_or_none()
    if not part:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repuesto no encontrado")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(part, key, value)

    await db.commit()
    await db.refresh(part)
    return part


@router.delete("/parts/{part_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_part(
    part_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(RepairPart).where(RepairPart.id == part_id))
    part = result.scalar_one_or_none()
    if not part:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repuesto no encontrado")
    await db.delete(part)
    await db.commit()
