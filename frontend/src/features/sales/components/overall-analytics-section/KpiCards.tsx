import { Card, CardContent, Skeleton } from "@/components/ui";
import { useGetSalesSummary } from "@/features/sales/hooks/useGetSalesSummary";
import { DollarSign, Ticket, CalendarCheck, TrendingDown } from "lucide-react";
import { cn } from "@/lib/utils";

interface IProps {
  dateRange: { start: Date; end: Date };
}

export const OverallKpiCards = ({ dateRange }: IProps) => {
  const { data, isLoading } = useGetSalesSummary(
    dateRange.start,
    dateRange.end,
  );

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
      title: "Lost Revenue (expired/cancelled)",
      value: data?.lost_revenue,
      icon: TrendingDown,
      accent: "text-rose-600",
      iconBg: "bg-rose-500/10",
      cardBg: "bg-rose-500/5",
      border: "border-rose-500/40",
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
