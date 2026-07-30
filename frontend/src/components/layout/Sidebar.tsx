import { Link, useLocation } from "@tanstack/react-router";
import { useAuth0 } from "@auth0/auth0-react";
import { CalendarIcon, LogInIcon, Ticket, UserIcon } from "lucide-react";

import {
  Sidebar as SidebarPrimitive,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar";
import { UserMenu } from "./UserMenu";
import { NAV_ITEMS } from "./nav-items";
import { useIsAdmin } from "@/features/common/auth/hooks/useIsAdmin";
import { useEffect } from "react";

export function AppSidebar() {
  const { isLoading, isAuthenticated, user, loginWithRedirect } = useAuth0();
  const location = useLocation();
  const isAdmin = useIsAdmin();
  const { setOpenMobile, isMobile } = useSidebar();

  // automatically close the mobile menu whenever the path changes
  useEffect(() => {
    if (isMobile) {
      setOpenMobile(false);
    }
  }, [location.pathname, isMobile, setOpenMobile]);

  return (
    <SidebarPrimitive collapsible="icon" variant="sidebar">
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg" asChild>
              <Link to="/" className="font-bold text-xl leading-none">
                <div className="flex flex items-center">
                  <Ticket className="h-5! w-5! mr-2" />
                  <p className="font-semibold">FastTicket</p>
                </div>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu className="gap-1">
              {NAV_ITEMS.filter((item) => {
                if (item.authRequired && !isAuthenticated) return false;
                if (item.adminRequired && !isAdmin) return false;
                return true;
              }).map((item) => (
                <SidebarMenuItem key={item.to}>
                  <SidebarMenuButton
                    asChild
                    isActive={location.pathname === item.to}
                    tooltip={item.label}
                  >
                    <Link to={item.to}>
                      <item.icon />
                      <span>{item.label}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter>
        <SidebarMenu>
          <SidebarMenuItem>
            {isLoading ? (
              <SidebarMenuButton disabled>
                <UserIcon className="animate-pulse" />
                <span>Loading…</span>
              </SidebarMenuButton>
            ) : isAuthenticated && user ? (
              <UserMenu />
            ) : (
              <SidebarMenuButton
                asChild
                tooltip="Sign in"
                onClick={() => loginWithRedirect()}
              >
                <button type="button">
                  <LogInIcon />
                  <span>Sign In</span>
                </button>
              </SidebarMenuButton>
            )}
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
    </SidebarPrimitive>
  );
}
