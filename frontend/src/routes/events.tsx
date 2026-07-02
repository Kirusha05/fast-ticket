import { createFileRoute } from "@tanstack/react-router";
import { EventsPage, eventsSearchSchema } from "@/features/events/components";

export const Route = createFileRoute("/events")({
  validateSearch: eventsSearchSchema,
  component: EventsPage,
});
