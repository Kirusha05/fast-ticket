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

export interface Booking {
  id: string;
  status: string;
  ticket_count: number;
  total_price: number;
  event_id: string;

  event: Event;
  seated_tickets: BookingEventSeat[];
  tiered_tickets: BookingEventTier[];

  created_at: string;
  updated_at: string;
};

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