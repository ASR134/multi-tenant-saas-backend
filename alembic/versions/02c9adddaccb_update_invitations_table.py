"""update invitations table

Revision ID: 02c9adddaccb
Revises: 3276c0fe2433
Create Date: 2026-09-25 21:47:31.739808

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '02c9adddaccb'
down_revision: Union[str, Sequence[str], None] = '3276c0fe2433'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'invitations',
        sa.Column(
            'invitation_token_hash',
            sa.String(length=64),
            nullable=True,
        ),
    )

    op.add_column(
        'invitations',
        sa.Column(
            'invitation_token_expires_at',
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.drop_constraint(
        op.f('invitations_token_key'),
        'invitations',
        type_='unique',
    )

    op.create_unique_constraint(
        'uq_invitations_invitation_token_hash',
        'invitations',
        ['invitation_token_hash'],
    )

    op.drop_column('invitations', 'token')
    op.drop_column('invitations', 'expires_at')



def downgrade() -> None:
    op.add_column(
        'invitations',
        sa.Column(
            'expires_at',
            postgresql.TIMESTAMP(timezone=True),
            nullable=True,
        ),
    )

    op.add_column(
        'invitations',
        sa.Column(
            'token',
            sa.VARCHAR(length=255),
            nullable=True,
        ),
    )

    op.drop_constraint(
        'uq_invitations_invitation_token_hash',
        'invitations',
        type_='unique',
    )

    op.create_unique_constraint(
        op.f('invitations_token_key'),
        'invitations',
        ['token'],
        postgresql_nulls_not_distinct=False,
    )

    op.drop_column(
        'invitations',
        'invitation_token_expires_at',
    )

    op.drop_column(
        'invitations',
        'invitation_token_hash',
    )