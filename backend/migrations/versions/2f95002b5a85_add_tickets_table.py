"""add tickets table

Revision ID: 2f95002b5a85
Revises: 6c89de8e6f7b
Create Date: 2026-07-25 19:43:28.249240

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2f95002b5a85'
down_revision: Union[str, Sequence[str], None] = '6c89de8e6f7b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    ticket_status_enum = sa.Enum('unused', 'used', name='ticket_status')

    op.create_table(
        'tickets',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('booking_id', sa.UUID(as_uuid=True), sa.ForeignKey('bookings.id', ondelete='RESTRICT'), nullable=False),
        # keeping event_id (even though it exists on the booking & seat/tier) for fast "how many checked in for this event"
        sa.Column('event_id', sa.UUID(as_uuid=True), sa.ForeignKey('events.id', ondelete='RESTRICT'), nullable=False),
        
        # One of these two will be filled, the other will be NULL
        sa.Column('seat_id', sa.UUID(as_uuid=True), sa.ForeignKey('event_seats.id', ondelete='RESTRICT'), nullable=True),
        sa.Column('tier_id', sa.UUID(as_uuid=True), sa.ForeignKey('event_tiers.id', ondelete='RESTRICT'), nullable=True),
        
        sa.Column('status', ticket_status_enum, nullable=False, default='unused'),
        sa.Column('checked_in_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        
        # This constraint ensures a ticket CANNOT have both a seat and a tier, 
        # and it CANNOT have neither. It MUST have exactly one.
        sa.CheckConstraint(
            "(seat_id IS NOT NULL AND tier_id IS NULL) OR (seat_id IS NULL AND tier_id IS NOT NULL)",
            name="check_ticket_has_seat_or_tier"
        ),
    )
    op.create_index('ix_tickets_booking_id', 'tickets', ['booking_id'])
    op.create_index('ix_tickets_event_id', 'tickets', ['event_id'])
    op.create_index('ix_tickets_seat_id', 'tickets', ['seat_id'])
    op.create_index('ix_tickets_tier_id', 'tickets', ['tier_id'])


def downgrade() -> None:
    op.drop_table('tickets')
    ticket_status_enum = sa.Enum(name='ticket_status')
    ticket_status_enum.drop(op.get_bind())
