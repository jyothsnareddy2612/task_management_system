import { AxiosError } from "axios";

export function getApiErrorMessage(error: unknown) {
  if (error instanceof AxiosError) {
    const detail = error.response?.data?.error?.message ?? error.response?.data?.detail;
    if (typeof detail === "string") {
      return detail;
    }
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "Request failed";
}
