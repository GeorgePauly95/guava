from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import TIMESTAMP, JSONB
from sqlalchemy import Integer, Identity, text, func, ForeignKey
from datetime import datetime
from ..connection import manage_connection
import json


class Base(DeclarativeBase):
    pass


class PauseAndResumeLogs(Base):
    __tablename__ = "pause_resume_logs"
    id: Mapped[int] = mapped_column(Integer, Identity(always=True), primary_key=True)
    workout_id: Mapped[int] = mapped_column(ForeignKey("workout.id"))
    paused_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False
    )
    resumed_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    deleted_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )

    @classmethod
    @manage_connection
    def pause_workout(cls, connection, workout_id, time):
        connection.execute(
            text(
                "INSERT INTO pause_resume_logs(workout_id, paused_at) VALUES(:workout_id, :paused_at)"
            ),
            {"workout_id": workout_id, "paused_at": time},
        )

    @classmethod
    @manage_connection
    def resume_workout(cls, connection, id, time):
        connection.execute(
            text(
                "UPDATE pause_resume_logs SET resumed_at=:resumed_at, updated_at=now() WHERE id=:id AND resumed_at IS NULL"
            ),
            {"id": id, "resumed_at": time},
        )

    @classmethod
    @manage_connection
    def get_logs(cls, connection, workout_id):
        logs = connection.execute(
            text("SELECT * FROM pause_resume_logs WHERE workout_id=:workout_id"),
            {"workout_id": workout_id},
        )
        logs = [log._mapping for log in logs]
        return logs
