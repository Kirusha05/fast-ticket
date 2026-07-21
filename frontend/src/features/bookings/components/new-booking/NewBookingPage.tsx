import { z } from "zod";
import { getRouteApi, useNavigate, Link } from "@tanstack/react-router";
import {
  CalendarDays,
  MapPin,
  Ticket,
  ArrowLeft,
  AlertCircle,
  Loader2,
  ShoppingCart,
  AlertCircleIcon,
} from "lucide-react";
import { toast } from "sonner";

import { useGetEvent } from "@/features/events/hooks/useGetEvent";
import { useCreateBooking } from "@/features/bookings/hooks/useCreateBooking";
import { useNewBookingStore } from "@/features/bookings/stores/useNewBookingStore";
import { EventType } from "@/features/events/types";
import { SeatSelector } from "./SeatSelector";
import { TierSelector } from "./TierSelector";
import {
  buildBookingRequest,
  countTickets,
  sumSeatsPrice,
  sumTiersPrice,
} from "./utils";
import {
  Button,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Skeleton,
  Separator,
  Alert,
  AlertTitle,
  AlertDescription
} from "@/components/ui";
import { useAuth0 } from "@auth0/auth0-react";

const routeApi = getRouteApi("/bookings_/new");

export const newBookingSchema = z.object({
  event_id: z.string(),
});

const formatDateTime = (dateStr: string): string => {
  const date = new Date(dateStr);
  return new Intl.DateTimeFormat("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(date);
};

export function NewBookingPage() {
  const { event_id } = routeApi.useSearch();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth0();
  const { data: event, isPending, isError, error } = useGetEvent(event_id);
  const { mutate: createBooking, isPending: isBooking } = useCreateBooking();

  const selectedSeatIds = useNewBookingStore((s) => s.selectedSeatIds);
  const tierCounts = useNewBookingStore((s) => s.tierCounts);
  const reset = useNewBookingStore((s) => s.reset);

  const isSeated = event?.event_type === EventType.SEATED;

  const totalPrice = event
    ? isSeated
      ? sumSeatsPrice(event.seats, selectedSeatIds)
      : sumTiersPrice(event.tiers, tierCounts)
    : 0;
  const totalTickets = event
    ? countTickets(event, selectedSeatIds, tierCounts)
    : 0;

  // At least one ticket must be selected to submit.
  const canSubmit = totalTickets > 0;

  function handleBookTickets() {
    if (!event || !canSubmit) return;

    createBooking(buildBookingRequest(event, selectedSeatIds, tierCounts), {
      onSuccess: () => {
        toast.success("Booking created!");
        reset();
        navigate({ to: "/bookings" });
      },
      onError: (err) => {
        toast.error(err.message ?? "Failed to create booking.");
      },
    });
  }

  if (isPending) {
    return (
      <div className="mx-auto max-w-4xl space-y-8 py-6">
        {/* Banner skeleton */}
        <Skeleton className="aspect-[16/9] w-full rounded-xl" />

        <div className="space-y-4">
          <Skeleton className="h-8 w-2/3" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-5/6" />
        </div>

        <Separator />

        {/* Tickets skeleton */}
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-16 w-full rounded-lg" />
          ))}
        </div>
      </div>
    );
  }

  if (isError || !event) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <Card className="w-full max-w-md">
          <CardHeader>
            <div className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-destructive" />
              <CardTitle>Failed to load event</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              {error?.message ?? "An unexpected error occurred."}
            </p>
          </CardContent>
          <div className="flex items-center gap-3 px-(--card-spacing) pb-(--card-spacing)">
            <Button variant="outline" asChild>
              <Link to="/events">
                <ArrowLeft className="mr-1 h-4 w-4" />
                Back to events
              </Link>
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  const formattedDate = formatDateTime(event.event_date);

  return (
    <div className="mx-auto max-w-4xl space-y-8">
      {/* ---------- Event summary card ---------- */}
      <Card className="overflow-hidden">
        {event.banner_url && (
          <img
            src={event.banner_url}
            alt={event.name}
            className="aspect-[16/9] w-full object-cover"
          />
        )}
        <CardContent>
          <h1 className="text-2xl font-bold tracking-tight">{event.name}</h1>

          <div className="mt-4 flex flex-wrap items-center gap-x-6 gap-y-4">
            {/* Venue */}
            <div className="flex items-center gap-2">
              <MapPin className="h-4 w-4 text-muted-foreground shrink-0" />
              <span className="text-sm text-muted-foreground">
                {event.venue}
              </span>
            </div>

            {/* Date */}
            <div className="flex items-center gap-2">
              <CalendarDays className="h-4 w-4 text-muted-foreground shrink-0" />
              <span className="text-sm text-muted-foreground">
                {formattedDate}
              </span>
            </div>

            {/* Available count */}
            <div className="flex items-center gap-2">
              <Ticket className="h-4 w-4 text-muted-foreground shrink-0" />
              <span className="text-sm text-muted-foreground">
                {event.available_tickets}{" "}
                {event.event_type === EventType.SEATED ? "seats" : "tickets"}{" "}
                left
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* ---------- Seats / Tickets configuration ---------- */}
      <section className="space-y-4">
        <h2 className="text-lg font-semibold">
          {event.event_type === EventType.SEATED
            ? "Select your seats"
            : "Select your tickets"}
        </h2>

        {event.event_type === EventType.SEATED ? (
          <SeatSelector seats={event.seats} />
        ) : (
          <TierSelector tiers={event.tiers} />
        )}
      </section>

      {!isAuthenticated && (
        <Alert variant="destructive" className="max-w">
          <AlertCircleIcon />
          <AlertTitle>Authentication required</AlertTitle>
          <AlertDescription>
            You must authenticate before booking any tickets.
          </AlertDescription>
        </Alert>
      )}

      {/* ---------- Booking summary ---------- */}
      <Card>
        <CardContent>
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <p className="text-sm text-muted-foreground">
                {totalTickets} {totalTickets === 1 ? "ticket" : "tickets"}
              </p>
              <p className="text-2xl font-bold">${totalPrice.toFixed(2)}</p>
            </div>

            <Button
              size="lg"
              disabled={!canSubmit || isBooking || !isAuthenticated}
              onClick={handleBookTickets}
            >
              {isBooking ? (
                <>
                  <Loader2 className="mr-1 h-4 w-4 animate-spin" />
                  Booking...
                </>
              ) : (
                <>
                  <ShoppingCart className="mr-1 h-4 w-4" />
                  Book tickets
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
