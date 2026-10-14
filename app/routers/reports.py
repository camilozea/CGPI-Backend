from datetime import date, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.models.user import User
from app.models.sale import Sale
from app.models.return_item import ReturnItem
from app.models.daily_goal import DailyGoal

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/seller-performance")
async def seller_performance(
    start: str = Query(None),
    end: str = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    start_date = date.fromisoformat(start) if start else date.today() - timedelta(days=30)
    end_date = date.fromisoformat(end) if end else date.today()

    active_users = await db.execute(
        select(User.id, User.name, User.apellido, User.role)
        .where(
            (User.role == "vendedor") |
            (User.id.in_(
                select(Sale.user_id).distinct().where(
                    Sale.date >= start_date, Sale.date <= end_date
                )
            )) |
            (User.id.in_(
                select(ReturnItem.user_id).distinct().where(
                    ReturnItem.fecha >= start_date, ReturnItem.fecha <= end_date
                )
            ))
        )
        .order_by(User.id)
    )
    sellers = active_users.fetchall()

    performance = []
    for seller_id, name, apellido, role in sellers:
        sales_result = await db.execute(
            select(func.count(Sale.id), func.coalesce(func.sum(Sale.prise), 0))
            .where(Sale.user_id == seller_id, Sale.date >= start_date, Sale.date <= end_date)
        )
        sale_count, sale_total = sales_result.one()

        returns_result = await db.execute(
            select(func.count(ReturnItem.id), func.coalesce(func.sum(ReturnItem.cantidad), 0))
            .where(ReturnItem.user_id == seller_id, ReturnItem.fecha >= start_date, ReturnItem.fecha <= end_date)
        )
        return_count, return_total = returns_result.one()

        performance.append({
            "user_id": seller_id,
            "nombre": f"{name} {apellido}",
            "role": role,
            "ventas_totales": float(sale_total),
            "cantidad_ventas": sale_count,
            "devoluciones_totales": float(return_total),
            "cantidad_devoluciones": return_count,
        })

    return {
        "start": start_date.isoformat(),
        "end": end_date.isoformat(),
        "sellers": performance,
    }


@router.get("/daily-goal")
async def get_daily_goal(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = date.today()

    goal_filter = [DailyGoal.date == today]
    sales_filter = [Sale.date == today]

    business_id = current_user.business_id
    if business_id:
        goal_filter.append(DailyGoal.business_id == business_id)
        user_ids = await db.execute(
            select(User.id).where(User.business_id == business_id)
        )
        ids = [row[0] for row in user_ids.fetchall()]
        if ids:
            sales_filter.append(Sale.user_id.in_(ids))

    goal_result = await db.execute(
        select(DailyGoal).where(*goal_filter).order_by(DailyGoal.id.desc()).limit(1)
    )
    daily_goal = goal_result.scalar_one_or_none()
    goal_amount = daily_goal.goal if daily_goal else 0

    sales_result = await db.execute(
        select(func.coalesce(func.sum(Sale.prise), 0))
        .where(*sales_filter)
    )
    current_sales = float(sales_result.scalar() or 0)

    sales_count_result = await db.execute(
        select(func.count(Sale.id)).where(*sales_filter)
    )
    sales_count = sales_count_result.scalar() or 0

    return {
        "date": today.isoformat(),
        "goal": goal_amount,
        "current": current_sales,
        "sales_count": sales_count,
        "progress_pct": round((current_sales / goal_amount * 100), 1) if goal_amount > 0 else 0,
    }


@router.put("/daily-goal")
async def set_daily_goal(
    goal: float = Query(..., gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "propietario")),
):
    today = date.today()
    business_id = current_user.business_id

    goal_filter = [DailyGoal.date == today]
    if business_id:
        goal_filter.append(DailyGoal.business_id == business_id)

    result = await db.execute(
        select(DailyGoal).where(*goal_filter).order_by(DailyGoal.id.desc()).limit(1)
    )
    existing = result.scalar_one_or_none()

    if existing:
        existing.goal = goal
    else:
        existing = DailyGoal(goal=goal, date=today, business_id=business_id)
        db.add(existing)

    await db.commit()
    return {"date": today.isoformat(), "goal": goal}
