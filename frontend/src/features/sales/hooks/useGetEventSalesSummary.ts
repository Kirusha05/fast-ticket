import { useAuth0 } from "@auth0/auth0-react";
import { useQuery } from "@tanstack/react-query";
import { getEventSalesSummary } from "../api/get-event-sales-summary";

export const useGetEventSalesSummary = (event_id: string, start_date: Date, end_date: Date) => {
    const auth = useAuth0();

  return useQuery({
    queryKey: ["sales", event_id, start_date, end_date],
    queryFn: () => getEventSalesSummary(auth, event_id, start_date, end_date),
    staleTime: 5 * 60 * 1000, // 5 min
  });
};
