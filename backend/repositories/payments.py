from repositories.base import BaseRepository
from psycopg import AsyncConnection
from models import Payment, Booking, EntityId


class PaymentsRepository(BaseRepository):
    def __init__(self, db_session: AsyncConnection):
        super().__init__(db_session)

    def _map_db_model_to_entity(self, data: dict) -> Payment:
        return Payment(
            id=Payment.build_entity_id_from_uuid(data['id']),
            booking_id=Booking.build_entity_id_from_uuid(data['id']),
            stripe_checkout_session_id=data['stripe_checkout_session_id'],
            stripe_checkout_url=data['stripe_checkout_url'],
            stripe_payment_intent_id=data['stripe_payment_intent_id'],
            amount_cents=data['amount_cents'],
            currency=data['currency'],
            status=data['status'],
            created_at=data['created_at'],
            updated_at=data['updated_at']
        )

    async def create(self, payment: Payment) -> Payment | None:
        async with self.db_session.cursor() as cursor:
            await cursor.execute("""
                INSERT INTO payments (
                    id, booking_id, stripe_checkout_session_id, stripe_checkout_url, stripe_payment_intent_id, amount_cents, currency, status
                ) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *
            """,
            (payment.id.value, payment.booking_id.value, payment.stripe_checkout_session_id, payment.stripe_checkout_url, payment.stripe_payment_intent_id, payment.amount_cents, payment.currency, payment.status))
            db_payment = await cursor.fetchone()
            if not db_payment:
                return None
            return self._map_db_model_to_entity(db_payment)

    async def get_by_id(self, id: EntityId) -> Payment | None:
        async with self.db_session.cursor() as cursor:
            await cursor.execute("SELECT * FROM payments WHERE id = %s", (id.value,))
            db_payment = await cursor.fetchone()
            if not db_payment:
                return None
            return self._map_db_model_to_entity(db_payment)

    async def get_by_stripe_session_id(self, stripe_session_id: str) -> Payment | None:
        async with self.db_session.cursor() as cursor:
            await cursor.execute("""
                SELECT * FROM payments
                WHERE stripe_checkout_session_id = %s
            """, (stripe_session_id,))
            db_payment = await cursor.fetchone()
            if not db_payment:
                return None
            return self._map_db_model_to_entity(db_payment)

    async def get_by_booking_id(self, booking_id: EntityId) -> Payment | None:
        async with self.db_session.cursor() as cursor:
            await cursor.execute("""
                SELECT * FROM payments
                WHERE booking_id = %s
            """, (booking_id.value,))
            db_payment = await cursor.fetchone()
            if not db_payment:
                return None
            return self._map_db_model_to_entity(db_payment)

    async def get_all(self):
        pass

    async def update(self, id: EntityId, payment: Payment) -> Payment | None:
        async with self.db_session.cursor() as cursor:
            await cursor.execute("""
                UPDATE payments
                SET 
                    status = %s,
                    stripe_payment_intent_id = %s,
                    updated_at = NOW()
                WHERE id = %s
                RETURNING *
            """,
                (payment.status, payment.stripe_payment_intent_id, id.value))
            db_payment = await cursor.fetchone()
            if not db_payment:
                return None
            return self._map_db_model_to_entity(db_payment)

    async def delete():
        pass