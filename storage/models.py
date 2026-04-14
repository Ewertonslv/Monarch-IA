from datetime import datetime, UTC
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class TaskRecord(Base):
    __tablename__ = "tasks"

    task_id = Column(String, primary_key=True)
    status = Column(String, nullable=False)
    raw_input = Column(Text, nullable=False)
    context_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
