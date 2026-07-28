import { createFileRoute, redirect } from "@tanstack/react-router";
import { TicketsPage } from "@/features/tickets/components";

export const Route = createFileRoute("/tickets_/$bookingId")({
  component: TicketsPage,
  beforeLoad: ({ context }) => {
    if (!context.auth.isAuthenticated) {
      throw redirect({
        to: '/events'
      })
    }
  },
});
