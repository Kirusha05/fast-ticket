import { useAuth0 } from "@auth0/auth0-react";
import { useMutation } from "@tanstack/react-query";
import type { CreateBookingRequest } from "../types";
import { createBooking } from "../api/create-booking";
import { queryClient } from "@/app/query-client";

export const useCreateBooking = () => {
  const auth = useAuth0();

  return useMutation({
    mutationFn: (body: CreateBookingRequest) => createBooking(auth, body),
    onSuccess: (data, body) => {
      queryClient.invalidateQueries({ queryKey: ["bookings"] });
    },
  });
};