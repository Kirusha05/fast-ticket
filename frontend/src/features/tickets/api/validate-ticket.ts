import { apiFetch } from "@/lib/utils";
import type { ValidateTicketRequest, Ticket } from "../types";
import type { Auth0ContextInterface, User } from "@auth0/auth0-react";

export const validateTicket = async (
  auth: Auth0ContextInterface<User>,
  body: ValidateTicketRequest,
) => {
  const authToken = await auth.getAccessTokenSilently();

  return apiFetch<Ticket>("/tickets/validate", {
    authToken,
    method: "POST",
    body: JSON.stringify(body),
  });
};
