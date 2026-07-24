import { createFileRoute, redirect } from "@tanstack/react-router";
import { SalesPage } from "@/features/sales/components";

export const Route = createFileRoute("/sales")({
  component: SalesPage,
  beforeLoad: ({ context }) => {
    if (!context.auth.isAuthenticated || !context.auth.isAdmin) {
      throw redirect({
        to: '/events'
      })
    }
  },
});
