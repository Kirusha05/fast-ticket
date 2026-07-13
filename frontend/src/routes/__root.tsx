import { createRootRouteWithContext, Outlet } from "@tanstack/react-router";
import { TanStackRouterDevtools } from "@tanstack/router-devtools";

import { AppSidebar, AppNavbar } from "@/components/layout";
import { SidebarProvider, SidebarInset } from "@/components/ui/sidebar";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Toaster } from "@/components/ui/sonner";
import { useIsAdmin } from "@/features/common/auth/hooks/useIsAdmin";

export interface RouterContext {
  auth: {
    isAuthenticated: boolean;
    isLoading: boolean;
    isAdmin: boolean;
  }
}

export const Route = createRootRouteWithContext<RouterContext>()({
  component: RootLayout,
});

function RootLayout() {
  const isAdmin = useIsAdmin();

  return (
    <TooltipProvider>
      <SidebarProvider defaultOpen={isAdmin}>
        {isAdmin && <AppSidebar />}

        <SidebarInset>
          <AppNavbar />

          <main className="mt-12 flex-1 p-8 md:p-6">
            <Outlet />
          </main>
        </SidebarInset>

        {/* <TanStackRouterDevtools /> */}
      </SidebarProvider>

      <Toaster richColors />
    </TooltipProvider>
  );
}