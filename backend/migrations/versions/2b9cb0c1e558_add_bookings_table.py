"""add bookings table

Revision ID: 2b9cb0c1e558
Revises: 6c5fa628ecd7
Create Date: 2026-06-21 19:12:05.710465

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2b9cb0c1e558'
down_revision: Union[str, Sequence[str], None] = '6c5fa628ecd7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    booking_status_enum = sa.Enum('pending', 'confirmed', 'expired', 'cancelled', name='booking_status')

    op.create_table(
        'bookings',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', sa.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('event_id', sa.UUID(as_uuid=True), sa.ForeignKey('events.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('ticket_count', sa.Integer(), nullable=False),

        sa.Column('total_price', sa.Numeric(10, 2), nullable=False),
        sa.Column('currency', sa.CHAR(3), default='usd', nullable=False),
        sa.Column('status', booking_status_enum, default='pending', nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),  # timestamp when the status will be set to 'expired'

        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)
    )
    op.create_index('ix_bookings_user_id', 'bookings', ['user_id'])
    op.create_index('ix_bookings_event_id', 'bookings', ['event_id'])


def downgrade() -> None:
    op.drop_table('bookings')
    booking_status_enum = sa.Enum(name='booking_status')
    booking_status_enum.drop(op.get_bind())
