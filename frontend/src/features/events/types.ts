export enum EventType {
  OPEN_FIELD = "open_field",
  SEATED = "seated",
}

export type SearchEventType = "open_field" | "seated" | undefined;

export interface EventSeat {
  id: string;
  event_id: string;
  seat_number: string;
  price: number;
  is_available: boolean;

  created_at: string;
  updated_at: string;
};

export interface EventTier {
  id: string;
  event_id: string;
  name: string;
  price: number;
  total_tickets: number;
  available_tickets: number;

  created_at: string;
  updated_at: string;
};

export interface Event {
  id: string;
  name: string;
  description: string;
  venue: string;
  event_date: string;
  event_type: EventType;
  banner_url: string;
  total_tickets: number;
  available_tickets: number;

  seats: EventSeat[];
  tiers: EventTier[];

  created_at: string;
  updated_at: string;
};

// API types
export interface EventSeatInput {
  seat_number: string;
  price: number;
};

export interface EventTierInput {
  name: string;
  price: number;
  total_tickets: number;
};

export interface CreateEventRequest {
  name: string;
  description: string;
  venue: string;
  event_date: string;
  event_type: EventType;
  banner_url: string;
  seats: EventSeatInput[];
  tiers: EventTierInput[];
};

export interface UpdateEventRequest {
  name: string | undefined;
  description: string | undefined;
  venue: string | undefined;
  event_date: string | undefined;
  banner_url: string | undefined;
};
