import { createRootRouteWithContext, Outlet } from "@tanstack/react-router";
// import { TanStackRouterDevtools } from "@tanstack/router-devtools";

import { AppSidebar, AppNavbar } from "@/components/layout";
import { SidebarProvider, SidebarInset } from "@/components/ui/sidebar";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Toaster } from "@/components/ui/sonner";
import { useIsMobile } from "@/hooks/use-mobile";
import { Footer } from "@/features/footer/components";

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
  const isMobile = useIsMobile();

  return (
    <TooltipProvider>
      <SidebarProvider defaultOpen={false}>
        {isMobile && <AppSidebar />}

        <SidebarInset>
          <AppNavbar />

          <main className="mt-12 flex-1 p-6">
            <Outlet />
          </main>
          <Footer />
        </SidebarInset>

        {/* <TanStackRouterDevtools /> */}
      </SidebarProvider>

      <Toaster richColors />
    </TooltipProvider>
  );
}