import { CalendarIcon, CircleDollarSignIcon, TicketIcon } from "lucide-react";
import type { LucideIcon } from "lucide-react";

export interface NavItem {
  to: string;
  label: string;
  icon: LucideIcon;
  // the item shoould only be shown to authenticated users
  authRequired: boolean;
  // the item shoould only be shown to admin users
  adminRequired?: boolean;
}

export const NAV_ITEMS: readonly NavItem[] = [
  { to: "/events", label: "Events", icon: CalendarIcon, authRequired: false },
  { to: "/bookings", label: "Bookings", icon: TicketIcon, authRequired: true },
  { to: "/sales", label: "Sales", icon: CircleDollarSignIcon, authRequired: true, adminRequired: true },
] as const;
