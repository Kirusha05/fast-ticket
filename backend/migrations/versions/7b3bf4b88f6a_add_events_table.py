"""add events table

Revision ID: 7b3bf4b88f6a
Revises: bec1ced5a855
Create Date: 2026-06-21 19:11:54.403324

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7b3bf4b88f6a'
down_revision: Union[str, Sequence[str], None] = 'bec1ced5a855'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    event_type_enum = sa.Enum('tiered', 'seated', name='event_type')
    
    op.create_table(
        'events',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('venue', sa.String(length=255), nullable=False),
        sa.Column('event_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('event_type', event_type_enum, nullable=False),
        sa.Column('banner_url', sa.Text(), nullable=False),
        sa.Column('total_tickets', sa.Integer(), nullable=True),
        sa.Column('available_tickets', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('events')
    event_type_enum = sa.Enum(name='event_type')
    event_type_enum.drop(op.get_bind())
