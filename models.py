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


class Location(Base):
    __tablename__ = "location"
    __table_args__ = {"extend_existing": True}
    id: Mapped[int] = mapped_column(Integer, Identity(always=True), primary_key=True)
    workout_id: Mapped[int]
    latitude: Mapped[float]
    longitude: Mapped[float]
    time: Mapped[datetime] = mapped_column(TIMESTAMP)

    @classmethod
    @manage_connection
    def store_location(cls, connection, location):
        connection.execute(
            text(
                """INSERT INTO location(latitude, longitude, time, workout_id)
                VALUES(:latitude, :longitude, :time, :workout_id)"""
            ),
            {
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "time": location["time"],
                "workout_id": location["workout_id"],
            },
        )
        connection.commit()
        connection.close()
        return


class Workout(Base):
    __tablename__ = "workout"
    id: Mapped[int] = mapped_column(Integer, Identity(always=True), primary_key=True)
    completed: Mapped[bool] = mapped_column(
        Boolean, server_default=sqlalchemy.sql.true()
    )

    @classmethod
    @manage_connection
    def get_workout_id(cls, connection):
        workout_id = connection.execute(
            text("INSERT INTO workout DEFAULT VALUES RETURNING id")
        )
        workout_id = [id._mapping for id in workout_id]
        connection.commit()
        connection.close()
        return workout_id

    @classmethod
    @manage_connection
    def tbd(cls, connection, workout_id):
        connection.execute(text("SELECT "), {"workout_id": workout_id})
        return
