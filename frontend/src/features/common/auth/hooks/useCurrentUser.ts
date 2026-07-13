import { useQuery } from "@tanstack/react-query";
import { useAuth0 } from "@auth0/auth0-react";
import { getCurrentUser } from "../api/get-current-user";

export const useCurrentUser = () => {
  const auth = useAuth0();

  return useQuery({
    queryKey: ["me"],
    queryFn: () => getCurrentUser(auth),
    // The query will not run until Auth0 will stop loading and the user will be confirmed to be authenticated
    enabled: !auth.isLoading && auth.isAuthenticated,
    staleTime: 3 * 3600 * 1000 // 3 hours
  });
};
