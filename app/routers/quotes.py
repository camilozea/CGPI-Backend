from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.quote import Quote
from app.models.business import Business
from app.schemas.quote import QuoteCreate, QuoteUpdate, QuoteResponse
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/quotes", tags=["quotes"])


@router.get("/", response_model=list[QuoteResponse])
async def list_quotes(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Quote).order_by(Quote.created_at.desc()))
    return result.scalars().all()


@router.post("/", response_model=QuoteResponse, status_code=status.HTTP_201_CREATED)
async def create_quote(
    data: QuoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    quote = Quote(**data.model_dump(), user_id=current_user.id)
    db.add(quote)
    await db.commit()
    await db.refresh(quote)
    return quote


@router.put("/{quote_id}", response_model=QuoteResponse)
async def update_quote(
    quote_id: int,
    data: QuoteUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Quote).where(Quote.id == quote_id))
    quote = result.scalar_one_or_none()
    if not quote:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cotización no encontrada")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(quote, key, value)

    await db.commit()
    await db.refresh(quote)
    return quote


@router.delete("/{quote_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quote(
    quote_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Quote).where(Quote.id == quote_id))
    quote = result.scalar_one_or_none()
    if not quote:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cotización no encontrada")
    await db.delete(quote)
    await db.commit()


@router.get("/{quote_id}/invoice")
async def get_quote_invoice(
    quote_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Quote).where(Quote.id == quote_id))
    quote = result.scalar_one_or_none()
    if not quote:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cotización no encontrada")

    business = None
    if current_user.business_id:
        result = await db.execute(select(Business).where(Business.id == current_user.business_id))
        business = result.scalar_one_or_none()

    return {
        "quote": {
            "id": quote.id,
            "auto": quote.auto,
            "marca": quote.marca,
            "modelo": quote.modelo,
            "nombres": quote.nombres,
            "apellidos": quote.apellidos,
            "tipo_documento": quote.tipo_documento,
            "numero_documento": quote.numero_documento,
            "tipo_reparacion": quote.tipo_reparacion,
            "descripcion": quote.descripcion,
            "items": quote.items,
            "total": quote.total,
            "validez_dias": quote.validez_dias,
            "notas": quote.notas,
            "estado": quote.estado,
            "created_at": quote.created_at.isoformat() if quote.created_at else None,
        },
        "business": {
            "name": business.name if business else "",
            "address": business.address if business else "",
            "phone": business.phone if business else "",
            "email": business.email if business else "",
        } if business else None,
    }
