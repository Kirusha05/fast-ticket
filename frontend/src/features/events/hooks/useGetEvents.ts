import { useQuery } from "@tanstack/react-query";
import { getEvents } from "../api/get-events";
import type { SearchEventType } from "../types";

export const useGetEvents = (eventType: SearchEventType) => {
  return useQuery({
    queryKey: ["events"],
    queryFn: () => getEvents(eventType),
    meta: {
      errorMessage: "Failed to load users",
    },
  });
};
