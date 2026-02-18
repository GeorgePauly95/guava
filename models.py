from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy import Integer, Identity
from engine import engine
from datetime import datetime


class Base(DeclarativeBase):
    pass


class Workout(Base):
    __tablename__ = "workout"

    id: Mapped[int] = mapped_column(Integer, Identity(always=True), primary_key=True)
    latitude: Mapped[float]
    longitude: Mapped[float]
    time: Mapped[datetime] = mapped_column(TIMESTAMP)
