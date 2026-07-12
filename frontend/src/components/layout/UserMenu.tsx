import { useAuth0 } from "@auth0/auth0-react";
import { LogOutIcon, UserIcon } from "lucide-react";

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
  useSidebar
} from "@/components/ui";

export function UserMenu() {
  const { user, logout } = useAuth0();
  const { state } = useSidebar();

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button
          type="button"
          className={`flex w-full items-center gap-2 rounded-md ${state == "expanded" ? "p-2" : "py-2 justify-center"} text-left text-sm ring-sidebar-ring outline-hidden transition-[width,height,padding] hover:bg-sidebar-accent hover:text-sidebar-accent-foreground focus-visible:ring-2 cursor-pointer`}
        >
          {user?.picture ? (
            <img
              src={user.picture}
              alt={user.name ?? "User"}
              className="size-6 shrink-0 rounded-full"
            />
          ) : (
            <UserIcon className="size-4 shrink-0" />
          )}
          {state === "expanded" && (
            <span className="truncate font-medium">{user?.name ?? "User"}</span>
          )}
        </button>
      </DropdownMenuTrigger>

      <DropdownMenuContent
        align="end"
        side="right"
        sideOffset={18}
        className="w-64"
      >
        <div className="flex items-center gap-3 px-2 py-2">
          {user?.picture ? (
            <img
              src={user.picture}
              alt={user.name ?? "User"}
              className="size-10 shrink-0 rounded-full"
            />
          ) : (
            <div className="flex size-10 shrink-0 items-center justify-center rounded-full bg-muted">
              <UserIcon className="size-5" />
            </div>
          )}
          <div className="flex min-w-0 flex-col">
            <span className="truncate text-sm font-medium">
              {user?.name ?? "User"}
            </span>
            <span className="truncate text-xs text-muted-foreground">
              {user?.email ?? ""}
            </span>
          </div>
        </div>

        <DropdownMenuSeparator />

        <DropdownMenuItem
          variant="destructive"
          onClick={() =>
            logout({ logoutParams: { returnTo: window.location.origin } })
          }
        >
          <LogOutIcon />
          Sign Out
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}