import { Link, useLocation } from "@tanstack/react-router";
import { useAuth0 } from "@auth0/auth0-react";
import { LogInIcon, LogOutIcon, UserIcon } from "lucide-react";

import { SidebarTrigger } from "@/components/ui/sidebar";
import { Button } from "@/components/ui/button";

const NAV_ITEMS = [
  { to: "/", label: "Home" },
  { to: "/events", label: "Events" },
] as const;

export function AppNavbar() {
  const { isLoading, isAuthenticated, loginWithRedirect, logout } =
    useAuth0();
  const location = useLocation();

  return (
    <header className="flex h-12 shrink-0 items-center gap-3 border-b px-3">
      <SidebarTrigger />

      {/* Desktop nav links */}
      <nav className="hidden items-center gap-1 md:flex">
        {NAV_ITEMS.map((item) => {
          const isActive = location.pathname === item.to;
          return (
            <Button
              key={item.to}
              variant={isActive ? "secondary" : "ghost"}
              size="sm"
              asChild
            >
              <Link to={item.to}>
                {item.label}
              </Link>
            </Button>
          );
        })}
      </nav>

      <div className="flex-1" />

      {/* Auth button in navbar (visible on desktop, hidden when sidebar footer shows it on mobile) */}
      <div className="hidden md:block">
        {isLoading ? (
          <Button variant="ghost" size="sm" disabled>
            <UserIcon className="animate-pulse" />
            Loading…
          </Button>
        ) : isAuthenticated ? (
          <Button
            variant="ghost"
            size="sm"
            onClick={() =>
              logout({
                logoutParams: { returnTo: window.location.origin },
              })
            }
          >
            <LogOutIcon />
            <span className="hidden lg:inline">Sign Out</span>
          </Button>
        ) : (
          <Button
            variant="default"
            size="sm"
            onClick={() => loginWithRedirect()}
          >
            <LogInIcon />
            <span className="hidden lg:inline">Sign In</span>
          </Button>
        )}
      </div>
    </header>
  );
}