from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
import csv
import io

from app.database import get_db
from app.dependencies import get_admin_user
from app.models.user import User
from app.models.product import Product
from app.models.sale import Sale
from app.models.return_item import ReturnItem
from app.models.inventory import Inventory
from app.models.activity_log import ActivityLog
from app.models.business import Business
from app.schemas.user import UserResponse, UserUpdate, UserRegister
from app.services.activity import log_activity
from app.routers.auth import hash_password

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(get_admin_user)])


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserRegister,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    from app.schemas.user import VALID_ROLES

    result = await db.execute(select(User).where(
        (User.usuario == data.usuario) | (User.correo == data.correo)
    ))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario o correo ya existe")

    role = data.role or "vendedor"
    if role not in VALID_ROLES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Rol inválido. Válidos: {', '.join(sorted(VALID_ROLES))}")

    hashed = hash_password(data.contrasena)
    user = User(
        name=data.name,
        apellido=data.apellido,
        correo=data.correo,
        usuario=data.usuario,
        contrasena=hashed,
        role=role,
        business_id=data.business_id,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    await log_activity(
        db, current_user.id, f"{current_user.name} {current_user.apellido}",
        "create", "user", user.id,
        f"Usuario creado desde admin: {user.usuario}",
    )
    return user


@router.get("/users", response_model=list[UserResponse])
async def list_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).order_by(User.id))
    return result.scalars().all()


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return user


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    update_data = user_data.model_dump(exclude_unset=True)
    if "contrasena" in update_data:
        if update_data["contrasena"]:
            update_data["contrasena"] = hash_password(update_data["contrasena"])
        else:
            del update_data["contrasena"]
    changes = []
    for field, value in update_data.items():
        old = getattr(user, field, "")
        if str(old) != str(value):
            changes.append(f"{field}: {old} -> {value}")
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)

    await log_activity(
        db, current_user.id, f"{current_user.name} {current_user.apellido}",
        "update", "user", user_id,
        f"Usuario {user.name} {user.apellido}: {'; '.join(changes)}" if changes else "Sin cambios",
    )
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    user_name = f"{user.name} {user.apellido}"
    await db.delete(user)
    await db.commit()

    await log_activity(
        db, current_user.id, f"{current_user.name} {current_user.apellido}",
        "delete", "user", user_id,
        f"Usuario eliminado: {user_name}",
    )


@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    users_count = await db.scalar(select(func.count(User.id)))
    products_count = await db.scalar(select(func.count(Product.id)))
    sales_count = await db.scalar(select(func.count(Sale.id)))
    returns_count = await db.scalar(select(func.count(ReturnItem.id)))

    total_revenue_result = await db.execute(select(func.sum(Sale.prise)))
    total_revenue = total_revenue_result.scalar() or 0

    businesses_count = await db.scalar(select(func.count(Business.id)))

    low_stock_result = await db.execute(
        select(func.count(Product.id)).where(Product.cantidad < 10)
    )
    low_stock = low_stock_result.scalar() or 0

    return {
        "total_users": users_count,
        "total_products": products_count,
        "total_sales": sales_count,
        "total_returns": returns_count,
        "total_revenue": float(total_revenue),
        "low_stock_products": low_stock,
        "total_businesses": businesses_count,
    }


@router.get("/activity")
async def get_activity(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    total = await db.scalar(select(func.count(ActivityLog.id)))

    result = await db.execute(
        select(ActivityLog).order_by(desc(ActivityLog.created_at)).offset(offset).limit(limit)
    )
    logs = result.scalars().all()

    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "data": [
            {
                "id": log.id,
                "user_id": log.user_id,
                "user_name": log.user_name,
                "action": log.action,
                "entity": log.entity,
                "entity_id": log.entity_id,
                "detail": log.detail,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in logs
        ],
    }


@router.get("/export/users")
async def export_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).order_by(User.id))
    users = result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Nombre", "Apellido", "Correo", "Usuario", "Rol"])
    for u in users:
        writer.writerow([u.id, u.name, u.apellido, u.correo, u.usuario, u.role])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=usuarios.csv"},
    )


@router.get("/export/products")
async def export_products(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).order_by(Product.id))
    products = result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Nombre", "Marca", "Tipo", "Descripcion", "Precio", "Stock"])
    for p in products:
        writer.writerow([p.id, p.name_product, p.Marca, p.Tipo, p.Description, p.Price_mayor, p.Price_cliente, p.cantidad])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=productos.csv"},
    )


@router.get("/health")
async def system_health(db: AsyncSession = Depends(get_db)):
    users_count = await db.scalar(select(func.count(User.id)))
    products_count = await db.scalar(select(func.count(Product.id)))
    sales_count = await db.scalar(select(func.count(Sale.id)))
    returns_count = await db.scalar(select(func.count(ReturnItem.id)))
    logs_count = await db.scalar(select(func.count(ActivityLog.id)))
    businesses_count = await db.scalar(select(func.count(Business.id)))

    low_stock = await db.execute(
        select(Product.name_product, Product.cantidad).where(Product.cantidad < 5).order_by(Product.cantidad)
    )
    alerts = [
        {"product": row[0], "stock": row[1]}
        for row in low_stock.fetchall()
    ]

    return {
        "status": "healthy",
        "database": "sqlite",
        "records": {
            "users": users_count,
            "products": products_count,
            "sales": sales_count,
            "returns": returns_count,
            "activity_logs": logs_count,
            "businesses": businesses_count,
        },
        "alerts": {
            "low_stock_count": len(alerts),
            "low_stock_items": alerts,
        },
    }
