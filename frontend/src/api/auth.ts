import { readJson } from "./client";

export interface AuthMePayload {
  auth_mode: string;
  role: string;
  key_fingerprint: string | null;
}

export const fallbackAuth: AuthMePayload = {
  auth_mode: "open",
  role: "admin",
  key_fingerprint: null
};

export function fetchAuthMe(): Promise<AuthMePayload> {
  return readJson<AuthMePayload>("/api/auth/me");
}
