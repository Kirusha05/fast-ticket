import { useQuery } from "@tanstack/react-query";
import { useAuth0 } from "@auth0/auth0-react";
import { getBookings } from "../api/get-bookings";

export const useGetBookings = () => {
  const auth = useAuth0();

  return useQuery({
    queryKey: ["bookings"],
    queryFn: () => getBookings(auth),
    meta: {
      errorMessage: "Failed to load bookings",
    },
  });
};