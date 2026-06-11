from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy import Integer, Identity, text, func, ForeignKey, bindparam
from datetime import datetime
from ..connection import manage_connection


class Base(DeclarativeBase):
    pass


class Workouts(Base):
    __tablename__ = "workout"
    id: Mapped[int] = mapped_column(Integer, Identity(always=True), primary_key=True)
    started_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False
    )
    stopped_at: Mapped[datetime] = mapped_column(
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
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    @classmethod
    @manage_connection
    def create_workout(cls, connection, user_id, started_at):
        workout = connection.execute(
            text(
                "INSERT INTO workout(user_id, started_at) VALUES(:user_id, :started_at) RETURNING id"
            ),
            {"user_id": user_id, "started_at": started_at},
        )
        workout_id = int([id._mapping for id in workout][0]["id"])
        return workout_id

    @classmethod
    @manage_connection
    def stop_workout(cls, connection, workout_id, stopped_at):
        workout = connection.execute(
            text(
                """UPDATE workout SET stopped_at=:stopped_at, updated_at=now()
                WHERE id=:workout_id AND stopped_at IS NULL"""
            ),
            {"workout_id": workout_id, "stopped_at": stopped_at},
        )
        return

    @classmethod
    @manage_connection
    def get_workout(cls, connection, workout_id):
        workouts = connection.execute(
            text("SELECT * FROM workout WHERE id=:workout_id"),
            {"workout_id": workout_id},
        )
        workout = workouts.fetchone()
        if workout is None:
            return workout
        return workout._mapping

    @classmethod
    @manage_connection
    def get_workouts(cls, connection, user_id):
        workouts = connection.execute(
            text("SELECT * FROM workout WHERE user_id=:user_id"),
            {"user_id": user_id},
        )
        workouts = [workout._mapping for workout in workouts]
        if len(workouts) == 0:
            return
        return workouts

    @classmethod
    @manage_connection
    def get_active_workouts(cls, connection):
        workouts = connection.execute(
            text("SELECT id FROM workout WHERE stopped_at IS NULL")
        )
        workouts = [workout._mapping for workout in workouts]
        workout_ids = [workout["id"] for workout in workouts]
        return workout_ids
