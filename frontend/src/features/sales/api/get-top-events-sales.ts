import type { Auth0ContextInterface, User } from "@auth0/auth0-react";
import { apiFetch } from "@/lib/utils";
import type { EventSalesSummary } from "../types";

export const getTopEventsSales = async (
  auth: Auth0ContextInterface<User>,
  start_date: Date,
  end_date: Date,
  top_k: number
) => {
  const authToken = await auth.getAccessTokenSilently();

  const searchParams = new URLSearchParams({
    start_date: start_date.toISOString(),
    end_date: end_date.toISOString(),
    top_k: top_k.toString()
  });

  return apiFetch<EventSalesSummary[]>(`/sales/events/top?${searchParams.toString()}`, {
    authToken,
  });
};
