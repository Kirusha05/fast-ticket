import type { EventSeat } from "@/features/events/types";
import { useNewBookingStore } from "../../stores/useNewBookingStore";
import { cn } from "@/lib/utils";

// Parse a seat number like "A1" → { row: 0, col: 0 }, "AA3" → { row: 26, col: 2 }
export function parseSeatNumber(sn: string): { row: number; col: number } {
  const m = sn.match(/^([A-Z]+)(\d+)$/);
  if (!m) throw new Error(`Invalid seat number: ${sn}`);
  let row = 0;
  for (let i = 0; i < m[1].length; i++) {
    row = row * 26 + (m[1].charCodeAt(i) - 64);
  }
  return { row: row - 1, col: parseInt(m[2], 10) - 1 };
}

// Cycled across distinct price tiers so seats of the same price share a color.
const PRICE_COLORS = [
  "#ef4444", "#3b82f6", "#22c55e", "#f59e0b",
  "#a855f7", "#ec4899", "#14b8a6", "#6366f1",
];

/**
 * One { price, color } entry per distinct price, sorted cheapest-first.
 * The first palette color always maps to the cheapest tier, regardless of
 * the order seats arrive in.
 */
function buildPriceLegend(seats: EventSeat[]) {
  const prices = [...new Set(seats.map((s) => s.price))].sort((a, b) => a - b);
  return prices.map((price, i) => ({
    price,
    color: PRICE_COLORS[i % PRICE_COLORS.length],
  }));
}

interface IProps {
  seats: EventSeat[];
};

export function SeatSelector({ seats }: IProps) {
  const selectedSeatIds = useNewBookingStore((s) => s.selectedSeatIds);
  const toggleSeat = useNewBookingStore((s) => s.toggleSeat);

  // One color per distinct price: `legend` lists them (for the key above the
  // grid), `colorByPrice` looks a single seat's price up in O(1).
  const legend = buildPriceLegend(seats);
  const colorByPrice: Record<number, string> = {};
  for (const { price, color } of legend) colorByPrice[price] = color;

  // Index seats by "row:col" for direct grid lookup, and track the grid bounds
  // from the highest row/col seen across all seats.
  const seatMap: Record<string, EventSeat> = {};
  let totalRows = 0;
  let totalCols = 0;
  for (const seat of seats) {
    const { row, col } = parseSeatNumber(seat.seat_number);
    seatMap[`${row}:${col}`] = seat;
    if (row + 1 > totalRows) totalRows = row + 1;
    if (col + 1 > totalCols) totalCols = col + 1;
  }

  return (
    <div className="space-y-4">
      {/* Price legend */}
      <div className="flex flex-wrap items-center gap-4">
        {legend.map(({ price, color }) => (
          <div key={price} className="flex items-center gap-1.5 text-xs">
            <div
              className="h-3 w-3 rounded-sm"
              style={{ backgroundColor: color }}
            />
            <span className="text-muted-foreground">
              ${price.toFixed(2)}
            </span>
          </div>
        ))}
      </div>

      {/* Seat grid */}
      <div
        className="grid gap-1.5"
        style={{
          gridTemplateColumns: `repeat(${totalCols}, minmax(0, 1fr))`,
        }}
      >
        {Array.from({ length: totalRows }, (_, r) =>
          Array.from({ length: totalCols }, (_, c) => {
            const seat = seatMap[`${r}:${c}`];
            if (!seat) {
              // Empty cell (no seat at this position)
              return <div key={`${r}-${c}`} />;
            }

            const isOccupied = !seat.is_available;
            const isSelected = selectedSeatIds.includes(seat.id);
            const color = colorByPrice[seat.price];

            return (
              <button
                key={seat.id}
                type="button"
                disabled={isOccupied}
                onClick={() => toggleSeat(seat.id)}
                title={`${seat.seat_number} — $${seat.price.toFixed(2)}${
                  isOccupied ? " (taken)" : ""
                }`}
                className={cn(
                  "aspect-square rounded-sm border text-[10px] font-medium transition-all",
                  isOccupied
                    ? "border-transparent opacity-20 cursor-not-allowed"
                    : "cursor-pointer border-border hover:opacity-80",
                  isSelected &&
                    "ring-1 ring-foreground ring-offset-1 ring-offset-background opacity-80 hover:opacity:80",
                )}
                style={{
                  backgroundColor: color
                }}
              >
                {seat.seat_number}
              </button>
            );
          }),
        )}
      </div>
    </div>
  );
}