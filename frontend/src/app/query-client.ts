import { MutationCache, QueryCache, QueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

function extractMessage(error: unknown): string {
  if (error instanceof Error) return error.message;
  if (typeof error === "string") return error;
  return "An unexpected error occurred";
}

export const queryClient = new QueryClient({
  queryCache: new QueryCache({
    onError(error, query) {
      toast.error(
        extractMessage(error) ??
        (query.meta?.errorMessage as string | undefined) ??
        "Failed to load data"
      , { position: "bottom-right" });
    },
  }),
  mutationCache: new MutationCache({
    onError(error, _variables, _context, mutation) {
      toast.error(
        extractMessage(error) ??
        (mutation.meta?.errorMessage as string | undefined) ??
        "Operation failed"
      , { position: "bottom-right" });
    },
  }),
  defaultOptions: {
    queries: {
      retry: 0,
      staleTime: 60 * 1000, // 60 sec
      refetchOnWindowFocus: true,
    }
  },
});
