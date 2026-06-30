import { createFileRoute } from "@tanstack/react-router";
import { CreateEvent } from "@/features/events/components";

export const Route = createFileRoute("/events_/create")({
  component: CreateEvent,
});