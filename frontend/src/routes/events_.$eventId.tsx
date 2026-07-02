import { createFileRoute } from "@tanstack/react-router";
import { EventPage } from "@/features/events/components";

export const Route = createFileRoute("/events_/$eventId")({
  component: EventPage,
});
