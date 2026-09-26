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
        ForeignKey("users.id",ondelete="SET NULL"),
        nullable=True,
    )

    created_at : Mapped[datetime] = mapped_column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now()
        )
    
    status : Mapped[str] = mapped_column(
            String(100),
            nullable=False,
            server_default="pending",
        )
    
    # for security purpose we have token 
    invitation_token_hash : Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
    )

    invitation_token_expires_at : Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    organization : Mapped["Organization"] = relationship(
        back_populates="invitations",
    )

    inviter : Mapped["User"] = relationship(
        back_populates="sent_invitations",
    )