import { EventType } from "@/features/events/types";
import type { Event, EventSeat, EventTier } from "@/features/events/types";
import type { CreateBookingRequest } from "../../types";

/**
 * Sum the prices of the selected seats. Seats are indexed by id first so each
 * lookup is O(1) instead of scanning the array per seat.
 */
export function sumSeatsPrice(
  seats: EventSeat[],
  selectedSeatIds: string[],
): number {
  const seatById: Record<string, EventSeat> = {};
  for (const seat of seats) seatById[seat.id] = seat;

  return selectedSeatIds.reduce(
    (sum, id) => sum + (seatById[id]?.price ?? 0),
    0,
  );
}

/**
 * Sum `price * count` for every tier that currently has a positive count.
 */
export function sumTiersPrice(
  tiers: EventTier[],
  tierCounts: Record<string, number>,
): number {
  const tierById: Record<string, EventTier> = {};
  for (const tier of tiers) tierById[tier.id] = tier;

  return Object.entries(tierCounts).reduce((sum, [id, count]) => {
    const tier = tierById[id];
    return sum + (tier ? tier.price * count : 0);
  }, 0);
}

/**
 * How many tickets the current selection represents:
 *  - SEATED: one per selected seat
 *  - OPEN_FIELD: the sum of all tier counts
 */
export function countTickets(
  event: Event,
  selectedSeatIds: string[],
  tierCounts: Record<string, number>,
): number {
  if (event.event_type === EventType.SEATED) return selectedSeatIds.length;
  return Object.values(tierCounts).reduce((sum, c) => sum + c, 0);
}

/**
 * Build the POST /bookings body from the current selection.
 *  - SEATED     → { event_id, seat_ids }
 *  - OPEN_FIELD → { event_id, tiered_tickets: [{ tier_id, count }] }
 *    (tiers with a count of 0 are dropped — the backend rejects empty entries)
 */
export function buildBookingRequest(
  event: Event,
  selectedSeatIds: string[],
  tierCounts: Record<string, number>,
): CreateBookingRequest {
  if (event.event_type === EventType.SEATED) {
    return { event_id: event.id, seat_ids: selectedSeatIds };
  }

  // Tiered
  const tiered_tickets = Object.entries(tierCounts)
    .filter(([_, count]) => count > 0)
    .map(([tier_id, count]) => ({ tier_id, count }));

  return { event_id: event.id, tiered_tickets };
}
