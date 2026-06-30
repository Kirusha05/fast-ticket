import { useNavigate } from "@tanstack/react-router";
import { z } from "zod";
import { Route } from "@/routes/events";
import { useGetEvents } from "@/features/events/hooks/useGetEvents";
import { Button } from "@/components/ui";
import { Plus } from "lucide-react";

export const eventsSearchSchema = z.object({
  event_type: z.enum(["open_field", "seated"]).optional().catch(undefined),
});

export function EventsPage() {
  const navigate = useNavigate();
  const { event_type } = Route.useSearch();
  const { data: events, isPending, isError, error } = useGetEvents(event_type);

  if (isPending) {
    return <div>Loading events...</div>;
  }

  if (isError) {
    return <div>An error has occured: {error.message}</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Events</h1>
        <Button className="cursor-pointer" onClick={() => navigate({ to: "/events/create" })}>
          <Plus className="mr-1 h-4 w-4" />
          New
        </Button>
      </div>
      {!events.length && <p>No events...</p>}
      {events && events.map(event => <div key={event.id}>{event.name}</div>)}
    </div>
  );
}
