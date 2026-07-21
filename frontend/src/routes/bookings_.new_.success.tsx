import { createFileRoute } from "@tanstack/react-router";
import { SuccessPage, successfulBookingSchema } from "@/features/bookings/components";

export const Route = createFileRoute("/bookings_/new_/success")({
  validateSearch: successfulBookingSchema,
  component: SuccessPage,
});
