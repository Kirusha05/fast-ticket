import { Link } from "@tanstack/react-router";
import { format } from "date-fns";
import { ExternalLink, Trophy } from "lucide-react";
import { cn } from "@/lib/utils";
import { useGetTopEventsSales } from "@/features/sales/hooks/useGetTopEventsSales";
import { Badge, Button, Progress, Separator, Skeleton } from "@/components/ui";

const getRankBadgeClass = (index: number) => {
  if (index === 0)
    return "bg-yellow-100 text-yellow-700 border-yellow-200 dark:bg-yellow-500/10 dark:text-yellow-400 dark:border-yellow-500/20";
  if (index === 1)
    return "bg-slate-100 text-slate-700 border-slate-200 dark:bg-slate-500/10 dark:text-slate-300 dark:border-slate-500/20";
  if (index === 2)
    return "bg-orange-100 text-orange-700 border-orange-200 dark:bg-orange-500/10 dark:text-orange-400 dark:border-orange-500/20";

  return "bg-muted text-muted-foreground";
};

interface IProps {
  dateRange: { start: Date; end: Date };
  topK: number;
}

export const TopEventsLeaderboard = ({ dateRange, topK }: IProps) => {
  const { data, isPending } = useGetTopEventsSales(
    dateRange.start,
    dateRange.end,
    topK,
  );

  return (
    <div className="mt-10 space-y-2">
      {isPending &&
        Array.from({ length: 5 }).map((_, i) => (
          <div
            key={i}
            className="grid grid-cols-[1fr_180px_120px] items-center rounded-xl border p-4"
          >
            <div className="flex items-center gap-3">
              <Skeleton className="h-8 w-8 rounded-full" />

              <div className="flex-1 space-y-2">
                <Skeleton className="h-4 w-40" />
                <Skeleton className="h-3 w-52" />
              </div>
            </div>

            <Skeleton className="h-2 w-full" />

            <Skeleton className="ml-auto h-5 w-20" />
          </div>
        ))}

      {data && data.length > 0 ? (
        <>
          {/* Table header */}
          <div className="hidden grid-cols-[3fr_1fr_1fr] gap-6 px-4 pb-2 text-xs font-medium uppercase tracking-wide text-muted-foreground sm:grid">
            <div>Event</div>
            <div className="text-center">Sell-through rate</div>
            <div className="text-right">Revenue</div>
          </div>

          {data.map((event, index) => (
            <div
              key={event.event_id}
              className="grid grid-cols-1 gap-4 rounded-xl border border-transparent px-4 py-3 transition-all hover:border-border hover:bg-muted/40 sm:grid-cols-[3fr_1fr_1fr]"
            >
              {/* Event */}
              <div className="flex items-center gap-3 min-w-0">
                <Badge
                  variant="outline"
                  className={cn(
                    "h-8 w-8 shrink-0 justify-center rounded-full font-semibold",
                    getRankBadgeClass(index),
                  )}
                >
                  {index + 1}
                </Badge>

                <div className="min-w-0 flex-1">
                  <p className="truncate font-medium">{event.event_name}</p>

                  <div className="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-muted-foreground">
                    <span>
                      {format(new Date(event.event_date), "MMM dd, yyyy")}
                    </span>
                    <Separator orientation="vertical" />
                    <span>
                      {event.sold_tickets.toLocaleString()} tickets sold
                    </span>
                    <Separator orientation="vertical" />
                    <Button
                      variant="ghost"
                      size="sm"
                      asChild
                      className="h-6 px-2 text-xs"
                    >
                      <Link
                        to="/events/$eventId"
                        params={{ eventId: event.event_id }}
                      >
                        <ExternalLink className="mr-1 h-3 w-3" />
                        View event
                      </Link>
                    </Button>
                  </div>
                </div>
              </div>

              {/* Sell-through */}
              <div className="flex items-center gap-3">
                <Progress
                  value={Math.min(event.sell_through_rate * 100, 100)}
                  className="h-1.5 flex-1"
                />

                <span className="w-10 text-right text-xs font-medium tabular-nums text-muted-foreground">
                  {Math.round(event.sell_through_rate * 100 * 100) / 100}%
                </span>
              </div>

              {/* Revenue */}
              <div className="flex items-center justify-between sm:justify-end">
                <span className="text-xs text-muted-foreground sm:hidden">
                  Revenue
                </span>

                <span className="font-semibold tabular-nums text-emerald-600">
                  ${event.confirmed_revenue.toLocaleString()}
                </span>
              </div>
            </div>
          ))}
        </>
      ) : (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <div className="mb-4 rounded-full bg-muted p-3">
            <Trophy className="h-8 w-8 text-muted-foreground" />
          </div>

          <p className="font-medium">No events found</p>

          <p className="mt-1 text-sm text-muted-foreground">
            Try adjusting your date range.
          </p>
        </div>
      )}
    </div>
  );
};
