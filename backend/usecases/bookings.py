from fastapi import HTTPException
from psycopg import AsyncConnection
from collections import Counter
from repositories import (
    BookingsRepository,
    EventsRepository,
    EventSeatsRepository,
    BookingSeatedTicketsRepository,
    EventTiersRepository,
    BookingTieredTicketsRepository,
    PaymentsRepository,
    TicketsRepository
)
from models import (
    Booking,
    BookingStatus,
    EntityId,
    Event,
    CreateBookingRequest,
    EventType,
    EventTier,
    EventSeat,
    BookingResponse,
    PaymentSessionResponse,
    User,
    Payment,
    PaymentStatus,
    Ticket,
    TicketStatus
)
from datetime import datetime, timedelta, timezone
import stripe
from config import stripe_client
from config import config


class BookingsUseCase:
    def __init__(self, db_session: AsyncConnection):
        self.db_session = db_session
        self._bookings_repository = BookingsRepository(db_session)
        self._events_repository = EventsRepository(db_session)
        self._event_seats_repository = EventSeatsRepository(db_session)
        self._booking_seated_tickets_repository = BookingSeatedTicketsRepository(db_session)
        self._event_tiers_repository = EventTiersRepository(db_session)
        self._booking_tiered_tickets_repository = BookingTieredTicketsRepository(db_session)
        self._payments_repository = PaymentsRepository(db_session)
        self._tickets_repository = TicketsRepository(db_session)

    async def create_booking(self, user: User, booking_request: CreateBookingRequest) -> BookingResponse:
        event_id = EntityId.from_string(booking_request.event_id)

        event = await self._events_repository.get_by_id(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        if datetime.now(timezone.utc) > event.event_date:
            raise HTTPException(status_code=409, detail="Cannot make a reservation after the event has started")

        if event.event_type == EventType.SEATED:
            if not booking_request.seat_ids:
                raise HTTPException(status_code=400, detail="Seated events require seat_ids")
            created_booking = await self._create_seated_booking(user.id, event, booking_request)

        elif event.event_type == EventType.TIERED:
            if not booking_request.tiered_tickets:
                raise HTTPException(status_code=400, detail="Tiered events require tiered_tickets")
            created_booking = await self._create_tiered_booking(user.id, event, booking_request)

        else:
            raise HTTPException(status_code=400, detail=f"Unknown event type: {event.event_type}")

        return created_booking

    async def _create_seated_booking(
        self, user_id: EntityId, event: Event, booking_request: CreateBookingRequest
    ) -> BookingResponse:
        seat_ids = [EntityId.from_string(sid) for sid in booking_request.seat_ids]
        seats = await self._event_seats_repository.get_seats_by_ids_for_update(seat_ids)

        if len(seats) != len(seat_ids):
            missing_seat_ids = set(sid.value for sid in seat_ids) - set(s.id.value for s in seats)
            missing_seat_ids = [str(EventSeat.build_entity_id_from_uuid(seat_id)) for seat_id in missing_seat_ids]
            raise HTTPException(status_code=404, detail=f"Seats not found: {', '.join(missing_seat_ids)}")

        for seat in seats:
            if seat.event_id.value != event.id.value:
                raise HTTPException(
                    status_code=400,
                    detail=f"Seat {seat.id} does not belong to event {event.id}"
                )

        unavailable_seats = [s for s in seats if not s.is_available]
        if unavailable_seats:
            unavailable_seat_numbers = [s.seat_number for s in unavailable_seats]
            raise HTTPException(
                status_code=409,
                detail=f"One or more seats are already taken: {', '.join(unavailable_seat_numbers)}"
            )

        # TODO: add max tickets per user per event to prevent scalping/resale

        total_price = sum(s.price for s in seats)

        booking = Booking(
            id=Booking.generate_entity_id(),
            user_id=user_id,
            event_id=event.id,
            ticket_count=len(seats),
            total_price=total_price,
            currency="usd",
            status=BookingStatus.PENDING,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=config.BOOKING_RESERVATION_TTL_HOURS)
        )

        created_booking = await self._bookings_repository.create(booking)
        if not created_booking:
            raise HTTPException(status_code=500, detail="Failed to create booking")

        await self._event_seats_repository.mark_seats_as_unavailable(seat_ids)
        await self._booking_seated_tickets_repository.create_many(created_booking.id, seat_ids)
        await self._events_repository.decrement_available_tickets(event.id, booking.ticket_count)

        enriched = await self._enrich_bookings([created_booking])
        return enriched[0]

    async def _create_tiered_booking(
        self, user_id: EntityId, event: Event, booking_request: CreateBookingRequest
    ) -> BookingResponse:
        tier_entries = []
        for ticket_input in booking_request.tiered_tickets:
            tier_id = EntityId.from_string(ticket_input.tier_id)
            tier_entries.append((tier_id, ticket_input.count))

        tier_ids = [entry[0] for entry in tier_entries]
        tiers = await self._event_tiers_repository.get_by_ids_for_update(tier_ids)

        if len(tiers) != len(tier_ids):
            found_ids = {t.id.value for t in tiers}
            missing = [str(tid) for tid in tier_ids if tid.value not in found_ids]
            raise HTTPException(status_code=404, detail=f"Tiers not found: {', '.join(missing)}")

        tier_map = {t.id.value: t for t in tiers}
        for tier_id, _ in tier_entries:
            tier = tier_map[tier_id.value]
            if tier.event_id.value != event.id.value:
                raise HTTPException(
                    status_code=400,
                    detail=f"Tier {tier.id} does not belong to event {event.id}"
                )

        total_ticket_count = 0
        total_price = 0.0
        ticket_rows = []

        for tier_id, count in tier_entries:
            tier = tier_map[tier_id.value]
            # count <= 0 already handled by the Pydantic validator on CreateBookingRequest

            if count > tier.available_tickets:
                raise HTTPException(
                    status_code=409,
                    detail=f"Not enough tickets available for tier {tier.name}. "
                           f"Requested: {count}, Available: {tier.available_tickets}"
                )

            # decrement tier's available tickets
            await self._event_tiers_repository.decrement_available_tickets(tier.id, count)

            # this check will never fire, as we're already holding a lock on the tier, but may use in the future if logic changes
            # success = await self._event_tiers_repository.decrement_available_tickets(tier.id, count)
            # if not success:
            #     raise HTTPException(
            #         status_code=409,
            #         detail="Not enough tickets available to fulfill your request. Try booking fewer tickets."
            #     )

            unit_price = tier.price
            total_ticket_count += count
            total_price += unit_price * count

            for _ in range(count):
                ticket_rows.append({
                    "tier_id": tier.id,
                    "unit_price": unit_price,
                })

        # decrement event's available tickets
        await self._events_repository.decrement_available_tickets(event.id, total_ticket_count)

        booking = Booking(
            id=Booking.generate_entity_id(),
            user_id=user_id,
            event_id=event.id,
            ticket_count=total_ticket_count,
            total_price=total_price,
            currency="usd",
            status=BookingStatus.PENDING,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=config.BOOKING_RESERVATION_TTL_HOURS)
        )

        created_booking = await self._bookings_repository.create(booking)
        if not created_booking:
            raise HTTPException(status_code=500, detail="Failed to create booking")

        await self._booking_tiered_tickets_repository.create_many(created_booking.id, ticket_rows)

        enriched = await self._enrich_bookings([created_booking])
        return enriched[0]

    async def _enrich_bookings(self, bookings: list[Booking]) -> list[BookingResponse]:
        # This function populates the .seated_tickets, .tiered_tickets and .event field, returning a complete BookingResponse
        # To avoid N+1 problems, I ended up doing 4 constant DB calls (booking/s in the parent fn + 3 enrichment calls)
        # We fetch all the corresponding seated/tiered tickets and assemble everything after that
        # This is better than fetching all bookings in one call, then calling "get_event", "get_seated_tickets" etc. 
        # separately for each booking in a loop (1 initial call + N calls * 3 calls), causing A LOT of roundtrips
        if not bookings:
            return []
        
        event_ids = [b.event_id for b in bookings]
        booking_ids = [b.id for b in bookings]

        events = await self._events_repository.get_by_ids(event_ids)
        seated_tickets = await self._booking_seated_tickets_repository.get_seated_tickets_by_booking_ids(booking_ids)
        tiered_tickets = await self._booking_tiered_tickets_repository.get_tiered_tickets_by_booking_ids(booking_ids)
        
        # convert from Booking to BookingResponse model
        bookings = [BookingResponse.model_validate(booking, from_attributes=True) for booking in bookings]

        # create the booking mapping for O(1) hashmap access
        booking_mapping: dict[EntityId, Booking] = {}
        for booking in bookings:
            booking_mapping[booking.id] = booking
        
        # create the event mapping for O(1) hashmap access
        event_mapping: dict[EntityId, Event] = {}
        for event in events:
            event_mapping[event.id] = event

        # populate .seated_tickets
        for seated_ticket in seated_tickets:
            booking_id = seated_ticket.booking_id
            booking_mapping[booking_id].seated_tickets.append(seated_ticket)
        
        # populate .tiered_tickets
        for tiered_ticket in tiered_tickets:
            booking_id = tiered_ticket.booking_id
            booking_mapping[booking_id].tiered_tickets.append(tiered_ticket)

        # populate .event
        for booking in bookings:
            booking.event = event_mapping[booking.event_id]
        
        return bookings

    async def get_booking(self, user_id: EntityId, booking_id: EntityId) -> BookingResponse:
        booking = await self._bookings_repository.get_by_id(booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        if booking.user_id.value != user_id.value:
            raise HTTPException(status_code=403, detail="You are not allowed to view this booking")

        enriched = await self._enrich_bookings([booking])
        return enriched[0]

    async def get_user_bookings(self, user_id: EntityId) -> list[BookingResponse]:
        bookings = await self._bookings_repository.get_by_user_id(user_id)

        for booking in bookings:
            # lazy expiration
            if booking.status == BookingStatus.PENDING and booking.expires_at <= datetime.now(timezone.utc) - timedelta(minutes=1):
                # may also fetch the Stripe API to check the payment status
                # there may be a small time window after the user paid but the Stripe webhook did non arrive yet
                # used this 1 minute delay to account for any webhook delays, but an additional Stripe call may be even better
                await self._expire_booking(booking)
                await self.db_session.commit()  # commit early

        enriched = await self._enrich_bookings(bookings)
        return enriched

    async def create_payment_session(self, current_user: User, booking_id: EntityId) -> PaymentSessionResponse:
        booking = await self._bookings_repository.get_by_id_for_update(booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        if booking.user_id.value != current_user.id.value:
            raise HTTPException(status_code=403, detail="You are not allowed to access this booking")
        
        if booking.status != BookingStatus.PENDING:
             raise HTTPException(status_code=409, detail="Booking already confirmed/expired/cancelled")

        # lazy expiration
        if booking.expires_at <= datetime.now(timezone.utc) - timedelta(minutes=1):
            await self._expire_booking(booking)
            await self.db_session.commit()  # must commit before raising or the updates will get rolled back

            raise HTTPException(status_code=409, detail="Booking expired")

        existing_payment_session = await self._payments_repository.get_by_booking_id(booking_id)
        if existing_payment_session:
            return PaymentSessionResponse(
                checkout_url=existing_payment_session.stripe_checkout_url,
                session_id=existing_payment_session.stripe_checkout_session_id
            )

        event = await self._events_repository.get_by_id(booking.event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Event no longer exists")
        
        try:
            amount_cents = int(booking.total_price * 100)
            session = await stripe_client.v1.checkout.sessions.create_async(
                {
                    "mode": "payment",
                    "line_items": [
                        {
                            "price_data": {
                                "currency": "usd",
                                "unit_amount": amount_cents,
                                "product_data": {
                                    "name": f"Tickets - {event.name}",
                                    "description": f"{booking.ticket_count} ticket(s) for the event."
                                },
                            },
                            "quantity": 1,
                        }
                    ],
                    "success_url": f"{config.CORS.MAIN_ORIGIN}{config.STRIPE.SUCCESS_URL_PATH}?booking_id={str(booking_id)}",
                    "cancel_url": f"{config.CORS.MAIN_ORIGIN}{config.STRIPE.CANCEL_URL_PATH}",
                    "expires_at": int(booking.expires_at.timestamp()),
                    "client_reference_id": str(booking_id),
                    "customer_email": current_user.email,
                    "metadata": {"booking_id": str(booking_id)},  # accessible on session.* events
                    "payment_intent_data": {
                        "metadata": {"booking_id": str(booking_id)}  # accessible on payment_intent.* events
                    }
                }
            )
        except stripe.StripeError as e:
            raise HTTPException(status_code=400, detail=str(e))

        new_payment = Payment(
            id=Payment.generate_entity_id(),
            booking_id=booking_id,
            stripe_checkout_session_id=session.id,
            stripe_checkout_url=session.url,
            stripe_payment_intent_id=None,
            amount_cents=amount_cents,
            currency=booking.currency,
            status=PaymentStatus.PENDING
        )
        await self._payments_repository.create(new_payment)

        return PaymentSessionResponse(
            checkout_url=session.url,
            session_id=session.id
        )

    # will be called by the Stripe webhook, MUST return status 2xx
    async def confirm_booking(self, booking_id: EntityId, stripe_session_id: str, stripe_payment_intent_id: str):
        booking = await self._bookings_repository.get_by_id_for_update(booking_id)
        if not booking:
            return
        
        # Allow only pending -> confirmed (network errors may result in the webhook being called twice)
        if booking.status != BookingStatus.PENDING:
            return

        # update booking status
        booking.status = BookingStatus.CONFIRMED
        booking.expires_at = None
        await self._bookings_repository.update(booking_id, booking)

        # update payment status and set the payment_intent_id
        payment = await self._payments_repository.get_by_stripe_session_id(stripe_session_id)
        payment.status = PaymentStatus.SUCCEEDED
        payment.stripe_payment_intent_id = stripe_payment_intent_id
        await self._payments_repository.update(payment.id, payment)

        # create the tickets
        await self._create_tickets(booking)

    async def _create_tickets(self, booking: Booking):
        enriched = await self._enrich_bookings([booking])
        enriched_booking = enriched[0]
        
        if enriched_booking.seated_tickets:
            tickets = [
                Ticket(
                    id=Ticket.generate_entity_id(),
                    booking_id=booking.id,
                    event_id=booking.event_id,
                    seat_id=seat.id,
                    tier_id=None,
                    status=TicketStatus.UNUSED,
                    checked_in_at=None
                ) for seat in enriched_booking.seated_tickets
            ]
        elif enriched_booking.tiered_tickets:
            tickets = [
                Ticket(
                    id=Ticket.generate_entity_id(),
                    booking_id=booking.id,
                    event_id=booking.event_id,
                    seat_id=None,
                    tier_id=tier.id,
                    status=TicketStatus.UNUSED,
                    checked_in_at=None
                ) for tier in enriched_booking.tiered_tickets
            ]

        await self._tickets_repository.create_many(tickets)

    async def _release_booking_resources(self, booking: Booking, throw = True):
        event = await self._events_repository.get_by_id(booking.event_id)
        if not event:
            if not throw:
                return
            raise HTTPException(status_code=404, detail="Event no longer exists")

        if event.event_type == EventType.SEATED:
            seated_tickets = await self._booking_seated_tickets_repository.get_seated_tickets_by_booking_ids([booking.id])
            seat_ids = [seated_ticket.id for seated_ticket in seated_tickets]
            if seat_ids:
                await self._event_seats_repository.mark_seats_as_available(seat_ids)
                await self._booking_seated_tickets_repository.delete_by_booking_id(booking.id)
                await self._events_repository.increment_available_tickets(event.id, booking.ticket_count)

        elif event.event_type == EventType.TIERED:
            tiered_tickets = await self._booking_tiered_tickets_repository.get_tiered_tickets_by_booking_ids([booking.id])

            tier_counts = Counter(tt.tier_id.value for tt in tiered_tickets)
            for tier_uuid, count in tier_counts.items():
                tier_id = EventTier.build_entity_id_from_uuid(tier_uuid)
                await self._event_tiers_repository.increment_available_tickets(tier_id, count)
            await self._booking_tiered_tickets_repository.delete_by_booking_id(booking.id)
            await self._events_repository.increment_available_tickets(event.id, booking.ticket_count)

    async def _expire_booking(self, booking: Booking, throw: bool = True):
        booking.status = BookingStatus.EXPIRED
        await self._bookings_repository.update(booking.id, booking)

        await self._release_booking_resources(booking, throw=throw)  # make sure to not throw

        # will not run if the user never clicked Pay Now and did not creat a Checkout Session
        payment = await self._payments_repository.get_by_booking_id(booking.id)
        if payment:
            payment.status = PaymentStatus.EXPIRED
            await self._payments_repository.update(payment.id, payment)

    # will be called by the Stripe webhook, MUST return status 2xx
    async def expire_booking_stripe(self, booking_id: EntityId, stripe_session_id: str):
        booking = await self._bookings_repository.get_by_id_for_update(booking_id)
        if not booking:
            return

        # Return (status 200) if booking was already confirmed/expired/cancelled
        if booking.status != BookingStatus.PENDING:
            return
        
        # ended up not using stripe_session_id, as we can fetch the payment row by booking id
        # we can do this because we have the 1 payment row for 1 booking row business rule
        await self._expire_booking(booking, throw=False)

    # will be called by the user
    async def cancel_booking(self, user_id: EntityId, booking_id: EntityId) -> BookingResponse:
        booking = await self._bookings_repository.get_by_id_for_update(booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        if booking.user_id.value != user_id.value:
            raise HTTPException(status_code=403, detail="You are not allowed to cancel this booking")

        if booking.status == BookingStatus.CANCELLED:
            raise HTTPException(status_code=400, detail="Booking already cancelled")
        
        if booking.status != BookingStatus.PENDING:
            # For now, the user will be able to cancel only pending booking
            # Confirmed bookings will not be cancellable (this already requires a refund, may be implemented later)
             raise HTTPException(status_code=409, detail="You cannot cancel this booking")

        # If a Stripe checkout session exists, expire it manually
        existing_payment_session = await self._payments_repository.get_by_booking_id(booking_id)
        if existing_payment_session:
            try:
                await stripe_client.v1.checkout.sessions.expire_async(existing_payment_session.stripe_checkout_session_id)
            except stripe.StripeError as e:
                # do not cancel if we get a Stripe error, as the payment already succeeded or the session expired
                raise HTTPException(status_code=400, detail="The booking is already confirmed/expired")
            
            existing_payment_session.status = PaymentStatus.EXPIRED
            await self._payments_repository.update(existing_payment_session.id, existing_payment_session)

        await self._release_booking_resources(booking)

        booking.status = BookingStatus.CANCELLED
        booking.expires_at = None
        updated_booking = await self._bookings_repository.update(booking_id, booking)

        enriched = await self._enrich_bookings([updated_booking])
        return enriched[0]