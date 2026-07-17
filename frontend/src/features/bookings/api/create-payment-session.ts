import { apiFetch } from "@/lib/utils";
import type { Auth0ContextInterface, User } from "@auth0/auth0-react";
import type { PaymentSessionResponse } from "../types";

export const createPaymentSession = async (
  auth: Auth0ContextInterface<User>,
  bookingId: string,
) => {
  const authToken = await auth.getAccessTokenSilently();
  return apiFetch<PaymentSessionResponse>(`/bookings/${bookingId}/payment`, {
    authToken,
    method: "POST"
  });
};