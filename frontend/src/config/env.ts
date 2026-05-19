const defaultApiBaseUrl = "http://localhost:8000/api/v1";
const defaultAuthBaseUrl = "http://localhost:8001/api/v1";

function toWebSocketUrl(apiBaseUrl: string) {
  const url = new URL(apiBaseUrl);
  url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
  url.pathname = `${url.pathname.replace(/\/$/, "")}/ws/tasks`;
  return url.toString();
}

export const env = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL ?? defaultApiBaseUrl,
  authBaseUrl: import.meta.env.VITE_AUTH_BASE_URL ?? defaultAuthBaseUrl,
  taskEventsUrl: import.meta.env.VITE_TASK_EVENTS_URL ?? toWebSocketUrl(import.meta.env.VITE_API_BASE_URL ?? defaultApiBaseUrl),
};
