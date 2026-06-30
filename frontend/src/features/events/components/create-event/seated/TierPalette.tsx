import { useCreateEventStore } from "../../../stores/useCreateEventStore";
import { Button } from "@/components/ui";
import { X } from "lucide-react";

export function TierPalette() {
  const seatedTiers = useCreateEventStore((s) => s.seatedTiers);
  const selectedTierId = useCreateEventStore((s) => s.selectedTierId);
  const selectTier = useCreateEventStore((s) => s.selectTier);
  const addSeatedTier = useCreateEventStore((s) => s.addSeatedTier);
  const updateSeatedTier = useCreateEventStore((s) => s.updateSeatedTier);
  const removeSeatedTier = useCreateEventStore((s) => s.removeSeatedTier);

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Tiers</h3>
        <Button
          type="button"
          size="sm"
          onClick={addSeatedTier}
        >
          + Add tier
        </Button>
      </div>

      {seatedTiers.length === 0 && (
        <p className="text-xs text-muted-foreground">
          No tiers yet. Add a tier to price seats.
        </p>
      )}

      <div className="space-y-2">
        {seatedTiers.map((tier) => (
          <div
            key={tier.id}
            onClick={() => selectTier(tier.id)}
            className={`flex items-center gap-2 rounded-md border p-2 transition-colors cursor-pointer ${
              selectedTierId === tier.id
                ? "border-primary ring-1 ring-primary"
                : "border-border hover:border-muted-foreground"
            }`}
          >
            <div
              className="h-5 w-5 shrink-0 rounded"
              style={{ backgroundColor: tier.color }}
            />
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={tier.name}
                onChange={(e) => updateSeatedTier(tier.id, { name: e.target.value })}
                onClick={(e) => e.stopPropagation()}
                placeholder="Tier name"
                className="h-6 w-1/2 rounded border border-border bg-transparent px-2 text-xs font-medium focus:outline-none focus:ring-1 focus:ring-primary"
              />
              <span className="text-sm text-muted-foreground">$</span>
              <input
                type="number"
                value={tier.price || ""}
                onChange={(e) =>
                  updateSeatedTier(tier.id, { price: parseFloat(e.target.value) || 0 })
                }
                onClick={(e) => e.stopPropagation()}
                placeholder="0.00"
                min={0}
                step={0.01}
                className="h-6 w-20 rounded border border-border bg-transparent px-1 text-xs focus:outline-none focus:ring-1 focus:ring-primary"
              />
            </div>
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                removeSeatedTier(tier.id);
              }}
              className="shrink-0 hover:text-destructive cursor-pointer"
              title="Remove tier"
            >
              <X size={14} />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}