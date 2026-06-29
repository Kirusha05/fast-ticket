import { apiFetch } from "@/lib/utils";
import type { Event } from "../types";

export const getEvent = (eventId: string) => {
  return apiFetch<Event>(`/events/${eventId}`);
};
