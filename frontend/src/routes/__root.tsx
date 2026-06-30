import { createRootRoute, Outlet } from "@tanstack/react-router";
import { TanStackRouterDevtools } from "@tanstack/router-devtools";

import { AppSidebar, AppNavbar } from "@/components/layout";
import { SidebarProvider, SidebarInset } from "@/components/ui/sidebar";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Toaster } from "@/components/ui/sonner";

export const Route = createRootRoute({
  component: RootLayout,
});

function RootLayout() {
  return (
    <TooltipProvider>
      <SidebarProvider defaultOpen={true}>
        <AppSidebar />

        <SidebarInset>
          <AppNavbar />

          <main className="flex-1 p-4 md:p-6">
            <Outlet />
          </main>
        </SidebarInset>

        {/* <TanStackRouterDevtools /> */}
      </SidebarProvider>

      <Toaster richColors />
    </TooltipProvider>
  );
}