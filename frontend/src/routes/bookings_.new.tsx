import { createFileRoute, redirect } from "@tanstack/react-router";
import { NewBookingPage, newBookingSchema } from "@/features/bookings/components";

export const Route = createFileRoute("/bookings_/new")({
  validateSearch: newBookingSchema,
  component: NewBookingPage,
  beforeLoad: ({ context }) => {
    if (!context.auth.isAuthenticated) {
      throw redirect({
        to: '/events'
      })
    }
  },
});
