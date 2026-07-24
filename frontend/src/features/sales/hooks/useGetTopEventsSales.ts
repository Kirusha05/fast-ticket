import { useAuth0 } from "@auth0/auth0-react";
import { useQuery } from "@tanstack/react-query";
import { getTopEventsSales } from "../api/get-top-events-sales";

export const useGetTopEventsSales = (start_date: Date, end_date: Date, top_k: number) => {
  const auth = useAuth0();

  return useQuery({
    queryKey: ["sales", "top_events", start_date, end_date, top_k],
    queryFn: () => getTopEventsSales(auth, start_date, end_date, top_k),
    staleTime: 5 * 60 * 1000, // 5 min
  });
};
