"""add users table

Revision ID: bec1ced5a855
Revises: 
Create Date: 2026-06-21 08:58:54.845369

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bec1ced5a855'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    user_role_enum = sa.Enum('user', 'admin', name='user_role')

    op.create_table(
        'users',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False, unique=True),
        sa.Column('auth0_id', sa.String(length=255), nullable=False, unique=True),
        sa.Column('role', user_role_enum, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_users_auth0_id', 'users', ['auth0_id'])


def downgrade() -> None:
    op.drop_table('users')
    user_role_enum = sa.Enum(name='user_role')
    user_role_enum.drop(op.get_bind())
