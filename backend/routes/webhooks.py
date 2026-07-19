from fastapi import APIRouter, Depends, Header, Request, HTTPException
from usecases import BookingsUseCase
from config.db_session import get_db_session
from config.config import config
import stripe
from models import EntityId


router = APIRouter()

@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    db = Depends(get_db_session),
    stripe_signature: str = Header(None, alias="stripe-signature"),
):
    # Stripe requires the raw request body (not parsed JSON) to verify the signature.
    payload = await request.body()

    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, config.STRIPE.WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    event_type = event.type
    print(f"STRIPE EVENT TYPE: {event_type}")
    data = event.data.object
    
    bookings_use_case = BookingsUseCase(db)

    # Decide your policy: do expired-then-paid bookings get confirmed, or refunded?

    # That's a good question. However since you're only using cards for payment options it may be better to set the payment expiration to be 31 or 32 minutes and have the user facing UI time out and prevent starting payment at the 30 minute mark.

    if event_type == "checkout.session.completed":
        stripe_session_id = data["id"]
        booking_id_raw = data["metadata"]["booking_id"]
        booking_id = EntityId.from_string(booking_id_raw)
        stripe_payment_intent_id = data["payment_intent"]
        await bookings_use_case.confirm_booking(booking_id, stripe_session_id, stripe_payment_intent_id)

    elif event_type == "checkout.session.expired":
        stripe_session_id = data["id"]
        booking_id_raw = data["metadata"]["booking_id"]
        booking_id = EntityId.from_string(booking_id_raw)
        await bookings_use_case.expire_booking(booking_id, stripe_session_id)

    # always return with status 200 (data doesn't matter) so Stripe doesn't keep retrying events we've already handled
    return { "success": True }
    