import { useQuery } from "@tanstack/react-query";
import { useAuth0 } from "@auth0/auth0-react";
import { getBooking } from "../api/get-booking";

export const useGetBooking = (bookingId: string) => {
  const auth = useAuth0();

  return useQuery({
    queryKey: ["bookings", bookingId],
    queryFn: () => getBooking(auth, bookingId),
  });
};