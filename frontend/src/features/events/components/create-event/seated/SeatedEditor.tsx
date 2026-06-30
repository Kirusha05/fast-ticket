import { useCreateEventStore } from "../../../stores/useCreateEventStore";
import { SeatGrid } from "./SeatGrid";
import { TierPalette } from "./TierPalette";
import { Input, Button, Label } from "@/components/ui";

export function SeatedEditor() {
  const rows = useCreateEventStore((s) => s.rows);
  const cols = useCreateEventStore((s) => s.cols);
  const gridConfirmed = useCreateEventStore((s) => s.gridConfirmed);
  const seatedTiers = useCreateEventStore((s) => s.seatedTiers);
  const setRows = useCreateEventStore((s) => s.setRows);
  const setCols = useCreateEventStore((s) => s.setCols);
  const confirmGrid = useCreateEventStore((s) => s.confirmGrid);
  const resetGrid = useCreateEventStore((s) => s.resetGrid);

  if (!gridConfirmed) {
    return (
      <div className="space-y-4">
        <div className="flex items-end gap-4">
          <div className="space-y-1.5">
            <Label htmlFor="rows">Rows</Label>
            <Input
              id="rows"
              type="number"
              min={1}
              max={50}
              value={rows}
              onChange={(e) => setRows(Math.max(1, parseInt(e.target.value) || 1))}
              className="w-24"
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="cols">Columns</Label>
            <Input
              id="cols"
              type="number"
              min={1}
              max={50}
              value={cols}
              onChange={(e) => setCols(Math.max(1, parseInt(e.target.value) || 1))}
              className="w-24"
            />
          </div>
          <Button type="button" onClick={confirmGrid}>
            Confirm
          </Button>
        </div>
        {rows > 0 && cols > 0 && (
          <p className="text-xs text-muted-foreground">
            {rows} rows &times; {cols} columns = {rows * cols} seats
          </p>
        )}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-xs text-muted-foreground">
          {rows} rows &times; {cols} columns &mdash;{" "}
          {seatedTiers.length} tier{seatedTiers.length !== 1 ? "s" : ""}
        </p>
        <Button
          type="button"
          onClick={resetGrid}
          size="sm"
        >
          Reset grid
        </Button>
      </div>
      <p className="text-xs text-muted-foreground">
        Select a tier, then click seats to price them. Click a priced seat again to clear.
      </p>
      <div className="grid grid-cols-[1fr_280px] gap-4">
        <SeatGrid />
        <TierPalette />
      </div>
    </div>
  );
}