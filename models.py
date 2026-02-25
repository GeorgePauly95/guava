import sqlalchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy import Integer, Identity, text, Boolean
from engine import engine
from datetime import datetime


class Base(DeclarativeBase):
    pass


class Location(Base):
    __tablename__ = "location"
    __table_args__ = {"extend_existing": True}
    id: Mapped[int] = mapped_column(Integer, Identity(always=True), primary_key=True)
    workout_id: Mapped[int]
    latitude: Mapped[float]
    longitude: Mapped[float]
    time: Mapped[datetime] = mapped_column(TIMESTAMP)

    def store_location(self, connection, location):
        with engine.begin() as connection:
            workout_id = Workout(Base).get_workout_id(connection)
            connection.execute(
                text(
                    "INSERT INTO location VALUES(:latitude, :longitude, :timestamp, :workout_id)"
                ),
                {
                    "latitude": location["latitude"],
                    "longitude": location["longitude"],
                    "timestamp": location["timestamp"],
                    "workout_id": workout_id,
                },
            )

            return


class Workout(Base):
    __tablename__ = "workout"
    id: Mapped[int] = mapped_column(Integer, Identity(always=True), primary_key=True)
    completed: Mapped[bool] = mapped_column(
        Boolean, server_default=sqlalchemy.sql.true()
    )

    def get_workout_id(self, connection):
        with engine.begin() as connection:
            workout_id = connection.execute(
                text("SELECT id FROM workout WHERE completed='False'")
            )
            if workout_id is not None:
                return workout_id
            workout_id = connection.execute(
                text("INSERT INTO workout DEFAULT VALUES RETURNING id")
            )
            return workout_id
