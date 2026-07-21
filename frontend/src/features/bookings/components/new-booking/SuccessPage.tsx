import { getRouteApi, Link } from "@tanstack/react-router";
import { z } from "zod";
import { useGetBooking } from "@/features/bookings/hooks/useGetBooking";
import { CheckCircle2, Loader2, MapPin, Ticket } from "lucide-react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ticketSummary, usd } from "./utils";

const routeApi = getRouteApi("/bookings_/new_/success");

export const successfulBookingSchema = z.object({
  booking_id: z.string(),
});

export function SuccessPage() {
  const { booking_id } = routeApi.useSearch();

  // fetch every 2 seconds until status !== "pending"
  const { data: booking, isLoading } = useGetBooking(booking_id, {
    refetchInterval: (query) => {
      return query.state.data?.status === "pending" ? 2000 : false;
    },
  });

  if (!booking) {
    return <p>Error: Booking could not be found</p>;
  }

  const isPending = booking.status === "pending";

  return (
    <div className="min-h-[80vh] flex items-center justify-center p-4">
      <Card className="w-full max-w-lg overflow-hidden shadow-lg">
        {/* Event Banner */}
        {isLoading ? (
          <Skeleton className="h-full w-full" />
        ) : (
          <>
            <img
              src={booking.event.banner_url}
              alt={booking.event.name}
              className="aspect-[20/9] w-full object-cover"
            />
          </>
        )}

        {/* Status Header */}
        <CardHeader className="text-center -mt-12 relative z-10">
          <div className="flex justify-center mb-3">
            {isLoading || isPending ? (
              <div className="h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center backdrop-blur-md border-4 border-background">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
              </div>
            ) : (
              <div className="h-16 w-16 rounded-full bg-green-500/10 flex items-center justify-center backdrop-blur-md border-4 border-background">
                <CheckCircle2 className="h-8 w-8 text-green-500" />
              </div>
            )}
          </div>

          {isLoading ? (
            <Skeleton className="h-8 w-3/4 mx-auto" />
          ) : isPending ? (
            <CardTitle className="text-2xl">Processing payment...</CardTitle>
          ) : (
            <CardTitle className="text-2xl text-green-600">
              Booking Confirmed!
            </CardTitle>
          )}

          {isLoading ? (
            <Skeleton className="h-4 w-2/3 mx-auto mt-2" />
          ) : isPending ? (
            <CardDescription className="text-base mt-2">
              Your payment is being processed. This usually takes just a few
              seconds. Thanks for your patience!
            </CardDescription>
          ) : (
            <CardDescription className="text-base mt-2">
              Get ready! Your tickets for{" "}
              <span className="font-medium text-foreground">
                {booking.event.name}
              </span>{" "}
              are secured.
            </CardDescription>
          )}
        </CardHeader>

        <CardContent className="space-y-6">
          {booking && (
            <>
              {/* Event Details */}
              <div className="flex items-center gap-4 rounded-lg bg-muted/50 p-4">
                <div className="flex flex-col items-center justify-center bg-background border rounded-md p-2 w-14 h-14 shrink-0">
                  {/* Simple Date formatting */}
                  <span className="text-xs font-medium uppercase text-muted-foreground">
                    {new Date(booking.event.event_date).toLocaleDateString(
                      "en-US",
                      { month: "short" },
                    )}
                  </span>
                  <span className="text-xl font-bold leading-none">
                    {new Date(booking.event.event_date).getDate()}
                  </span>
                </div>
                <div className="flex flex-col gap-1 min-w-0">
                  <h3 className="font-semibold truncate">
                    {booking.event.name}
                  </h3>
                  <div className="flex items-center text-sm text-muted-foreground">
                    <MapPin className="mr-1 h-3 w-3 shrink-0" />
                    <span className="truncate">{booking.event.venue}</span>
                  </div>
                </div>
              </div>

              <Separator />

              {/* Order Summary */}
              <div className="space-y-2">
                <h4 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
                  Order Details
                </h4>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Booking ID</span>
                  <span className="font-mono font-medium">{booking.id}</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Items</span>
                  <span className="font-medium">{ticketSummary(booking)}</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Total</span>
                  <span className="font-medium">
                    {usd.format(booking.total_price)}
                  </span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Status</span>
                  <Badge
                    variant={isPending ? "outline" : "default"}
                    className="capitalize"
                  >
                    {booking.status}
                  </Badge>
                </div>
              </div>
            </>
          )}
        </CardContent>

        <CardFooter className="flex flex-col gap-2">
          <Button
            className="w-full"
            size="lg"
            asChild
            disabled={isLoading || isPending}
          >
            <Link to="/bookings">
              <Ticket className="mr-2 h-4 w-4" />
              {isPending ? "Waiting for confirmation..." : "View bookings"}
            </Link>
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}
