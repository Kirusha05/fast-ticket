import { apiFetch } from "@/lib/utils";
import type { Auth0ContextInterface, User } from "@auth0/auth0-react";
import type { AppUser } from "../types";

export const getCurrentUser = async (
  auth: Auth0ContextInterface<User>
) => {
  const authToken = await auth.getAccessTokenSilently();
  return apiFetch<AppUser>('/users/me', { authToken })
};