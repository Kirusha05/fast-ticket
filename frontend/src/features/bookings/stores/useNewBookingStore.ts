import { create } from "zustand";

type NewBookingState = {
  selectedSeatIds: string[];
  // map of tier_id -> ticket count
  tierCounts: Record<string, number>;

  // toggle a seat's selection (add if absent, remove if present)
  toggleSeat: (seatId: string) => void;
  setTierCount: (tierId: string, count: number) => void;
  reset: () => void;
};

export const useNewBookingStore = create<NewBookingState>((set) => ({
  selectedSeatIds: [],
  tierCounts: {},

  toggleSeat: (seatId) =>
    set((s) => {
      const exists = s.selectedSeatIds.includes(seatId);
      return {
        selectedSeatIds: exists
          ? s.selectedSeatIds.filter((id) => id !== seatId)
          : [...s.selectedSeatIds, seatId],
      };
    }),

  setTierCount: (tierId, count) =>
    set((s) => ({
      tierCounts: { ...s.tierCounts, [tierId]: Math.max(0, count) },
    })),

  reset: () => set({ selectedSeatIds: [], tierCounts: {} }),
}));