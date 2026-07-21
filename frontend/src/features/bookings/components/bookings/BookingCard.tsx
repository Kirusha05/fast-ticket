import { CalendarDays, MapPin, Ticket, ExternalLink } from "lucide-react";
import { Link } from "@tanstack/react-router";
import type { Booking, BookingStatus } from "@/features/bookings/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { useCancelBooking } from "@/features/bookings/hooks/useCancelBooking";
import { useCreatePaymentSession } from "@/features/bookings/hooks/useCreatePaymentSession";
import { cn } from "@/lib/utils";
import { toast } from "sonner";
import { useIsMobile } from "@/hooks/use-mobile";
import { ticketSummary, usd } from "../new-booking/utils";

const dateFormat = new Intl.DateTimeFormat("en-US", {
  dateStyle: "medium",
  timeStyle: "short",
});

// new Intl.DateTimeFormat("en-US", {
//   month: "short",
//   day: "numeric",
//   year: "numeric",
//   hour: "numeric",
//   minute: "2-digit",
// })

const badgeColorMap: Record<BookingStatus, string> = {
  pending: "bg-yellow-500",
  confirmed: "bg-green-500",
  cancelled: "bg-red-500",
  expired: "bg-slate-500"
}

interface IProps {
  booking: Booking;
}

export function BookingCard({ booking }: IProps) {
  const { mutate: cancelBooking, isPending: isCancelling } = useCancelBooking();
  const { mutate: createPaymentSession, isPending: isCreatingPaymentSession } = useCreatePaymentSession(booking.id);
  const isMobile = useIsMobile();

  const handlePayment = () => {
    createPaymentSession();
  }

  const handleCancelBooking = () => {
    cancelBooking(booking.id, {
      onSuccess: () => {
        toast.success("Booking cancelled");
      },
      onError: (err) => {
        toast.error(err.message ?? "Failed to cancel booking.");
      },
    });
  }

  const isCancelled = booking.status === "cancelled";
  const isConfirmed = booking.status === "confirmed";
  const isPending = booking.status === "pending";
  const isExpired = booking.status === "expired";
  const formattedEventDate = dateFormat.format(new Date(booking.event.event_date));

  return (
    <Card
      className={cn(
        "flex-col md:flex-row gap-0 md:gap-2 overflow-hidden py-0 transition-shadow hover:shadow-md ",
        (isCancelled || isExpired) && "opacity-60",
      )}
    >
      {/* event banner — clickable to event page */}
      <Link
        to="/events/$eventId"
        params={{ eventId: booking.event_id }}
        className="shrink-0"
      >
        <img
          src={booking.event.banner_url}
          alt={booking.event.name}
          className="aspect-[4/3] w-full md:w-auto h-60 shrink-0 cursor-pointer object-cover transition-opacity hover:opacity-80"
        />
      </Link>

      <CardContent className="flex min-w-0 flex-1 flex-col justify-between p-4">
        <div className="space-y-2">
          {/* row 1: event name + status */}
          <div className="flex items-center justify-between gap-2">
            <span className="truncate text-sm font-semibold">
              {booking.event.name}
            </span>
            <div className="flex items-center gap-1.5 shrink-0">
              <Button variant="outline" size="sm" asChild>
                <Link
                  to="/events/$eventId"
                  params={{ eventId: booking.event_id }}
                  >
                  <ExternalLink className="h-3.5 w-3.5" />
                  View event
                </Link>
              </Button>
            </div>
          </div>

          {/* row 2: venue + date */}
          <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-xs text-muted-foreground mt-4 md:mt-0">
            <span className="inline-flex items-center gap-1">
              <MapPin className="h-3.5 w-3.5 shrink-0" />
              {booking.event.venue}
            </span>
            <span className="inline-flex items-center gap-1">
              <CalendarDays className="h-3.5 w-3.5 shrink-0" />
              {formattedEventDate}
            </span>
          </div>

          <Separator className="my-4" />

          {/* row 3: ticket breakdown */}
          {ticketSummary(booking) && (
            <>
              <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                <Ticket className="h-3.5 w-3.5 shrink-0" />
                <span className="truncate">{ticketSummary(booking)}</span>
              </div>
              {isMobile && <Separator className="mt-auto my-4" />}
            </>
          )}
        </div>


        {/* row 4: count + total */}
        <div className="flex flex-col md:flex-row md:items-center gap-2 justify-between text-sm">
          <div className="flex items-center gap-1.5 shrink-0">
            <span className="text-muted-foreground">
              {booking.ticket_count}{" "}
              {booking.ticket_count === 1 ? "ticket" : "tickets"}
            </span>
            <Separator orientation="vertical" className="mx-1" />
            <span className="inline-flex items-center gap-1 text-muted-foreground">
              {isPending && "reservation expires on"}
              {isConfirmed && "confirmed on"}
              {isCancelled && "cancelled on"}
              {isExpired && "expired on"}
              <CalendarDays className="h-3.5 w-3.5 shrink-0" />
              {isPending && dateFormat.format(new Date(booking.expires_at!))}
              {(isConfirmed || isCancelled || isExpired) && dateFormat.format(new Date(booking.updated_at))}
            </span>
            {!isMobile && (
              <>
                <Separator orientation="vertical" className="mx-1" />
                <Badge variant="default" className={`${badgeColorMap[booking.status]} text-black capitalize`}>
                  {booking.status.split('_').join(' ')}
                </Badge>
              </>
            )}
          </div>
          <div className="mt-4 md:mt-0 flex justify-between md:justify-start items-center gap-4">
            <span className="font-semibold">
              {usd.format(booking.total_price)}
            </span>
            {isPending && (
              <Button
                className="cursor-pointer"
                variant="default"
                size="sm"
                onClick={handlePayment}
                disabled={isCreatingPaymentSession}
              >
                {isCreatingPaymentSession ? "Loading..." : "Pay Now"}
              </Button>
            )}
            {(isConfirmed || isPending) && !isMobile && <Separator orientation="vertical" />}
            {isConfirmed && (
              <Button
                className="cursor-pointer"
                variant="default"
                size="sm"
                onClick={() => {}}
                disabled={false}
              >
                View Tickets
              </Button>
            )}
            {isPending && (
              <Button
                className="cursor-pointer"
                variant="destructive"
                size="sm"
                onClick={handleCancelBooking}
                disabled={isCancelling}
              >
                {isCancelling ? "Cancelling…" : "Cancel booking"}
              </Button>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
