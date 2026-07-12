import { Link } from "@tanstack/react-router";
import {
  CalendarDays,
  MapPin,
  Ticket,
  ArrowLeft,
  AlertCircle,
} from "lucide-react";

import { Route } from "@/routes/events_.$eventId";
import { useGetEvent } from "@/features/events/hooks/useGetEvent";
import {
  Button,
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
  Skeleton,
  Separator,
} from "@/components/ui";
import { EventType } from "@/features/events/types";
import type { Event } from "@/features/events/types";

function getLowestPrice(event: Event): number | null {
  if (event.event_type === EventType.SEATED && event.seats.length > 0) {
    return Math.min(...event.seats.map((s) => s.price));
  }
  if (event.event_type === EventType.OPEN_FIELD && event.tiers.length > 0) {
    return Math.min(...event.tiers.map((t) => t.price));
  }
  return null;
}

function formatDateTime(dateStr: string): string {
  const date = new Date(dateStr);
  return new Intl.DateTimeFormat("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(date);
}

export function EventPage() {
  const { eventId } = Route.useParams();
  const { data: event, isPending, isFetching, isError, error } = useGetEvent(eventId);

  console.log("Event: ", event);

  if (isPending) {
    return (
      <div className="space-y-10">
        {/* Banner skeleton */}
        <Skeleton className="aspect-[16/9] max-w-4xl rounded-xl mx-auto" />

        {/* Two-column skeleton grid */}
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-8">
          <div className="space-y-4 lg:col-span-6">
            {/* Title skeleton */}
            <Skeleton className="h-9 w-2/3" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-5/6" />
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-4 w-1/2" />
          </div>
          <div className="lg:col-span-2">
            <div className="overflow-hidden rounded-xl ring-1 ring-foreground/10">
              <div className="space-y-3 p-4">
                <Skeleton className="h-6 w-1/2" />
                <Skeleton className="h-4 w-3/4" />
                <Skeleton className="h-4 w-1/3" />
                <Skeleton className="h-10 w-full" />
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (isError) {
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
          <CardFooter>
            <Button variant="outline" asChild>
              <Link to="/events">
                <ArrowLeft className="mr-1 h-4 w-4" />
                Back to events
              </Link>
            </Button>
          </CardFooter>
        </Card>
      </div>
    );
  }

  const lowestPrice = getLowestPrice(event);
  const formattedDate = formatDateTime(event.event_date);
  const ticketNoun = event.event_type === EventType.SEATED ? "seats" : "tickets";

  return (
    <div className="space-y-10">
      {/* Banner image */}
      {event.banner_url && (
        <div className="max-w-4xl mx-auto">
          <img
            src={event.banner_url}
            alt={event.name}
            className="aspect-[16/9] w-full rounded-xl object-cover"
          />
        </div>
      )}

      {/* Two-column layout */}
      <div className="grid grid-cols-1 gap-8 lg:grid-cols-8">
        {/* Left column, event details */}
        <div className="space-y-4 lg:col-span-6">
          {/* Event name */}
          <h1 className="text-3xl font-bold tracking-tight">{event.name}</h1>
          {/* Description */}
          <p className="text-base leading-relaxed text-muted-foreground">
            {event.description}
          </p>

          <Separator />

          {/* Venue */}
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-muted">
              <MapPin className="h-5 w-5 text-muted-foreground" />
            </div>
            <div>
              <p className="text-sm font-medium">Where?</p>
              <p className="text-sm text-muted-foreground">{event.venue}</p>
            </div>
          </div>

          {/* Date & time */}
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-muted">
              <CalendarDays className="h-5 w-5 text-muted-foreground" />
            </div>
            <div>
              <p className="text-sm font-medium">When?</p>
              <p className="text-sm text-muted-foreground">{formattedDate}</p>
            </div>
          </div>
        </div>

        {/* Right column, ticket CTA card */}
        <div className="lg:col-span-2">
          <Card className="sticky top-6">
            <CardHeader>
              <div className="flex items-center justify-start gap-0.5">
                <Ticket className="h-5 w-5 text-muted-foreground mr-2" />
                <CardTitle>Tickets</CardTitle>
              </div>
            </CardHeader>

            <Separator />

            <CardContent className="space-y-4 pt-4">
              {/* Available count */}
              <div className="text-center">
                <span className="text-4xl font-bold tracking-tight">
                  {event.available_tickets}
                </span>
                <p className="text-sm text-muted-foreground">
                  {ticketNoun} left
                </p>
              </div>

              {/* Starting price */}
              {lowestPrice !== null && (
                <p className="text-center text-sm text-muted-foreground">
                  Tickets starting from{" "}
                  <span className="font-semibold text-foreground">
                    ${lowestPrice.toFixed(2)}
                  </span>
                </p>
              )}
            </CardContent>

            <CardFooter>
              {event.available_tickets > 0 ? (
                <Button className="w-full cursor-pointer" size="lg" asChild>
                  <Link to="/bookings/new" search={{ event_id: event.id }}>Get Tickets</Link>
                </Button>
              ) : (
                <p className="w-full text-center text-sm text-muted-foreground">
                  SOLD OUT
                </p>
              )}
            </CardFooter>
          </Card>
        </div>
      </div>

      {/* Background fetching indicator */}
      {isFetching && (
        <div className="fixed bottom-4 right-4 z-50">
          <Skeleton className="h-5 w-5 rounded-full" />
        </div>
      )}
    </div>
  );
}
