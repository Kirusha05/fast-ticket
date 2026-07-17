import { useMutation } from "@tanstack/react-query";
import { useAuth0 } from "@auth0/auth0-react";
import { createPaymentSession } from "../api/create-payment-session";
import { queryClient } from "@/app/query-client";

export const useCreatePaymentSession = (bookingId: string) => {
  const auth = useAuth0();

  return useMutation({
    mutationFn: () => createPaymentSession(auth, bookingId),
    onSuccess: (data) => {
        queryClient.invalidateQueries({ queryKey: ["bookings"] });
        window.location.href = data.checkout_url;
    },
  });
};