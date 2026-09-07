from datetime import datetime

from sqlalchemy.orm import Mapped,mapped_column,relationship
from sqlalchemy import ForeignKey, Text, DateTime, func

from app.db.base import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.task import Task


class Comment(Base):

    __tablename__ = "comments"

    id : Mapped[int] = mapped_column(primary_key=True)

    task_id : Mapped[int] = mapped_column(
        ForeignKey("tasks.id",ondelete="CASCADE"),
        nullable=False,
        index = True,
    )

    user_id : Mapped[int] = mapped_column(
        ForeignKey("users.id",ondelete="CASCADE"),
        nullable=False,
    )

    content : Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at : Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    task : Mapped["Task"] = relationship(
        back_populates="comments",
    )

    user : Mapped["User"] = relationship(
        back_populates="comments",
    )