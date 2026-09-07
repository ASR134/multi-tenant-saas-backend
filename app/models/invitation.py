from app.db.base import Base
from datetime import datetime

from sqlalchemy import Text, String, ForeignKey, DateTime, func
from sqlalchemy.orm import mapped_column,Mapped,relationship

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.user import User
    from app.models.organization import Organization

class Invitation(Base):
    __tablename__ = "invitations"

    id : Mapped[int] = mapped_column(primary_key=True)

    organization_id : Mapped[int] = mapped_column(
        ForeignKey("organizations.id"),
        nullable=False,
        index = True,
    )

    email : Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    invited_by : Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    # for security purpose we have token 
    token : Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    status : Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="pending",
    )

    created_at : Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    expires_at : Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    organization : Mapped["Organization"] = relationship(
        back_populates="invitations",
    )

    inviter : Mapped["User"] = relationship(
        back_populates="sent_invitations",
    )