import { Link, useLocation } from "@tanstack/react-router";
import { useAuth0 } from "@auth0/auth0-react";
import { CalendarIcon, HomeIcon, LogInIcon, UserIcon } from "lucide-react";

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
} from "@/components/ui/sidebar";
import { UserMenu } from "./UserMenu";

const NAV_ITEMS = [
  { to: "/", label: "Home", icon: HomeIcon },
  { to: "/events", label: "Events", icon: CalendarIcon },
] as const;

export function AppSidebar() {
  const { isLoading, isAuthenticated, user, loginWithRedirect } =
    useAuth0();
  const location = useLocation();

  return (
    <SidebarPrimitive collapsible="icon" variant="sidebar">
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg" asChild>
              <Link to="/">
                <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                  <CalendarIcon className="size-4" />
                </div>
                <div className="flex flex-col gap-0.5 leading-none">
                  <span className="font-semibold">FastTicket</span>
                  <span className="text-xs text-muted-foreground">
                    All the events you love
                  </span>
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
              {NAV_ITEMS.map((item) => (
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