import { useNavigate } from "@tanstack/react-router";
import { z } from "zod";
import { Route } from "@/routes/events";
import { useGetEvents } from "@/features/events/hooks/useGetEvents";
import { EventCard } from "./EventCard";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui";
import { Loader2, Plus, Ticket } from "lucide-react";

export const eventsSearchSchema = z.object({
  event_type: z.enum(["open_field", "seated"]).optional().catch(undefined),
});

const FILTERS = [
  { label: "All", value: undefined },
  { label: "Seated", value: "seated" as const },
  { label: "Open Field", value: "open_field" as const },
] as const;

export function EventsPage() {
  const navigate = useNavigate();
  const { event_type } = Route.useSearch();
  const { data: events, isPending, isFetching, isError, error } = useGetEvents(event_type);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Events</h1>
        <Button className="cursor-pointer" onClick={() => navigate({ to: "/events/create" })}>
          <Plus className="mr-1 h-4 w-4" />
          New
        </Button>
      </div>

      {/* Filter tabs */}
      <div className="flex items-center gap-1.5">
        <Ticket className="h-5 w-5 text-muted-foreground mr-2" />
        {FILTERS.map((f) => {
          const isActive = event_type === f.value;
          return (
            <Button
              key={f.label}
              variant={isActive ? "default" : "outline"}
              size="sm"
              onClick={() =>
                navigate({
                  to: "/events",
                  search: f.value ? { event_type: f.value } : {},
                })
              }
            >
              {f.label}
            </Button>
          );
        })}
      </div>

      {/* Loading skeleton cards */}
      {isPending && (
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {Array.from({ length: 7 }).map((_, i) => (
            <div key={i} className="overflow-hidden rounded-xl ring-1 ring-foreground/10">
              <Skeleton className="aspect-[16/9] w-full rounded-none" />
              <div className="space-y-3 p-4">
                <Skeleton className="h-5 w-3/4" />
                <Skeleton className="h-4 w-1/2" />
                <Skeleton className="h-4 w-2/3" />
              </div>
            </div>
          ))}
        </div>
      )}

      {isError && <div>An error has occured: {error.message}</div>}

      {events && !events.length && <p>No events...</p>}
      {events && events.length > 0 && (
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {events.map((event) => (
            <EventCard key={event.id} event={event} />
          ))}
        </div>
      )}

      {/* Background fetching spinner */}
      {!isPending && isFetching && (
        <div className="fixed bottom-4 right-4 z-50">
          <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
        </div>
      )}
    </div>
  );
}
