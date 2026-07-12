import { useAuth0 } from "@auth0/auth0-react";
import { useMutation } from "@tanstack/react-query";
import { cancelBooking } from "../api/cancel-booking";
import { queryClient } from "@/app/query-client";
import type { Booking } from "../types";

export const useCancelBooking = () => {
  const auth = useAuth0();

  return useMutation({
    mutationFn: (bookingId: string) => cancelBooking(auth, bookingId),
    onSuccess: (data, bookingId) => {
      queryClient.setQueryData<Booking[]>(["bookings"], (old) =>
        old?.map((b) => (b.id === bookingId ? data : b)),
      );
    },
  });
};