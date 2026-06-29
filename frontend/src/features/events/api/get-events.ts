import { apiFetch } from "@/lib/utils";
import type { Event, SearchEventType } from "../types";

export const getEvents = (eventType: SearchEventType) => {
  const searchParams = eventType ? `?event_type=${eventType}` : ""
  return apiFetch<Event[]>(`/events${searchParams}`);
};
