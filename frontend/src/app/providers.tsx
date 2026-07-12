import { Auth0Provider } from "@auth0/auth0-react";
import { QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { RouterProvider } from "@tanstack/react-router";

import { router } from "./router";
import { queryClient } from "./query-client";

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
        <RouterProvider router={router} />
      </QueryClientProvider>
    </Auth0Provider>
  );
};
