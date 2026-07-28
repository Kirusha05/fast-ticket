import { apiFetch } from "@/lib/utils";
import type { Ticket } from "../types";
import type { Auth0ContextInterface, User } from "@auth0/auth0-react";

export const getTickets = async (
  auth: Auth0ContextInterface<User>,
  bookingId: string,
) => {
  const authToken = await auth.getAccessTokenSilently();

  return apiFetch<Ticket[]>(`/tickets/${bookingId}`, { authToken });
};
