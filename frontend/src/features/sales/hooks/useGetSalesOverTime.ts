import { useAuth0 } from "@auth0/auth0-react";
import { useQuery } from "@tanstack/react-query";
import { getSalesOverTime } from "../api/get-sales-over-time";
import type { SalesGranularity } from "../types";

export const useGetSalesOverTime = (start_date: Date, end_date: Date, granularity: SalesGranularity) => {
    const auth = useAuth0();

  return useQuery({
    queryKey: ["sales_over_time", start_date, end_date, granularity],
    queryFn: () => getSalesOverTime(auth, start_date, end_date, granularity),
    staleTime: 5 * 60 * 1000, // 5 min
  });
};
