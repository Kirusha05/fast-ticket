import { useCreateEventStore } from "../../../stores/useCreateEventStore";
import { seatNumber } from "../utils";

export function SeatGrid() {
  const rows = useCreateEventStore((s) => s.rows);
  const cols = useCreateEventStore((s) => s.cols);
  const seatAssignments = useCreateEventStore((s) => s.seatAssignments);
  const seatedTiers = useCreateEventStore((s) => s.seatedTiers);
  const assignSeat = useCreateEventStore((s) => s.assignSeat);

  const tierById = new Map(seatedTiers.map((t) => [t.id, t]));

  return (
    <div
      className="grid gap-1"
      style={{
        gridTemplateColumns: `repeat(${cols}, minmax(0, 1fr))`,
      }}
    >
      {Array.from({ length: rows }, (_, r) =>
        Array.from({ length: cols }, (_, c) => {
          const tierId = seatAssignments[r]?.[c] ?? null;
          const tier = tierId ? tierById.get(tierId) : undefined;
          return (
            <button
              key={`${r}-${c}`}
              type="button"
              onClick={() => assignSeat(r, c)}
              title={`${seatNumber(r, c)}${tier ? ` — $${tier.price.toFixed(2)}` : " — unassigned"}`}
              className="aspect-square rounded-sm border border-border text-[10px] font-medium transition-colors hover:opacity-80"
              style={{
                backgroundColor: tier?.color ?? "hsl(var(--muted))",
                color: tier ? "#fff" : "hsl(var(--muted-foreground))",
              }}
            >
              {seatNumber(r, c)}
            </button>
          );
        }),
      )}
    </div>
  );
}