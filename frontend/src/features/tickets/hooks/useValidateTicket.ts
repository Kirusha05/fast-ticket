import { useAuth0 } from "@auth0/auth0-react";
import { useMutation } from "@tanstack/react-query";
import type { ValidateTicketRequest } from "../types";
import { validateTicket } from "../api/validate-ticket";

export const useValidateTicket = () => {
  const auth = useAuth0();

  return useMutation({
    mutationFn: (body: ValidateTicketRequest) => validateTicket(auth, body),
  });
};
