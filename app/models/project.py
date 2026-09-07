from app.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Text, DateTime,func
from datetime import datetime

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.task import Task

class Project(Base):

    __tablename__ = "projects"

    id : Mapped[int]  = mapped_column(primary_key=True)

    organization_id : Mapped[int] = mapped_column(
        ForeignKey("organizations.id"),
        nullable=False,
        index = True, # database indexing
    ) 

    name : Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    description : Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at : Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    version : Mapped[int] = mapped_column( # for optimistic concurrency
        nullable=False,
        default=1,
    )

    organization : Mapped["Organization"] = relationship(
        back_populates="projects",
    )

    tasks : Mapped[list["Task"]] = relationship(
        back_populates="project",
    )