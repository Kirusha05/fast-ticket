"""add booking_seats table

Revision ID: e93ec9fad1a9
Revises: 2b9cb0c1e558
Create Date: 2026-06-21 19:12:08.030087

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e93ec9fad1a9'
down_revision: Union[str, Sequence[str], None] = '2b9cb0c1e558'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'booking_seated_tickets',
        sa.Column('booking_id', sa.UUID(as_uuid=True), sa.ForeignKey('bookings.id', ondelete='CASCADE'), nullable=False),
        sa.Column('seat_id', sa.UUID(as_uuid=True), sa.ForeignKey('event_seats.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        # Pure join table, so just use a composite primary key
        sa.PrimaryKeyConstraint('booking_id', 'seat_id'),
    )


def downgrade() -> None:
    op.drop_table('booking_seated_tickets')
