import { type Event } from "@/features/events/types";

export interface BookingEventSeat {
  id: string;
  seat_number: string;
  price: number;
  booking_id: string;
  is_available: boolean;
};

export interface BookingEventTier {
  id: string;
  tier_name: string;
  unit_price: number;
  booking_id: string;
  tier_id: string;
};

export type BookingStatus = "pending" | "confirmed" | "payment_failed" | "expired" | "cancelled"

export interface Booking {
  id: string;
  event_id: string;
  ticket_count: number;
  total_price: number;
  currency: string;
  status: BookingStatus;
  expires_at: string | null;

  event: Event;
  seated_tickets: BookingEventSeat[];
  tiered_tickets: BookingEventTier[];

  created_at: string;
  updated_at: string;
};

export interface PaymentSessionResponse {
  checkout_url: string;
  session_id: string;
}

// API request types
export interface TicketInput {
  tier_id: string;
  count: number;
};

export interface CreateBookingRequest {
  event_id: string;
  seat_ids?: string[];
  tiered_tickets?: TicketInput[];
};