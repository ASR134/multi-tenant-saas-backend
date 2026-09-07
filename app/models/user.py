
from datetime import datetime # python datetime type
from typing import TYPE_CHECKING

from sqlalchemy import String,DateTime,func
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


    memberships : Mapped[list["Membership"]] = relationship(
        back_populates="user"
    )

    comments : Mapped[list["Comment"]] = relationship(
        back_populates="user",
    )

    sent_invitations : Mapped[list["Invitation"]] = relationship(
        back_populates="inviter",
    )
# relationship() returns python object to the class attribute.
# back_populates is used to setup two way relationship.

# we are using "" for class names . This is called forward reference.

# so basically to prevent circular imports -> type_checking -> which is always false in runtime  -> no import in files -> use forward reference -> after all files are loaded, the forward references are resolved --> the imports are placed in __init__ file