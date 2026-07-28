import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export async function apiFetch<T>(
  url: string,  // should include trailing slash i.e. /path
  { authToken, ...init }: RequestInit & { authToken?: string } = {}
): Promise<T> {
  const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}${url}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(authToken && { Authorization: `Bearer ${authToken}` }),
      ...init.headers,
    },
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    // console.log(body)
    let message =
      body?.detail ?? body?.message ?? `Request failed with status ${response.status}`;

    // Pydantic validation error
    if (response.status == 422 && Array.isArray(message)) {
      message = message[0].msg;
    }
    throw new Error(message);
  }

  return response.json();
}