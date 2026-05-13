from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import TIMESTAMP, JSONB
from sqlalchemy import Integer, Identity, text, func
from datetime import datetime
from ..connection import manage_connection


class Base(DeclarativeBase):
    pass


# TODO: user is a reserved keyword in postgres. modify the table name to users.
class Users(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(Integer, Identity(always=True), primary_key=True)

    username: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    deleted_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    google_id: Mapped[str] = mapped_column(nullable=True, unique=True)

    @classmethod
    @manage_connection
    def create_user(cls, connection, username):
        user = connection.execute(
            text('INSERT INTO "user"(username) VALUES(:username) RETURNING id'),
            {"username": username},
        )

        user_id = int([id._mapping for id in user][0]["id"])
        return user_id

    @classmethod
    @manage_connection
    def get_or_create_by_google_id(cls, connection, google_id, username):
        user = connection.execute(
            text('SELECT id FROM "user" where google_id=:google_id'),
            {"google_id": google_id},
        ).fetchone()
        if user:
            return user._mapping["id"]
        new_user = connection.execute(
            text(
                'INSERT INTO "user"("username", "google_id") VALUES(:username, :google_id) RETURNING id'
            ),
            {"username": username, "google_id": google_id},
        ).fetchone()
        return new_user._mapping["id"]
