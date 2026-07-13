export type UserRole = "user" | "admin";

export interface AppUser {
  id: string;
  name: string;
  email: string;
  auth0_id: string;
  role: UserRole;

  created_at: string;
  updated_at: string;
}
