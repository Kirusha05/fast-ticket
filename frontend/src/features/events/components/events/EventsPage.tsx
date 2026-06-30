import { z } from "zod";
import { Route } from "@/routes/events";
import { useGetEvents } from "@/features/events/hooks/useGetEvents";

export const eventsSearchSchema = z.object({
  event_type: z.enum(["open_field", "seated"]).optional().catch(undefined),
});

export function EventsPage() {
  const { event_type } = Route.useSearch()
  const { data: events, isPending, isError, error } = useGetEvents(event_type);

  if (isPending) {
    return <div>Loading events...</div>;
  }

  if (isError) {
    return <div>An error has occured: {error.message}</div>;
  }

  return (
    <>
      <h1>Events Page</h1>
      {!events.length && <p>No events...</p>}
      {events && events.map(event => <div>{event.name}</div>)}
    </>
  );
}
