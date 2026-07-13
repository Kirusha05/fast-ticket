import { createFileRoute, redirect } from "@tanstack/react-router";
import { CreateEvent } from "@/features/events/components";

export const Route = createFileRoute("/events_/create")({
  component: CreateEvent,
  beforeLoad: ({ context }) => {
    if (!context.auth.isAuthenticated || !context.auth.isAdmin) {
      throw redirect({
        to: '/events'
      })
    }
  },
});
