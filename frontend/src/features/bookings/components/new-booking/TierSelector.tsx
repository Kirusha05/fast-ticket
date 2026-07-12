import type { EventTier } from "@/features/events/types";
import { useNewBookingStore } from "../../stores/useNewBookingStore";
import { Minus, Plus } from "lucide-react";
import { cn } from "@/lib/utils";

type TierSelectorProps = {
  tiers: EventTier[];
};

export function TierSelector({ tiers }: TierSelectorProps) {
  const tierCounts = useNewBookingStore((s) => s.tierCounts);
  const setTierCount = useNewBookingStore((s) => s.setTierCount);

  if (tiers.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">
        No tickets available for this event.
      </p>
    );
  }

  return (
    <div className="space-y-3">
      {tiers.map((tier) => {
        const count = tierCounts[tier.id] ?? 0;
        const canIncrement = count < tier.available_tickets;

        return (
          <div
            key={tier.id}
            className="flex items-center justify-between rounded-lg border border-border p-4"
          >
            {/* Left: tier info */}
            <div className="min-w-0 space-y-0.5">
              <p className="text-sm font-medium">{tier.name}</p>
              <p className="text-xs text-muted-foreground">
                ${tier.price.toFixed(2)} / ticket &middot;{" "}
                {tier.available_tickets} available
              </p>
            </div>

            {/* Right: counter */}
            <div className="flex items-center gap-2">
              <button
                type="button"
                disabled={count <= 0}
                onClick={() => setTierCount(tier.id, count - 1)}
                className={cn(
                  "flex h-8 w-8 items-center justify-center rounded-md border border-border transition-colors",
                  count <= 0
                    ? "cursor-not-allowed opacity-40"
                    : "hover:bg-muted cursor-pointer",
                )}
                aria-label={`Decrease ${tier.name} count`}
              >
                <Minus className="h-4 w-4" />
              </button>

              <span className="flex h-8 w-10 items-center justify-center rounded-md border border-border bg-muted/30 text-sm font-semibold tabular-nums">
                {count}
              </span>

              <button
                type="button"
                disabled={!canIncrement}
                onClick={() => setTierCount(tier.id, count + 1)}
                className={cn(
                  "flex h-8 w-8 items-center justify-center rounded-md border border-border transition-colors",
                  !canIncrement
                    ? "cursor-not-allowed opacity-40"
                    : "hover:bg-muted cursor-pointer",
                )}
                aria-label={`Increase ${tier.name} count`}
              >
                <Plus className="h-4 w-4" />
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
}