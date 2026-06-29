import { apiFetch } from "@/lib/utils";
import type { CreateEventRequest, Event } from "../types";
import type { Auth0ContextInterface, User } from "@auth0/auth0-react";

export const createEvent = async (
  auth: Auth0ContextInterface<User>,
  body: CreateEventRequest,
) => {
  const authToken = await auth.getAccessTokenSilently();

  return apiFetch<Event>("/events", {
    authToken,
    method: "POST",
    body: JSON.stringify(body),
  });
};
