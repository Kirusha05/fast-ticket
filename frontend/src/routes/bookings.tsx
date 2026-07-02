import { createFileRoute } from "@tanstack/react-router";
import { BookingsPage } from "@/features/bookings/components";

export const Route = createFileRoute("/bookings")({
  component: BookingsPage,
});
