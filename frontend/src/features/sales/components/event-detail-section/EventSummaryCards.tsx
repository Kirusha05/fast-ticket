import { cn } from "@/lib/utils";
import { useGetEventSalesSummary } from "@/features/sales/hooks/useGetEventSalesSummary";
import { type Event } from "@/features/events/types";
import { Card, CardContent, Skeleton } from "@/components/ui";
import {
  CalendarCheck,
  DollarSign,
  Layers,
  Percent,
  Ticket,
} from "lucide-react";

interface IProps {
  selectedEvent: Event;
  dateRange: { start: Date; end: Date };
}

export const EventSummaryCards = ({ selectedEvent, dateRange }: IProps) => {
  const { data, isLoading } = useGetEventSalesSummary(
    selectedEvent.id,
    dateRange.start,
    dateRange.end,
  );

  // Empty State: No event selected
  if (!selectedEvent) {
    return (
      <Card className="rounded-2xl shadow-sm border-dashed">
        <CardContent className="flex flex-col items-center justify-center py-16 text-center">
          <div className="p-4 bg-muted rounded-full mb-4">
            <Layers className="h-10 w-10 text-muted-foreground" />
          </div>
          <p className="font-medium text-lg">No Event Selected</p>
          <p className="text-sm text-muted-foreground mt-1 max-w-sm">
            Use the search box above to select an event and view its detailed
            sales breakdown.
          </p>
        </CardContent>
      </Card>
    );
  }

  const stats = [
    {
      title: "Confirmed Revenue",
      value: data?.confirmed_revenue,
      icon: DollarSign,
      accent: "text-emerald-600",
      iconBg: "bg-emerald-500/10",
      cardBg: "bg-emerald-500/5",
      border: "border-emerald-500/40",
      format: (val: number) => `$${val.toLocaleString()}`,
    },
    {
      title: "Tickets Sold",
      value: data?.sold_tickets,
      icon: Ticket,
      accent: "text-blue-600",
      iconBg: "bg-blue-500/10",
      cardBg: "bg-blue-500/5",
      border: "border-blue-500/40",
      format: (val: number) => val.toLocaleString(),
    },
    {
      title: "Confirmed Bookings",
      value: data?.confirmed_bookings_count,
      icon: CalendarCheck,
      accent: "text-purple-600",
      iconBg: "bg-purple-500/10",
      cardBg: "bg-purple-500/5",
      border: "border-purple-500/40",
      format: (val: number) => val.toLocaleString(),
    },
    {
      title: "Sell-Through Rate",
      value: data?.sell_through_rate,
      icon: Percent,
      accent: "text-amber-600",
      iconBg: "bg-amber-500/10",
      cardBg: "bg-amber-500/5",
      border: "border-amber-500/40",
      format: (val: number) => `${Math.round(val * 100 * 100) / 100}%`,
    },
  ];

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {stats.map((stat) => (
        <Card
          key={stat.title}
          className={cn(
            "border ring-0 transition-all duration-200 hover:-translate-y-0.5",
            stat.cardBg,
            stat.border,
          )}
        >
          <CardContent className="p-5">
            <div className="flex items-center justify-between">
              {isLoading ? (
                <Skeleton className="h-11 w-32" />
              ) : (
                <>
                  <p className="text-4xl font-semibold tabular-nums tracking-tight text-foreground">
                    {stat.format(stat.value || 0)}
                  </p>
                  <div className={cn("rounded-lg p-1.5", stat.iconBg)}>
                    <stat.icon className={cn("h-6 w-6", stat.accent)} />
                  </div>
                </>
              )}
            </div>
            <p className="mt-3 text-xs font-bold capitalize tracking-wide text-muted-foreground">
              {stat.title}
            </p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
};
