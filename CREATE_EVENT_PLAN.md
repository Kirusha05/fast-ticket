# Create Event — Implementation Plan

Goal: Implement the "Create Event" flow. A **"New"** button on `/events` navigates to a new page `/events/create` where an admin picks an event type (**seated** or **open field**), configures it, and submits via the existing `useCreateEvent` mutation against `POST /events`.

This plan is self-contained. The implementing agent should follow it in order. All file paths are relative to `frontend/`.

---

## 0. Critical context the agent MUST understand before coding

The backend `CreateEventRequest` (see `backend/models/event.py`) is:

```python
class CreateEventRequest(BaseModel):
    name: str
    description: str
    venue: str
    event_date: datetime
    event_type: EventType              # "seated" | "open_field"
    seats: list[EventSeatInput] = []   # { seat_number: str, price: float }
    tiers: list[EventTierInput] = []   # { name: str, price: float, total_tickets: int }

    @model_validator(mode='after')
    def validate_event_type(self):
        if self.event_type == EventType.SEATED and not self.seats:
            raise ValueError("Seated events require seats")
        if self.event_type == EventType.OPEN_FIELD and not self.tiers:
            raise ValueError("Open field events require tiers")
        return self
```

**Two different payload shapes depending on type:**

- **SEATED** → send `seats: [{ seat_number, price }]`, `tiers: []`.
  - The "tiers" in the seated UI are a **client-side price-painting tool only**. They do NOT go to the backend. On submit, each seat's assigned tier price is flattened into `seat.price`.
  - `seat_number` is `VARCHAR(10)` in the DB — keep labels short (e.g. `A1`, `B12`).
  - Backend sets `total_tickets = len(seats)` itself; do not send it.

- **OPEN_FIELD** → send `tiers: [{ name, price, total_tickets }]`, `seats: []`.
  - No grid, no seats. Just a list of named tiers with a price and a ticket quantity.
  - Backend sets `total_tickets = sum(tier.total_tickets)` itself; do not send it.

The existing frontend types (`src/features/events/types.ts`) already define `EventType`, `EventSeatInput`, `EventTierInput`, `CreateEventRequest` — **reuse them, do not redefine.** The existing `api/create-event.ts` and `hooks/useCreateEvent.ts` already work (POST `/events`, invalidates `["events"]`). **Do not touch them.**

`apiFetch` is at `src/lib/utils.ts`; `useCreateEvent` returns a standard `useMutation` (errors auto-toast via the global `MutationCache` in `src/app/query-client.ts`).

---

## 1. Files to create / modify

### Modify
- `src/routes/events.tsx` — no change needed (EventsPage is rendered here). The "New" button lives inside `EventsPage` itself.
- `src/features/events/components/events/EventsPage.tsx` — add a **"New"** button (top-right) that navigates to `/events/create`.
- `src/features/events/components/events/CreateEvent.tsx` — **replace** the current placeholder stub with the real page component (orchestrator).
- `src/features/events/components/index.ts` — export the new sub-components as needed.

### Create
- `src/routes/events.create.tsx` — TanStack route file → path `/events/create`.
- `src/features/events/stores/useCreateEventStore.ts` — Zustand store holding the entire form session.
- `src/features/events/components/create-event/` — new subfolder for the create UI:
  - `CreateEventForm.tsx` — common fields (name, description, venue, date/time, type switch) + type-specific section + submit button. (This is what `CreateEvent.tsx` renders, or fold `CreateEvent.tsx` directly into this — see §6.)
  - `EventTypeSwitch.tsx` — seated / open-field toggle.
  - `seated/SeatedEditor.tsx` — the dimensions inputs, "Confirm" grid generation, and the seat grid.
  - `seated/SeatGrid.tsx` — the x×y grid of clickable colored cells.
  - `seated/TierPalette.tsx` — the list of colored tier boxes with price inputs + "add tier" + selection.
  - `seated/DimensionsInput.tsx` — rows × cols inputs + Confirm button (optional; can inline in `SeatedEditor`).
  - `open-field/OpenFieldEditor.tsx` — list of tiers (name, price, total_tickets) + add/remove.
  - `open-field/TierRow.tsx` — one open-field tier row (optional; can inline).

Keep the `components/events/` vs `components/event/` convention. The create UI is a sub-flow of the plural "events" listing, so it lives under `components/events/` (replacing the stub) with sub-components in `components/create-event/`. **Update `index.ts` barrel exports accordingly; routes import only from the barrel, never deep paths** (per CLAUDE.md).

---

## 2. Zustand store — `src/features/events/stores/useCreateEventStore.ts`

Per CLAUDE.md: one store per concern, **narrow selectors**, per-input subscriptions (never select the whole store). The store holds the full form session. Use `zustand` (already installed).

```ts
import { create } from "zustand";
import { EventType } from "../types";

// ---- Seated-only types (local to the create flow; NOT sent to backend as-is) ----
export type SeatedTier = {
  id: string;          // local uuid-ish (use crypto.randomUUID())
  name: string;        // label shown in palette, e.g. "VIP"
  color: string;       // tailwind bg class or hex, e.g. "#ef4444"
  price: number;       // cents? no — plain number, matches backend float
};

export type OpenFieldTier = {
  id: string;
  name: string;
  price: number;
  totalTickets: number;
};

type CreateEventState = {
  // common
  name: string;
  description: string;
  venue: string;
  eventDate: string;      // value of <input type="datetime-local">, e.g. "2026-12-15T19:00"
  eventType: EventType;   // default EventType.SEATED

  // seated
  rows: number;
  cols: number;
  gridConfirmed: boolean;               // has the user clicked "Confirm" to lock dims?
  seatedTiers: SeatedTier[];
  selectedTierId: string | null;
  // seat -> tier assignment. Index as seatAssignments[row][col] = tierId | null.
  seatAssignments: (string | null)[][];

  // open field
  openFieldTiers: OpenFieldTier[];

  // actions (granular setters — one per field so selectors stay narrow)
  setName, setDescription, setVenue, setEventDate, setEventType,
  setRows, setCols, confirmGrid, resetGrid,
  addSeatedTier, updateSeatedTier, removeSeatedTier, selectTier,
  assignSeat,           // (row, col) -> toggles selected tier on that cell
  clearSeat,            // (row, col) -> null
  addOpenFieldTier, updateOpenFieldTier, removeOpenFieldTier,
  reset,                // clear everything (call on unmount + after successful submit)
};
```

### Behavior rules
- `setEventType(type)`: when switching, **do not** destroy the other type's data (let the user switch back), but only the matching editor renders. Reset `gridConfirmed`/grid when rows/cols change before confirm.
- `confirmGrid()`: validates `rows >= 1 && cols >= 1`, sets `gridConfirmed = true`, and (re)initializes `seatAssignments` to a `rows × cols` matrix of `null`. Regenerating wipes assignments — that's expected.
- `assignSeat(row, col)`: if no `selectedTierId`, do nothing (or toast "select a tier first"). If the cell already equals `selectedTierId`, set it to `null` (toggle off). Otherwise set to `selectedTierId`.
- Tier colors: maintain a palette array (e.g. 8 distinct hexes) and assign the next unused color when adding a tier; cycle if exhausted.
- IDs: `crypto.randomUUID()`.

### Suggested palette
```ts
const TIER_COLORS = ["#ef4444", "#3b82f6", "#22c55e", "#f59e0b", "#a855f7", "#ec4899", "#14b8a6", "#6366f1"];
```

### Selector usage in components (example)
```ts
const name = useCreateEventStore(s => s.name);
const setName = useCreateEventStore(s => s.setName);
const seatAssignments = useCreateEventStore(s => s.seatAssignments); // 2D array; ok to select, it's the grid itself
```
For per-cell rendering, read `seatAssignments[row][col]` inside the cell component and subscribe to that cell via a tiny selector `s => s.seatAssignments[row][col]` to avoid re-rendering the whole grid on every click. (If perf is fine for typical grids ≤ ~50×50, a single grid subscription is acceptable — agent's call, but prefer per-cell for large grids.)

---

## 3. Route — `src/routes/events.create.tsx`

Mirror the existing `events.tsx` route. File name `events.create.tsx` → URL `/events/create`.

```tsx
import { createFileRoute } from "@tanstack/react-router";
import { CreateEvent } from "@/features/events/components";

export const Route = createFileRoute("/events/create")({
  component: CreateEvent,
});
```

The `routeTree.gen.ts` regenerates automatically on dev/build — **do not hand-edit it.**

---

## 4. "New" button on EventsPage — `EventsPage.tsx`

Add a header row with a "New" button that navigates to `/events/create`.

```tsx
import { useNavigate } from "@tanstack/react-router";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";

const navigate = useNavigate();
// in JSX header:
<Button onClick={() => navigate({ to: "/events/create" })}>
  <Plus /> New
</Button>
```

Keep the existing `useGetEvents` listing below it.

---

## 5. The page component — `CreateEvent.tsx`

Replace the stub. This is the orchestrator. Layout (top to bottom):

1. Page title "Create Event".
2. Common fields card: Name, Description, Venue, Date/Time, **EventTypeSwitch**.
3. Type-specific editor:
   - `eventType === SEATED` → `<SeatedEditor />`
   - `eventType === OPEN_FIELD` → `<OpenFieldEditor />`
4. Footer: **"Create"** button (disabled while mutation is pending) + a "Cancel" that navigates back to `/events`.

On "Create" click → `buildPayload()` (§7) → `useCreateEvent().mutate(payload)`. On success → `toast.success("Event created")`, `reset()` the store, `navigate({ to: "/events" })`. Errors are auto-toasted by the global `MutationCache` — no extra handling needed, but you can also read `isError`/`error` from the mutation if you want inline feedback.

Use the `useCreateEventStore` for all field state; **no local `useState` for form fields** (per the user's explicit Zustand request). Local `useState` is fine only for purely presentational things (e.g. nothing critical here).

### Date/time input
No date library is installed. Use a **native `<input type="datetime-local">`** styled with the existing `Input` ShadCN component. Its `.value` is already in `YYYY-MM-DDTHH:mm` format, which is exactly what the backend `datetime` parser accepts (e.g. `"2026-12-15T19:00"`). No conversion needed. Bind it directly to `eventDate` in the store. (Alternative: add shadcn `calendar` + `popover` + `react-day-picker` — **not recommended** here; native input is zero-dependency and sufficient. If the user later wants a rich picker, swap then.)

---

## 6. Sub-components

### `EventTypeSwitch.tsx`
Two buttons / a segmented toggle: "Seated" / "Open Field". Writes `setEventType`. Subscribes only to `eventType`.

### `SeatedEditor.tsx` (the heart of the feature)
Two-phase UI gated by `gridConfirmed`:

**Phase A — dimensions (before confirm):**
- `rows` input (number, min 1) + `cols` input (number, min 1), bound to store.
- **"Confirm"** button → calls `confirmGrid()`. After this, Phase B renders.

**Phase B — grid + palette (after confirm):**
- Left/main: `<SeatGrid />`.
- Side: `<TierPalette />`.
- A small hint: "Select a tier, then click seats to price them. Click a priced seat again to clear."
- A "Reset grid" link → `resetGrid()` (back to Phase A).

Render both the palette and the grid; the palette must exist before the user can price seats. Allow adding tiers at any time.

### `SeatGrid.tsx`
- Renders a `rows × cols` grid using CSS grid (`gridTemplateColumns: repeat(cols, minmax(0, 1fr))`).
- Each cell is a square (`aspect-square`) button. Color logic:
  - If `seatAssignments[r][c]` is `null` → gray (`bg-muted`).
  - Else → the assigned tier's `color` (inline `style={{ backgroundColor: color }}`).
- `onClick` → `assignSeat(r, c)`.
- Optional: show the seat label (`A1`, `B2`, …) faintly inside the cell, and the price on hover (title attribute).
- **Seat numbering convention:** row label = letter(s) starting at `A` (row 0 = `A`, row 25 = `Z`, row 26 = `AA`, …), column = 1-based number. So seat `r,c` → `${rowLabel(r)}${c+1}`. This label is what becomes `seat_number` in the payload. Keep a helper `seatNumber(r, c)` and **use the same helper in §7** so they can't drift.

### `TierPalette.tsx` (seated)
- Lists `seatedTiers`. Each entry: a colored swatch (the tier's `color`), a name input, a price input (number), a remove button.
- The currently selected tier is highlighted (ring/border). Clicking a tier row calls `selectTier(tier.id)`.
- An **"Add tier"** button → `addSeatedTier()` (auto-assigns next palette color, default name `"Tier N"`, price `0`).
- Subscribe narrowly: list length via `s => s.seatedTiers.length`, selected id via `s => s.selectedTierId`. For each tier row's fields, select that specific tier object by id. (Per CLAUDE.md per-input subscription guidance.)

### `OpenFieldEditor.tsx`
- Lists `openFieldTiers`. Each row: name input, price input (number), total tickets input (number), remove button.
- **"Add tier"** button → `addOpenFieldTier()` (default name `"Tier N"`, price `0`, `totalTickets` `0`).
- A read-only total: "Total tickets: N" = sum of `totalTickets` (informational; backend computes it too).
- Same narrow-selector pattern as the palette.

---

## 7. Building the request payload — `buildPayload(): CreateEventRequest`

Lives in `CreateEvent.tsx` (or a small `buildPayload.ts` next to the store). Reads from the store and produces the exact `CreateEventRequest` shape from `types.ts`.

```ts
import { EventType, type CreateEventRequest, type EventSeatInput, type EventTierInput } from "../types";

function rowLabel(r: number): string {
  // 0->A, 25->Z, 26->AA ...
  let s = "";
  r += 1;
  while (r > 0) {
    const mod = (r - 1) % 26;
    s = String.fromCharCode(65 + mod) + s;
    r = Math.floor((r - 1) / 26);
  }
  return s;
}

function seatNumber(r: number, c: number): string {
  return `${rowLabel(r)}${c + 1}`;
}

function buildPayload(state): CreateEventRequest {
  const base = {
    name: state.name.trim(),
    description: state.description.trim(),
    venue: state.venue.trim(),
    event_date: state.eventDate,            // "2026-12-15T19:00" — backend datetime accepts
    event_type: state.eventType,
  };

  if (state.eventType === EventType.SEATED) {
    const tierById = new Map(state.seatedTiers.map(t => [t.id, t]));
    const seats: EventSeatInput[] = [];
    for (let r = 0; r < state.rows; r++) {
      for (let c = 0; c < state.cols; c++) {
        const tierId = state.seatAssignments[r]?.[c] ?? null;
        const tier = tierId ? tierById.get(tierId) : undefined;
        seats.push({
          seat_number: seatNumber(r, c),
          price: tier?.price ?? 0,   // validation in §8 guarantees tier exists & price>0
        });
      }
    }
    return { ...base, seats, tiers: [] };
  }

  // OPEN_FIELD
  const tiers: EventTierInput[] = state.openFieldTiers.map(t => ({
    name: t.name.trim(),
    price: t.price,
    total_tickets: t.totalTickets,
  }));
  return { ...base, seats: [], tiers };
}
```

**Use `seatNumber`/`rowLabel` consistently between `SeatGrid` (display) and `buildPayload` (payload).** Put them in a shared `seated-utils.ts` if you prefer.

---

## 8. Validation (before calling `mutate`)

Do this in `CreateEvent.tsx` before `buildPayload`/`mutate`. On failure, `toast.error(msg)` and abort. Rules:

**Common:**
- `name`, `description`, `venue` non-empty (after trim).
- `eventDate` non-empty and parses as a valid future-ish datetime (at minimum non-empty; optional: warn if in the past).

**SEATED:**
- `gridConfirmed === true`.
- `seatedTiers.length >= 1`.
- Every seated tier has `price > 0` (and a non-empty name).
- **Every cell is assigned** — no `null` in `seatAssignments`. (Backend requires `price` per seat; unassigned seats have no price.) Count unassigned and report `"N seats have no tier assigned"`.

**OPEN_FIELD:**
- `openFieldTiers.length >= 1`.
- Every tier has non-empty `name`, `price > 0`, `totalTickets > 0` (integer).

Show the first failing message (or a concise list). The backend will also validate (seated⇒seats, open_field⇒tiers) but the frontend checks give better UX.

---

## 9. Submission + cleanup

```tsx
const { mutateAsync, isPending } = useCreateEvent();

async function handleCreate() {
  const state = useCreateEventStore.getState();   // read whole state once for validation+build
  const error = validate(state);
  if (error) { toast.error(error); return; }

  const payload = buildPayload(state);
  try {
    await mutateAsync(payload);
    toast.success("Event created");
    useCreateEventStore.getState().reset();
    navigate({ to: "/events" });
  } catch {
    // already toasted by global MutationCache
  }
}
```

- Disable the "Create" button while `isPending`.
- Call `reset()` on success (and ideally on unmount via `useEffect` cleanup) so re-entering the page starts fresh.

---

## 10. ShadCN components to add (if missing)

Already available: `button`, `input`, `separator`, `sonner` (toaster). Likely needed and probably **not** present yet: `card`, `label`, `select` (for nothing critical here — the type switch can be buttons), `textarea` (for description). Run via shadcn CLI as needed:

```bash
npx shadcn@latest add card label textarea
```

They land in `src/components/ui/`. Keep them untouched/generated. Use `Textarea` for `description`, `Label` for field labels, `Card`/`CardHeader`/`CardContent` to group the common fields and the editor sections. If you'd rather not add deps, plain `<textarea>`/`<label>` with tailwind classes is acceptable — but prefer the shadcn primitives for consistency with the rest of the app.

Check `src/components/ui/` first to avoid re-adding what's there.

---

## 11. Styling notes

- Use Tailwind 4 utilities + `cn()`. Match the existing `EventsPage` / sidebar aesthetic.
- Seat cells: `aspect-square rounded-sm border border-border` default gray `bg-muted`; priced cells use inline `backgroundColor` (because colors are dynamic hex, not tailwind classes).
- Tier swatch: a small `h-5 w-5 rounded` div with inline `backgroundColor`.
- Layout: common fields in a `Card` at top; editor in a `Card` below; grid + palette side-by-side (`grid grid-cols-[1fr_280px] gap-4`) on desktop, stacked on mobile.

---

## 12. Implementation order (suggested)

1. Add shadcn primitives (`card`, `label`, `textarea`) if missing.
2. Create the Zustand store with all fields + actions + `reset`.
3. Create the route file `events.create.tsx`.
4. Add the "New" button to `EventsPage.tsx`.
5. Build `EventTypeSwitch`, then `OpenFieldEditor` (simpler — good warmup).
6. Build `SeatedEditor` + `SeatGrid` + `TierPalette` + the `seatNumber` util.
7. Replace `CreateEvent.tsx` stub: wire common fields, conditional editor, validation, `buildPayload`, submit, reset.
8. Update `components/index.ts` barrel.
9. Manual test both flows end-to-end against the running backend (start `db` + `uvicorn`, ensure `frontend/.env` `VITE_API_BASE_URL=http://localhost:8000`).

---

## 13. Definition of done

- [ ] "New" button on `/events` navigates to `/events/create`.
- [ ] Seated flow: enter rows×cols → Confirm → gray grid appears → add tiers with prices → select a tier → click cells to color them → cells show tier color → click a colored cell again to clear.
- [ ] Open-field flow: add tiers with name/price/total_tickets.
- [ ] Common fields (name, description, venue, datetime) captured.
- [ ] Validation blocks incomplete submissions with a clear toast.
- [ ] Successful submit calls `POST /events` with the correct shape (seated⇒seats, open-field⇒tiers), invalidates the events list, toasts success, resets the store, returns to `/events`.
- [ ] No new `useState` for form fields; everything form-related lives in the Zustand store with narrow selectors.
- [ ] `routeTree.gen.ts` is regenerated by the toolchain, not hand-edited.
- [ ] `npm run lint` and `npm run build` pass.

---

## 14. Gotchas

- **Seated tiers ≠ backend tiers.** Seated `seatedTiers` are local-only; they are flattened to per-seat `price`. Only open-field `openFieldTiers` become backend `tiers`. Mixing this up is the #1 bug risk.
- **`seat_number` must be ≤ 10 chars** (DB `VARCHAR(10)`). `rowLabel`+col is safe for normal grids; don't invent a longer scheme.
- **Don't send `total_tickets` / `available_tickets`** — backend computes them.
- **`apiFetch` POST path is `/events` (no trailing slash)** — already correct in `create-event.ts`; leave it.
- **`event_date` format**: pass the raw `datetime-local` value (`YYYY-MM-DDTHH:mm`). No timezone suffix needed; backend `datetime` parses it.
- **Per CLAUDE.md**: routes import from the feature barrel (`@/features/events/components`), never from deep paths. Keep `index.ts` updated.
- **Don't hand-edit `routeTree.gen.ts`.**
