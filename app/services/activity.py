from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.activity_log import ActivityLog


async def log_activity(
    db: AsyncSession,
    user_id: int,
    user_name: str,
    action: str,
    entity: str | None = None,
    entity_id: int | None = None,
    detail: str | None = None,
):
    log = ActivityLog(
        user_id=user_id,
        user_name=user_name,
        action=action,
        entity=entity,
        entity_id=entity_id,
        detail=detail,
        created_at=datetime.now(timezone.utc),
    )
    db.add(log)
    await db.commit()
