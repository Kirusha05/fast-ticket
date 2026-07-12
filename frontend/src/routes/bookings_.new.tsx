import { createFileRoute } from "@tanstack/react-router";
import { NewBookingPage, newBookingSchema } from "@/features/bookings/components";

export const Route = createFileRoute("/bookings_/new")({
  validateSearch: newBookingSchema,
  component: NewBookingPage,
});
