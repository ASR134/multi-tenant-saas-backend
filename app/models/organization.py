from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped,mapped_column,relationship

from app.db.base import Base


if TYPE_CHECKING:
    from app.models.membership import Membership
    from app.models.project import Project
    from app.models.invitation import Invitation

# a organization represents one tenant in our SaaS system

class Organization(Base):
    __tablename__ = "organizations"

    id : Mapped[int] = mapped_column(primary_key=True)

    name : Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    memberships : Mapped[list["Membership"]] = relationship(
        back_populates="organization"
    )

    projects : Mapped["Project"] = relationship(
        back_populates="organization",
    )

    invitations : Mapped[list["Invitation"]] = relationship(
        back_populates="organization",
    )
