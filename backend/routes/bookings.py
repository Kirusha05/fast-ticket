from fastapi import APIRouter, Depends, status
from usecases import BookingsUseCase
from config.db_session import get_db_session
from routes.deps.auth import get_current_user
from models import Booking, CreateBookingRequest, User


router = APIRouter()


@router.get("/")
async def get_all_bookings(
    db=Depends(get_db_session),
    user: User = Depends(get_current_user),
):
    bookings_use_case = BookingsUseCase(db)
    return await bookings_use_case.list_user_bookings(user.id)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking: CreateBookingRequest,
    db=Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> Booking:
    bookings_use_case = BookingsUseCase(db)
    result = await bookings_use_case.create(user.id, booking)
    return result
