from datetime import date
from sqlalchemy import Column, Integer, Float, Date
from app.database import Base


class DailyGoal(Base):
    __tablename__ = "daily_goals"

    id = Column(Integer, primary_key=True, index=True)
    goal = Column(Float, nullable=False, default=0.0)
    date = Column(Date, nullable=False, default=date.today)
    business_id = Column(Integer, nullable=True, default=None)
