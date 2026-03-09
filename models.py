import sqlalchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy import Integer, Identity, text, Boolean
from datetime import datetime
from engine import engine


def manage_connection(model_function):
    def inner(cls, *args, **kwargs):
        with engine.begin() as connection:
            return model_function(cls, connection, *args, **kwargs)

    return inner


class Base(DeclarativeBase):
    pass


class Locations(Base):
    __tablename__ = "location"
    __table_args__ = {"extend_existing": True}
    id: Mapped[int] = mapped_column(Integer, Identity(always=True), primary_key=True)
    workout_id: Mapped[int]
    latitude: Mapped[float]
    longitude: Mapped[float]
    time: Mapped[datetime] = mapped_column(TIMESTAMP)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP)

    @classmethod
    @manage_connection
    def store_location(cls, connection, location):
        latitude, longitude, time, workout_id, created_at = location.values()
        connection.execute(
            text(
                """INSERT INTO location(latitude, longitude, time, workout_id, created_at)
                VALUES(:latitude, :longitude, :time, :workout_id, :created_at)"""
            ),
            {
                "latitude": latitude,
                "longitude": longitude,
                "time": time,
                "workout_id": workout_id,
                "created_at": created_at,
            },
        )
        return

    @classmethod
    @manage_connection
    def get_workout_locations(cls, connection, workout_id):
        locations = connection.execute(
            text(
                """SELECT latitude, longitude, time, workout_id, created_at
                FROM location WHERE workout_id=:workout_id
                ORDER BY time"""
            ),
            {"workout_id": workout_id},
        )
        locations = [location._mapping for location in locations]
        return locations


class Workouts(Base):
    __tablename__ = "workout"
    id: Mapped[int] = mapped_column(Integer, Identity(always=True), primary_key=True)
    status: Mapped[bool] = mapped_column(Boolean, server_default=sqlalchemy.sql.true())
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)
    paused_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True)
    resumed_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True)
    stopped_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True)

    @classmethod
    @manage_connection
    def create_workout(cls, connection, created_at):
        workout = connection.execute(
            text("INSERT INTO workout(created_at) VALUES(:created_at) RETURNING id"),
            {"created_at": created_at},
        )
        workout_id = int([id._mapping for id in workout][0]["id"])
        return workout_id

    @classmethod
    @manage_connection
    def stop_workout(cls, connection, workout_id, stopped_at):
        connection.execute(
            text(
                """UPDATE workout SET status=:True, stopped_at=:stopped_at WHERE id=:workout_id"""
            ),
            {"True": True, "workout_id": workout_id, "stopped_at": stopped_at},
        )
        return

    @classmethod
    @manage_connection
    def check_workout_status(cls, connection, workout_id):
        status = connection.execute(
            text("SELECT status FROM workout WHERE id=:workout_id"),
            {"workout_id": workout_id},
        )
        return status
