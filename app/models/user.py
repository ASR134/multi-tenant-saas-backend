
from datetime import datetime # python datetime type
from typing import TYPE_CHECKING

from sqlalchemy import String, DateTime, func, false
from sqlalchemy.orm import Mapped,mapped_column,relationship

from app.db.base import Base

# type_checking is a special constant that is always False while program is in runtime
if TYPE_CHECKING:# to prevent circular imports
    from app.models.membership import Membership
    from app.models.comment import Comment
    from app.models.invitation import Invitation

# class User defines structure of table 
# actual table lives in postgresql
# an object of class -> represents one row in a table
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Mapped -> what this attribute is in python
    # mapped_column -> database table column settings
    # a user can belong to multiple organizations so no org_id in this model

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    full_name : Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    created_at : Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(), # database side default
        # default=lambda: datetime.now(timezone.utc) # python side default
    )

    email_verified : Mapped[bool] = mapped_column(
        server_default=false(),
        nullable=False,
    )

    verification_token_hash : Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    verification_token_expires_at : Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    memberships : Mapped[list["Membership"]] = relationship(
        back_populates="user",
        passive_deletes=True,# Let the database handle what happens to these child rows when the parent is deleted . Don't let SQLAlchemy manage the delete behaviour 
    )

    comments : Mapped[list["Comment"]] = relationship(
        back_populates="user",
        passive_deletes=True,
    )

    sent_invitations : Mapped[list["Invitation"]] = relationship(
        back_populates="inviter",
        passive_deletes=True,
    )
# relationship() returns python object to the class attribute.
# back_populates is used to setup two way relationship.

# we are using "" for class names . This is called forward reference.

# so basically to prevent circular imports -> type_checking -> which is always false in runtime  -> no import in files -> use forward reference -> after all files are loaded, the forward references are resolved --> the imports are placed in __init__ file