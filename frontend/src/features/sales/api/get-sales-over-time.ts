import type { Auth0ContextInterface, User } from "@auth0/auth0-react";
import { apiFetch } from "@/lib/utils";
import type { SalesGranularity, TimeSeriesPoint } from "../types";

export const getSalesOverTime = async (
  auth: Auth0ContextInterface<User>,
  start_date: Date,
  end_date: Date,
  granularity: SalesGranularity
) => {
  const authToken = await auth.getAccessTokenSilently();
  
  const searchParams = new URLSearchParams({
    start_date: start_date.toISOString(),
    end_date: end_date.toISOString(),
    granularity
  });

  return apiFetch<TimeSeriesPoint[]>(`/sales/over-time?${searchParams.toString()}`, {
    authToken,
  });
};
