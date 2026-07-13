import { Auth0Provider, useAuth0 } from "@auth0/auth0-react";
import { QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { RouterProvider } from "@tanstack/react-router";

import { router } from "./router";
import { queryClient } from "./query-client";
import { useEffect, useState } from "react";
import { useCurrentUser } from "@/features/common/auth/hooks/useCurrentUser";
import { LoadingScreen } from "@/components/layout";

export function Providers() {
  return (
    <Auth0Provider
      domain={import.meta.env.VITE_AUTH0_DOMAIN}
      clientId={import.meta.env.VITE_AUTH0_CLIENT_ID}
      authorizationParams={{
        redirect_uri: window.location.origin,
        audience: import.meta.env.VITE_AUTH0_AUDIENCE,
      }}
      cacheLocation="localstorage"
    >
      <QueryClientProvider client={queryClient}>
        {/* <ReactQueryDevtools initialIsOpen={false} position="bottom" /> */}
        <RouterProviderWithContext />
      </QueryClientProvider>
    </Auth0Provider>
  );
}

// writing this as a separate context so we can use the useAuth0 hook and populate the router context with auth data
function RouterProviderWithContext() {
  const { isAuthenticated, isLoading: isAuth0Loading } = useAuth0();
  const { data: user, isPending: isLoadingAppUser } = useCurrentUser();

  const [isFakeLoading, setIsFakeLoading] = useState(true);

  useEffect(() => {
    setTimeout(() => {
      setIsFakeLoading(false);
    }, 500)
  }, [])

  // using fake loading during dev for better loading visual on fast localhost
  if (isFakeLoading || (isAuthenticated && isLoadingAppUser)) {
    return <LoadingScreen />
  }

  const isAdmin = user?.role === "admin";

  return (
    <RouterProvider
      router={router}
      context={{
        auth: { isAuthenticated, isLoading: isFakeLoading, isAdmin },
      }}
    />
  );
}
