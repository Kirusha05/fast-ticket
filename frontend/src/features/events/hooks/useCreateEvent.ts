import { useAuth0 } from "@auth0/auth0-react";
import { useMutation } from "@tanstack/react-query";
import type { CreateEventRequest } from "../types";
import { createEvent } from "../api/create-event";
import { queryClient } from "@/app/query-client";

export const useCreateEvent = () => {
  const auth = useAuth0();

  return useMutation({
    mutationFn: (body: CreateEventRequest) => createEvent(auth, body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["events"] });
    },
  });
};
