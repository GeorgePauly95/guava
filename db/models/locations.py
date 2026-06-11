from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy import Integer, Identity, text, func, ForeignKey, bindparam
from datetime import datetime
from ..connection import manage_connection


class Base(DeclarativeBase):
    pass


class Locations(Base):
    __tablename__ = "location"
    __table_args__ = {"extend_existing": True}
    id: Mapped[int] = mapped_column(Integer, Identity(always=True), primary_key=True)
    workout_id: Mapped[int] = mapped_column(ForeignKey("workout.id"))
    latitude: Mapped[float]
    longitude: Mapped[float]
    time: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )
    deleted_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )

    @classmethod
    @manage_connection
    def store_location(cls, connection, location):
        (
            latitude,
            longitude,
            time,
            workout_id,
        ) = (
            location["latitude"],
            location["longitude"],
            location["time"],
            location["workout_id"],
        )
        connection.execute(
            text(
                """INSERT INTO location(latitude, longitude, time, workout_id)
                VALUES(:latitude, :longitude, :time, :workout_id)"""
            ),
            {
                "latitude": latitude,
                "longitude": longitude,
                "time": time,
                "workout_id": workout_id,
            },
        )
        return

    @classmethod
    @manage_connection
    def get_workout_locations(cls, connection, user_ids):
        sql = text(
            """SELECT latitude, longitude, time, workout_id, user_id
                FROM location ON workout.id = location.workout_id WHERE user_id IN :user_ids AND workout.stopped_at IS NULL
                ORDER BY time"""
        )
        sql = sql.bindparams(bindparam("user_ids", expanding=True))
        locations = connection.execute(sql, {"user_ids": user_ids})
        locations = [location._mapping for location in locations]
        return locations
