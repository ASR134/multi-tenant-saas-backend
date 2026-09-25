"""add default to invitation status

Revision ID: a525bec18640
Revises: 02c9adddaccb
Create Date: 2026-09-25 22:52:08.662035

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a525bec18640'
down_revision: Union[str, Sequence[str], None] = '02c9adddaccb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "invitations",
        "status",
        server_default="pending",
    )


def downgrade() -> None:
    op.alter_column(
        "invitations",
        "status",
        server_default=None,
    )