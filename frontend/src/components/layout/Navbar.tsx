import { Link, useLocation } from "@tanstack/react-router";
import { useAuth0 } from "@auth0/auth0-react";
import { LogInIcon, UserIcon, Ticket} from "lucide-react";

import { Button, SidebarTrigger } from "@/components/ui";
import { useIsAdmin } from "@/features/common/auth/hooks/useIsAdmin";
import { NAV_ITEMS } from "./nav-items";
import { UserMenu } from "./UserMenu";
import { useIsMobile } from "@/hooks/use-mobile";

export function AppNavbar() {
  const { isLoading, isAuthenticated, loginWithRedirect, user } =
    useAuth0();
  const location = useLocation();
  const isAdmin = useIsAdmin();
  const isMobile = useIsMobile();

  return (
    <header className="bg-black/30 z-50 shrink-0 border-b px-6 fixed w-full left-0 top-0 backdrop-blur-lg">
      <div className="container mx-auto flex items-center gap-3 h-12">        
        {/* Logo */}
        <Link
          to="/"
          className="truncate font-bold text-xl leading-none flex items-center"
        >
          <Ticket className="h-5 w-5 mr-2" />
          FastTicket
        </Link>

        {/* Desktop nav links */}
        <nav className="ml-4 hidden items-center gap-1 md:flex">
          {NAV_ITEMS.filter(item => {
            if (item.authRequired && !isAuthenticated) return false;
            if (item.adminRequired && !isAdmin) return false;
            return true;
          }).map((item) => {
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
            <Button disabled>
              <UserIcon className="animate-pulse" />
              <span>Loading…</span>
            </Button>
          ) : isAuthenticated && user ? (
            <UserMenu />
          ) : (
            <Button
              className="cursor-pointer"
              title="Sign in"
              onClick={() => loginWithRedirect()}
            >
              <LogInIcon />
              <span>Sign In</span>
            </Button>
          )}
        </div>

        {isMobile && <SidebarTrigger />}
      </div>
    </header>
  );
}