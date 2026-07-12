import { useGetBookings } from "@/features/bookings/hooks/useGetBookings";
import { BookingCard } from "./BookingCard";
import { Skeleton } from "@/components/ui/skeleton";
import { Loader2 } from "lucide-react";

export function BookingsPage() {
  const {
    data: bookings,
    isPending,
    isFetching,
    isError,
    error,
  } = useGetBookings();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Bookings</h1>
      </div>

      {/* Loading skeletons */}
      {isPending && (
        <div className="space-y-4">
          {Array.from({ length: 5 }).map((_, i) => (
            <div
              key={i}
              className="flex overflow-hidden rounded-xl ring-1 ring-foreground/10"
            >
              <Skeleton className="aspect-[4/3] h-60 shrink-0 rounded-none" />
              <div className="flex flex-1 flex-col gap-3 p-4">
                <div className="flex items-start justify-between">
                  <Skeleton className="h-4 w-2/3" />
                  <Skeleton className="h-5 w-20 rounded-full" />
                </div>
                <Skeleton className="h-3 w-1/3" />
                <Skeleton className="h-3 w-1/2" />
                <div className="mt-auto flex items-center justify-between">
                  <Skeleton className="h-4 w-16" />
                  <Skeleton className="h-4 w-20" />
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {isError && <div>An error has occured: {error.message}</div>}

      {bookings && !bookings.length && <p>No bookings yet.</p>}

      {bookings && bookings.length > 0 && (
        <div className="space-y-4">
          {bookings.sort((a, b) => b.created_at.localeCompare(a.created_at)).map((booking) => (
            <BookingCard key={booking.id} booking={booking} />
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