import { apiFetch } from "@/lib/utils";
import type { Auth0ContextInterface, User } from "@auth0/auth0-react";
import type { Booking, CreateBookingRequest } from "../types";

export const createBooking = async (
  auth: Auth0ContextInterface<User>,
  body: CreateBookingRequest,
) => {
  const authToken = await auth.getAccessTokenSilently();
  return apiFetch<Booking>("/bookings", {
    authToken,
    method: "POST",
    body: JSON.stringify(body),
  });
};