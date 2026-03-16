import sqlalchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy import Integer, Identity, text, Boolean, func, ForeignKey
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
    workout_id: Mapped[int] = mapped_column(ForeignKey("workout.id"))
    latitude: Mapped[float]
    longitude: Mapped[float]
    time: Mapped[datetime] = mapped_column(TIMESTAMP)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True)

    @classmethod
    @manage_connection
    def store_location(cls, connection, location):
        latitude, longitude, time, workout_id = location.values()
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
    def get_workout_locations(cls, connection, workout_id):
        locations = connection.execute(
            text(
                """SELECT latitude, longitude, time, workout_id
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
    # can delete this status column
    status: Mapped[bool] = mapped_column(Boolean, server_default=sqlalchemy.sql.true())
    started_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)
    stopped_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True)

    @classmethod
    @manage_connection
    def create_workout(cls, connection, started_at):
        workout = connection.execute(
            text("INSERT INTO workout(started_at) VALUES(:started_at) RETURNING id"),
            {"started_at": started_at},
        )
        workout_id = int([id._mapping for id in workout][0]["id"])
        return workout_id

    @classmethod
    @manage_connection
    def stop_workout(cls, connection, workout_id, stopped_at):
        workout = connection.execute(
            text(
                """UPDATE workout SET status=True, stopped_at=:stopped_at, updated_at=now()
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
    def get_active_workouts(cls, connection):
        workouts = connection.execute(
            text("SELECT id FROM workout WHERE stopped_at IS NULL")
        )
        workouts = [workout._mapping for workout in workouts]
        workout_ids = [workout["id"] for workout in workouts]
        return workout_ids


class PauseAndResumeLogs(Base):
    __tablename__ = "pause_resume_logs"
    id: Mapped[int] = mapped_column(Integer, Identity(always=True), primary_key=True)
    workout_id: Mapped[int] = mapped_column(ForeignKey("workout.id"))
    paused_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)
    resumed_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True)

    @classmethod
    @manage_connection
    def pause_workout(cls, connection, workout_id, time):
        logs = connection.execute(
            text(
                "SELECT * FROM pause_resume_logs WHERE workout_id=:workout_id AND resumed_at IS NULL"
            ),
            {"workout_id": workout_id},
        )
        logs = logs.all()
        if len(logs) == 0:
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
        print("AAAA", logs)
        return logs
