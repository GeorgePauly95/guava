from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import TIMESTAMP, JSONB
from sqlalchemy import Integer, Identity, text, func
from datetime import datetime
from ..connection import manage_connection
import json


class Base(DeclarativeBase):
    pass


# Add user_id column to the table.
class FitnessData(Base):
    __tablename__ = "data"
    id: Mapped[int] = mapped_column(Integer, Identity(always=True), primary_key=True)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    deleted_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    data: Mapped[json] = mapped_column(JSONB, nullable=False)

    @classmethod
    @manage_connection
    def ingest_data(cls, connection, data):
        connection.execute(
            text('INSERT INTO data("data") VALUES (:data)'), {"data": data}
        )
        return "Data ingested!"
