import { create } from "zustand";
import { EventType } from "../types";

// ---- Seated-only types (local to the create flow; NOT sent to backend as-is) ----
export type SeatedTier = {
  id: string;
  name: string;
  color: string;
  price: number;
};

export type OpenFieldTier = {
  id: string;
  name: string;
  price: number;
  totalTickets: number;
};

const TIER_COLORS = [
  "#ef4444", "#3b82f6", "#22c55e", "#f59e0b",
  "#a855f7", "#ec4899", "#14b8a6", "#6366f1",
];

let colorIndex = 0;
function nextColor(): string {
  const c = TIER_COLORS[colorIndex % TIER_COLORS.length];
  colorIndex++;
  return c;
}

type CreateEventState = {
  // common
  name: string;
  description: string;
  venue: string;
  eventDate: string;
  eventType: EventType;

  // seated
  rows: number;
  cols: number;
  gridConfirmed: boolean;
  seatedTiers: SeatedTier[];
  selectedTierId: string | null;
  seatAssignments: (string | null)[][];

  // open field
  openFieldTiers: OpenFieldTier[];

  // actions
  setName: (v: string) => void;
  setDescription: (v: string) => void;
  setVenue: (v: string) => void;
  setEventDate: (v: string) => void;
  setEventType: (v: EventType) => void;

  setRows: (v: number) => void;
  setCols: (v: number) => void;
  confirmGrid: () => void;
  resetGrid: () => void;

  addSeatedTier: () => void;
  updateSeatedTier: (id: string, patch: Partial<Pick<SeatedTier, "name" | "price">>) => void;
  removeSeatedTier: (id: string) => void;
  selectTier: (id: string | null) => void;
  assignSeat: (row: number, col: number) => void;
  clearSeat: (row: number, col: number) => void;

  addOpenFieldTier: () => void;
  updateOpenFieldTier: (id: string, patch: Partial<Pick<OpenFieldTier, "name" | "price" | "totalTickets">>) => void;
  removeOpenFieldTier: (id: string) => void;

  reset: () => void;
};

function createInitialSeatAssignments(rows: number, cols: number): null[][] {
  return Array.from({ length: rows }, () => Array(cols).fill(null));
}

const initialState = {
  name: "",
  description: "",
  venue: "",
  eventDate: "",
  eventType: EventType.SEATED,
  rows: 10,
  cols: 15,
  gridConfirmed: false,
  seatedTiers: [] as SeatedTier[],
  selectedTierId: null as string | null,
  seatAssignments: [] as (string | null)[][],
  openFieldTiers: [] as OpenFieldTier[],
};

export const useCreateEventStore = create<CreateEventState>((set, get) => ({
  ...initialState,

  setName: (name) => set({ name }),
  setDescription: (description) => set({ description }),
  setVenue: (venue) => set({ venue }),
  setEventDate: (eventDate) => set({ eventDate }),
  setEventType: (eventType) => set({ eventType }),

  setRows: (rows) => set({ rows }),
  setCols: (cols) => set({ cols }),
  confirmGrid: () => {
    const { rows, cols } = get();
    if (rows < 1 || cols < 1) return;
    set({ gridConfirmed: true, seatAssignments: createInitialSeatAssignments(rows, cols) });
  },
  resetGrid: () => {
    set({ gridConfirmed: false, seatAssignments: [], selectedTierId: null });
  },

  addSeatedTier: () => {
    const { seatedTiers } = get();
    const tier: SeatedTier = {
      id: crypto.randomUUID(),
      name: `Tier ${seatedTiers.length + 1}`,
      color: nextColor(),
      price: 0,
    };
    set({ seatedTiers: [...seatedTiers, tier] });
  },
  updateSeatedTier: (id, patch) => {
    set((s) => ({
      seatedTiers: s.seatedTiers.map((t) => (t.id === id ? { ...t, ...patch } : t)),
    }));
  },
  removeSeatedTier: (id) => {
    set((s) => ({
      seatedTiers: s.seatedTiers.filter((t) => t.id !== id),
      selectedTierId: s.selectedTierId === id ? null : s.selectedTierId,
      seatAssignments: s.seatAssignments.map((row) =>
        row.map((cell) => (cell === id ? null : cell)),
      ),
    }));
  },
  selectTier: (id) => set({ selectedTierId: id }),
  assignSeat: (row, col) => {
    const { selectedTierId, seatAssignments } = get();
    if (!selectedTierId) return;
    const current = seatAssignments[row]?.[col];
    if (current === selectedTierId) {
      // toggle off
      const updated = seatAssignments.map((r, ri) =>
        ri === row ? r.map((c, ci) => (ci === col ? null : c)) : r,
      );
      set({ seatAssignments: updated });
    } else {
      const updated = seatAssignments.map((r, ri) =>
        ri === row ? r.map((c, ci) => (ci === col ? selectedTierId : c)) : r,
      );
      set({ seatAssignments: updated });
    }
  },
  clearSeat: (row, col) => {
    const { seatAssignments } = get();
    const updated = seatAssignments.map((r, ri) =>
      ri === row ? r.map((c, ci) => (ci === col ? null : c)) : r,
    );
    set({ seatAssignments: updated });
  },

  addOpenFieldTier: () => {
    const { openFieldTiers } = get();
    const tier: OpenFieldTier = {
      id: crypto.randomUUID(),
      name: `Tier ${openFieldTiers.length + 1}`,
      price: 0,
      totalTickets: 0,
    };
    set({ openFieldTiers: [...openFieldTiers, tier] });
  },
  updateOpenFieldTier: (id, patch) => {
    set((s) => ({
      openFieldTiers: s.openFieldTiers.map((t) =>
        t.id === id ? { ...t, ...patch } : t,
      ),
    }));
  },
  removeOpenFieldTier: (id) => {
    set((s) => ({
      openFieldTiers: s.openFieldTiers.filter((t) => t.id !== id),
    }));
  },

  reset: () => {
    colorIndex = 0;
    set({ ...initialState });
  },
}));