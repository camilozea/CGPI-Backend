from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.return_item import ReturnItem
from app.schemas.return_item import ReturnCreate, ReturnUpdate, ReturnResponse
from app.dependencies import get_current_user, require_role
from app.models.user import User

router = APIRouter(prefix="/returns", tags=["returns"])


@router.get("/", response_model=list[ReturnResponse])
async def list_returns(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(ReturnItem).order_by(ReturnItem.fecha.desc()))
    return result.scalars().all()


@router.get("/{return_id}", response_model=ReturnResponse)
async def get_return(
    return_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(ReturnItem).where(ReturnItem.id == return_id))
    ret = result.scalar_one_or_none()
    if not ret:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Devolución no encontrada")
    return ret


@router.post("/", response_model=ReturnResponse, status_code=status.HTTP_201_CREATED)
async def create_return(
    data: ReturnCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "propietario", "vendedor")),
):
    ret = ReturnItem(**data.model_dump(), user_id=current_user.id)
    db.add(ret)
    await db.commit()
    await db.refresh(ret)
    return ret


@router.put("/{return_id}", response_model=ReturnResponse)
async def update_return(
    return_id: int,
    data: ReturnUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "propietario")),
):
    result = await db.execute(select(ReturnItem).where(ReturnItem.id == return_id))
    ret = result.scalar_one_or_none()
    if not ret:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Devolución no encontrada")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(ret, key, value)

    await db.commit()
    await db.refresh(ret)
    return ret


@router.delete("/{return_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_return(
    return_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "propietario")),
):
    result = await db.execute(select(ReturnItem).where(ReturnItem.id == return_id))
    ret = result.scalar_one_or_none()
    if not ret:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Devolución no encontrada")

    await db.delete(ret)
    await db.commit()


@router.get("/inventory/summary")
async def returns_inventory(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(
            ReturnItem.producto,
            func.count(ReturnItem.id).label("total_devoluciones"),
            func.sum(ReturnItem.cantidad).label("total_cantidad"),
        )
        .group_by(ReturnItem.producto)
        .order_by(func.sum(ReturnItem.cantidad).desc())
    )
    rows = result.all()
    return [
        {
            "producto": row.producto,
            "total_devoluciones": row.total_devoluciones,
            "total_cantidad": row.total_cantidad,
        }
        for row in rows
    ]
