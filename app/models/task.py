from app.db.base import Base
from datetime import datetime
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey, String, Text, DateTime, func

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.comment import Comment

class Task(Base):
    __tablename__ = "tasks"

    id : Mapped[int] = mapped_column(primary_key=True)

    project_id : Mapped[int] = mapped_column(
        ForeignKey("projects.id"),
        nullable=False,
        index = True,
    )

    title : Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    description : Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status : Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="todo",
    )

    created_at : Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    version : Mapped[int] = mapped_column( # for optimistic concurrency
        nullable = False,
        default=1,
    )

    project : Mapped["Project"] = relationship(
        back_populates="tasks",
    )

    comments : Mapped[list["Comment"]] = relationship(
        back_populates="task",
    )