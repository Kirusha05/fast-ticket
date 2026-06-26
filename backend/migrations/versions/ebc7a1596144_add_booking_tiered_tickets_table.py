"""add_booking_tiered_tickets_table

Revision ID: ebc7a1596144
Revises: d455052884ad
Create Date: 2026-06-25 12:07:44.188260

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ebc7a1596144'
down_revision: Union[str, Sequence[str], None] = 'd455052884ad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'booking_tiered_tickets',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('booking_id', sa.UUID(as_uuid=True), sa.ForeignKey('bookings.id', ondelete='CASCADE'), nullable=False),
        sa.Column('ticket_tier_id', sa.UUID(as_uuid=True), sa.ForeignKey('event_tiers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('unit_price', sa.Numeric(10, 2), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_booking_tiered_tickets_booking_id', 'booking_tiered_tickets', ['booking_id'])
    op.create_index('ix_booking_tiered_tickets_ticket_tier_id', 'booking_tiered_tickets', ['ticket_tier_id'])


def downgrade() -> None:
    op.drop_index('ix_booking_tiered_tickets_ticket_tier_id')
    op.drop_index('ix_booking_tiered_tickets_booking_id')
    op.drop_table('booking_tiered_tickets')