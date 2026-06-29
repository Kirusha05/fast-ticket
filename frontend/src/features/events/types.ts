export enum EventType {
  OPEN_FIELD = "open_field",
  SEATED = "seated",
}

export type SearchEventType = "open_field" | "seated" | undefined;

export type EventSeat = {
  id: string;
  event_id: string;
  seat_number: string;
  price: number;
  is_available: boolean;

  created_at: string;
  updated_at: string;
};

export type EventTier = {
  id: string;
  event_id: string;
  name: string;
  price: number;
  total_tickets: number;
  available_tickets: number;

  created_at: string;
  updated_at: string;
};

export type Event = {
  id: string;
  name: string;
  description: string;
  venue: string;
  event_date: string;
  event_type: EventType;
  total_tickets: number;
  available_tickets: number;

  seats: EventSeat[];
  tiers: EventTier[];

  created_at: string;
  updated_at: string;
};

// API types
export type EventSeatInput = {
  seat_number: string;
  price: number;
};

export type EventTierInput = {
  name: string;
  price: number;
  total_tickets: number;
};

export type CreateEventRequest = {
  name: string;
  description: string;
  venue: string;
  event_date: string;
  event_type: EventType;
  seats: EventSeatInput[];
  tiers: EventTierInput[];
};

export type UpdateEventRequest = {
  name: string | undefined;
  description: string | undefined;
  venue: string | undefined;
  event_date: string | undefined;
};
