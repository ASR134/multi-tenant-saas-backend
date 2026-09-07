from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey,String,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column,relationship

from app.db.base import Base


if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.user import User

class Membership(Base):
    __tablename__ = "memberships"

    __table_args__ = ( 
        UniqueConstraint(
            "user_id",
            "organization_id",
            name = "uq_membership_user_organization",
        ),
    )

    id : Mapped[int] = mapped_column(primary_key=True)

    user_id : Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    organization_id : Mapped[int] = mapped_column(
        ForeignKey("organizations.id")
    )

    role : Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # these are not columns at all
    user : Mapped["User"] = relationship(
        back_populates="memberships" # connects the two individual relationships into one
    )

    organization : Mapped["Organization"] = relationship(
        back_populates = "memberships" # string must match attribute name in other model
    )
