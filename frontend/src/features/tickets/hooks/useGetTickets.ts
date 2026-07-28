import { useAuth0 } from "@auth0/auth0-react";
import { useQuery } from "@tanstack/react-query";
import { getTickets } from "../api/get-tickets";

export const useGetTickets = (bookingId: string) => {
  const auth = useAuth0();

  return useQuery({
    queryKey: ["tickets", bookingId],
    queryFn: () => getTickets(auth, bookingId),
  });
};
