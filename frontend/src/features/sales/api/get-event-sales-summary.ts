import type { Auth0ContextInterface, User } from "@auth0/auth0-react";
import { apiFetch } from "@/lib/utils";
import type { EventSalesSummary } from "../types";

export const getEventSalesSummary = async (
  auth: Auth0ContextInterface<User>,
  event_id: string,
  start_date: Date,
  end_date: Date
) => {
  const authToken = await auth.getAccessTokenSilently();

  const searchParams = new URLSearchParams({
    start_date: start_date.toISOString(),
    end_date: end_date.toISOString()
  });

  return apiFetch<EventSalesSummary>(`/sales/events/${event_id}?${searchParams.toString()}`, {
    authToken,
  });
};
