"""add payments table

Revision ID: 6c89de8e6f7b
Revises: ebc7a1596144
Create Date: 2026-07-15 20:52:22.245341

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6c89de8e6f7b'
down_revision: Union[str, Sequence[str], None] = 'ebc7a1596144'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# A new payment record will be created for each payment attempt.
# A new Stripe Checkout Session will be created for each attempt, and the 'bookings' stripe_checkout_session_id will
# always have the latest session id, while this 'payments' table will record each individual attempt
# Example: for a specific booking, the first attempt may get the status 'failed', and this gets recorded in the payments table
# Then the user retries with another card and succeeds -> a new record with status = 'succeeded' gets inserted
# This behavior enhances auditability


def upgrade() -> None:
    payment_status_enum = sa.Enum('pending', 'succeeded', 'failed', 'expired', name='payment_status')

    op.create_table(
        'payments',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('booking_id', sa.UUID(as_uuid=True), sa.ForeignKey('bookings.id', ondelete='CASCADE'), nullable=False),
        sa.Column('stripe_checkout_session_id', sa.String(255), nullable=False, unique=True),
        sa.Column('stripe_payment_intent_id', sa.String(255), nullable=True),

        sa.Column('amount_cents', sa.Integer(), nullable=False),
        sa.Column('currency', sa.CHAR(3), default='usd', nullable=False),
        sa.Column('status', payment_status_enum, default='pending', nullable=False),

        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False)
    )


def downgrade() -> None:
    op.drop_table('payments')
    payment_status_enum = sa.Enum(name='payment_status')
    payment_status_enum.drop(op.get_bind())

