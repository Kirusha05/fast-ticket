import { apiFetch } from "@/lib/utils";
import type { Auth0ContextInterface, User } from "@auth0/auth0-react";
import type { Booking } from "../types";

export const getBooking = async (
  auth: Auth0ContextInterface<User>,
  bookingId: string,
) => {
  const authToken = await auth.getAccessTokenSilently();
  return apiFetch<Booking>(`/bookings/${bookingId}`, { authToken });
};