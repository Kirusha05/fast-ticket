import { useCurrentUser } from "./useCurrentUser";

export const useIsAdmin = () => {
  const { data: user } = useCurrentUser();
  return user?.role === "admin";
};
