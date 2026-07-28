export enum TicketStatus {
  UNUSED = "unused",
  USED = "used",
}

export interface Ticket {
    id: string;
    booking_id: string;
    event_id: string;
    seat_id: string | null;
    tier_id: string | null; 

    status: TicketStatus
    checked_in_at: string | null;

    seat_number: string | null;
    seat_price: number | null;
    tier_name: string | null;
    tier_price: number | null;

    created_at: string;
    updated_at: string;
}

export interface ValidateTicketRequest {
    ticket_id: string;
}