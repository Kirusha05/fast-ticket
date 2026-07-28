import { Route } from "@/routes/tickets_.$bookingId";
import { useGetTickets } from "../../hooks/useGetTickets";
import { useGetBooking } from "@/features/bookings/hooks/useGetBooking";
import { Skeleton } from "@/components/ui";
import { TicketCard } from "./TicketCard";
import { Layers } from "lucide-react";

export const TicketsPage = () => {
  const { bookingId } = Route.useParams();
  const {
    data: tickets,
    isPending: isPendingTickets,
    error: errorTickets,
  } = useGetTickets(bookingId);
  const {
    data: booking,
    isPending: isPendingBooking,
    error: errorBooking,
  } = useGetBooking(bookingId);

  if (isPendingBooking || isPendingTickets) {
    return <p>Loading...</p>;
  }

  console.log("Booking:", booking);
  console.log("Tickets:", tickets);

  return (
    <div className="space-y-6 container mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Your Tickets</h1>
      </div>

      {/* Loading skeletons */}
      {(isPendingBooking || isPendingTickets) && (
        <div className="space-y-4">
          <Skeleton className="aspect-[4/3] h-60 shrink-0 rounded-lg" />
          <Skeleton className="aspect-[4/3] h-60 shrink-0 rounded-lg" />
        </div>
      )}

      {!errorBooking ||
        (errorTickets && (
          <p>
            An error has occured:{" "}
            {errorBooking?.message || errorTickets?.message}
          </p>
        ))}

      {booking && tickets && !tickets.length && (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <div className="mb-4 rounded-full bg-muted p-3">
            <Layers className="h-8 w-8 text-muted-foreground" />
          </div>

          <p className="font-medium">No tickets found</p>

          <p className="mt-1 text-sm text-muted-foreground">
            This booking was not confirmed, so you don't have any tickets.
          </p>
        </div>
      )}

      {booking && tickets && tickets.length > 0 && (
        <div className="space-y-4">
          {tickets.map((ticket) => (
            <TicketCard key={ticket.id} event={booking.event} ticket={ticket} />
          ))}
        </div>
      )}
    </div>
  );
};
