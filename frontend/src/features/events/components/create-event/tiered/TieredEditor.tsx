import { useCreateEventStore } from "../../../stores/useCreateEventStore";
import { Input, Label, Button } from "@/components/ui";

export function TiersEditor() {
  const tiers = useCreateEventStore((s) => s.tiers);
  const addTier = useCreateEventStore((s) => s.addTier);
  const updateTier = useCreateEventStore((s) => s.updateTier);
  const removeTier = useCreateEventStore((s) => s.removeTier);

  const totalTickets = tiers.reduce((sum, t) => sum + (t.totalTickets || 0), 0);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-sm">Edit the available ticket tiers for this event.</p>
        <Button type="button" variant="outline" size="sm" onClick={addTier}>
          + Add tier
        </Button>
      </div>

      {tiers.length === 0 && (
        <p className="text-sm text-muted-foreground">
          No tiers yet. Add at least one tier with a name, price, and ticket quantity.
        </p>
      )}

      <div className="space-y-3">
        {tiers.map((tier) => (
          <div
            key={tier.id}
            className="flex items-end gap-3 rounded-md border border-border p-3"
          >
            <div className="space-y-1.5 flex-1">
              <Label htmlFor={`of-name-${tier.id}`} className="text-xs">
                Name
              </Label>
              <Input
                id={`of-name-${tier.id}`}
                type="text"
                value={tier.name}
                onChange={(e) =>
                  updateTier(tier.id, { name: e.target.value })
                }
                placeholder="e.g. General Admission"
              />
            </div>
            <div className="space-y-1.5 w-28">
              <Label htmlFor={`of-price-${tier.id}`} className="text-xs">
                Price ($)
              </Label>
              <Input
                id={`of-price-${tier.id}`}
                type="number"
                value={tier.price || ""}
                onChange={(e) =>
                  updateTier(tier.id, {
                    price: parseFloat(e.target.value) || 0,
                  })
                }
                placeholder="0.00"
                min={0}
                step={0.01}
              />
            </div>
            <div className="space-y-1.5 w-28">
              <Label htmlFor={`of-qty-${tier.id}`} className="text-xs">
                Tickets
              </Label>
              <Input
                id={`of-qty-${tier.id}`}
                type="number"
                value={tier.totalTickets || ""}
                onChange={(e) =>
                  updateTier(tier.id, {
                    totalTickets: parseInt(e.target.value) || 0,
                  })
                }
                placeholder="0"
                min={0}
                step={1}
              />
            </div>
            <button
              type="button"
              onClick={() => removeTier(tier.id)}
              className="mb-0.5 text-muted-foreground hover:text-destructive shrink-0"
              title="Remove tier"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth={2}
                className="h-4 w-4"
              >
                <path d="M18 6L6 18M6 6l12 12" />
              </svg>
            </button>
          </div>
        ))}
      </div>

      <p className="text-sm text-muted-foreground">
        Total tickets: <strong>{totalTickets}</strong>
      </p>
    </div>
  );
}