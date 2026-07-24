import { createFileRoute, redirect } from "@tanstack/react-router";
import { BookingsPage } from "@/features/bookings/components";

export const Route = createFileRoute("/bookings")({
  component: BookingsPage,
  beforeLoad: ({ context }) => {
    if (!context.auth.isAuthenticated) {
      throw redirect({
        to: '/events'
      })
    }
  },
});
