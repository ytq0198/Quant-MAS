export const API_KEY_STORAGE_KEY = "quant_mas_api_key";

export function getStoredApiKey(): string {
  if (typeof window === "undefined") {
    return "";
  }
  return window.localStorage.getItem(API_KEY_STORAGE_KEY) || "";
}

export function setStoredApiKey(apiKey: string): void {
  if (typeof window === "undefined") {
    return;
  }
  const trimmed = apiKey.trim();
  if (trimmed) {
    window.localStorage.setItem(API_KEY_STORAGE_KEY, trimmed);
  } else {
    window.localStorage.removeItem(API_KEY_STORAGE_KEY);
  }
}

export async function readJson<T>(url: string): Promise<T> {
  const apiKey = getStoredApiKey();
  const response = await fetch(url, {
    headers: apiKey ? { "X-Quant-MAS-Key": apiKey } : undefined
  });
  if (!response.ok) {
    throw new Error(`${url} failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}
