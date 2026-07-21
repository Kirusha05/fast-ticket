import { useQuery, type UseQueryOptions } from "@tanstack/react-query";
import { useAuth0 } from "@auth0/auth0-react";
import { getBooking } from "../api/get-booking";

// Infers the return type of your API call automatically
type BookingData = Awaited<ReturnType<typeof getBooking>>;

export const useGetBooking = (
  bookingId: string, 
  // 1. Pass the inferred data type to UseQueryOptions
  // 2. Omit 'queryKey' and 'queryFn' so they can't be accidentally overridden
  options?: Omit<UseQueryOptions<BookingData>, 'queryKey' | 'queryFn'>
) => {
  const auth = useAuth0();

  return useQuery({
    queryKey: ["bookings", bookingId],
    queryFn: () => getBooking(auth, bookingId),
    ...options,
  });
};