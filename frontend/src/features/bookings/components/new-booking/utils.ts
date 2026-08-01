import { EventType } from "@/features/events/types";
import type { Event, EventSeat, EventTier } from "@/features/events/types";
import type { Booking, CreateBookingRequest } from "../../types";

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
 *  - TIERED: the sum of all tier counts
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
 *  - TIERED → { event_id, tiered_tickets: [{ tier_id, count }] }
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
    .filter(([, count]) => count > 0)
    .map(([tier_id, count]) => ({ tier_id, count }));

  return { event_id: event.id, tiered_tickets };
}


export const usd = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
});

export function ticketSummary(booking: Booking) {
  if (booking.seated_tickets.length > 0) {
    return booking.seated_tickets
      .map((s) => `${s.seat_number} (${usd.format(s.price)})`)
      .join(", ");
  }

  if (booking.tiered_tickets.length > 0) {
    const grouped = booking.tiered_tickets.reduce(
      (acc, t) => {
        const key = `${t.tier_name}::${t.unit_price}`;
        if (!acc[key])
          acc[key] = { name: t.tier_name, price: t.unit_price, count: 0 };
        acc[key].count += 1;
        return acc;
      },
      {} as Record<string, { name: string; price: number; count: number }>,
    );
    return Object.values(grouped)
      .map((g) => `${g.name} × ${g.count} at ${usd.format(g.price)} each`)
      .join(", ");
  }

  return null;
}