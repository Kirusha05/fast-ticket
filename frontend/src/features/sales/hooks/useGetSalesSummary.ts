import { useAuth0 } from "@auth0/auth0-react";
import { useQuery } from "@tanstack/react-query";
import { getSalesSummary } from "../api/get-sales-summary";

export const useGetSalesSummary = (start_date: Date, end_date: Date) => {
  const auth = useAuth0();

  return useQuery({
    queryKey: ["sales", start_date, end_date],
    queryFn: () => getSalesSummary(auth, start_date, end_date),
    staleTime: 5 * 60 * 1000, // 5 min
  });
};
