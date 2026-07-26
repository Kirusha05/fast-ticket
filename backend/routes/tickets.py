from fastapi import APIRouter, Depends
from usecases import TicketsUseCase
from config.db_session import get_db_session
from models import User, EntityId, ValidateTicketRequest
from routes.deps.auth import get_current_user


router = APIRouter()

@router.get("/{booking_id}")
async def get_booking_tickets(
    booking_id: str,
    db=Depends(get_db_session),
    user: User = Depends(get_current_user)
):
    booking_id = EntityId.from_string(booking_id)
    tickets_use_case = TicketsUseCase(db)
    result = await tickets_use_case.get_booking_tickets(user.id, booking_id)
    return result

@router.post("/validate")
async def validate_ticket(
    validate_req: ValidateTicketRequest,
    db=Depends(get_db_session),
    user: User = Depends(get_current_user)
):
    tickets_use_case = TicketsUseCase(db)
    result = await tickets_use_case.validate_ticket(user, validate_req)
    return result