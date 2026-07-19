from fastapi import APIRouter, Depends, status
from usecases import BookingsUseCase
from config.db_session import get_db_session
from routes.deps.auth import get_current_user
from models import CreateBookingRequest, EntityId, User, BookingResponse, PaymentSessionResponse


router = APIRouter()


@router.get("")
async def get_all_bookings(
    db=Depends(get_db_session),
    user: User = Depends(get_current_user),
):
    bookings_use_case = BookingsUseCase(db)
    return await bookings_use_case.get_user_bookings(user.id)


@router.get("/{booking_id}")
async def get_booking(
    booking_id: str,
    db=Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> BookingResponse:
    bookings_use_case = BookingsUseCase(db)
    booking_id = EntityId.from_string(booking_id)
    return await bookings_use_case.get_booking(user.id, booking_id)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking: CreateBookingRequest,
    db=Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> BookingResponse:
    bookings_use_case = BookingsUseCase(db)
    return await bookings_use_case.create_booking(user, booking)


@router.post("/{booking_id}/payment", status_code=status.HTTP_201_CREATED)
async def create_payment_session(
    booking_id: str,
    db=Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> PaymentSessionResponse:
    bookings_use_case = BookingsUseCase(db)
    booking_id = EntityId.from_string(booking_id)
    return await bookings_use_case.create_payment_session(user, booking_id)


@router.post("/{booking_id}/cancel")
async def cancel_booking(
    booking_id: str,
    db=Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> BookingResponse:
    bookings_use_case = BookingsUseCase(db)
    booking_id = EntityId.from_string(booking_id)
    return await bookings_use_case.cancel_booking(user.id, booking_id)
