import { useQuery } from "@tanstack/react-query";
import { getEvent } from "../api/get-event";

export const useGetEvent = (eventId: string) => {
  return useQuery({
    queryKey: ["events", eventId],
    queryFn: () => getEvent(eventId),
    staleTime: 0
  });
};
