import type { Auth0ContextInterface, User } from "@auth0/auth0-react";
import { apiFetch } from "@/lib/utils";
import type { SalesSummary } from "../types";

export const getSalesSummary = async (
  auth: Auth0ContextInterface<User>,
  start_date: Date,
  end_date: Date,
) => {
  const authToken = await auth.getAccessTokenSilently();

  const searchParams = new URLSearchParams({
    start_date: start_date.toISOString(),
    end_date: end_date.toISOString(),
  });

  return apiFetch<SalesSummary>(`/sales/summary?${searchParams.toString()}`, {
    authToken,
  });
};
