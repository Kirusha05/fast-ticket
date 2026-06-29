import { Route } from "@/routes/events_.$eventId";
import { useGetEvent } from "@/features/events/hooks/useGetEvent";

export function EventPage() {
    const { eventId } = Route.useParams();
    const { data: event, isPending, isError, error } = useGetEvent(eventId);
  
    if (isPending) {
      return <div>Loading events...</div>;
    }
  
    if (isError) {
      return <div>An error has occured: {error.message}</div>;
    }
  
    return (
      <>
        <h1>Event Page</h1>
        {event.name}
      </>
    );
  }
  