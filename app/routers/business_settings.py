from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.models.user import User
from app.models.business import Business
from app.schemas.business import BusinessUpdate

router = APIRouter(prefix="/business", tags=["business"])


@router.get("/settings")
async def get_business_settings(
    current_user: User = Depends(require_role("admin", "propietario")),
    db: AsyncSession = Depends(get_db),
):
    if not current_user.business_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No tienes un negocio asignado")

    result = await db.execute(select(Business).where(Business.id == current_user.business_id))
    business = result.scalar_one_or_none()
    if not business:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Negocio no encontrado")

    return {"id": business.id, "name": business.name, "profit_margin": business.profit_margin}


@router.put("/settings")
async def update_business_settings(
    data: BusinessUpdate,
    current_user: User = Depends(require_role("admin", "propietario")),
    db: AsyncSession = Depends(get_db),
):
    if not current_user.business_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No tienes un negocio asignado")

    result = await db.execute(select(Business).where(Business.id == current_user.business_id))
    business = result.scalar_one_or_none()
    if not business:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Negocio no encontrado")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(business, key, value)

    await db.commit()
    await db.refresh(business)

    return {"id": business.id, "name": business.name, "profit_margin": business.profit_margin}
