import axios from "axios";

import { env } from "../config/env";
import { getAccessToken } from "./storage";

export const apiClient = axios.create({
  baseURL: env.apiBaseUrl,
  headers: {
    "Content-Type": "application/json",
  },
});

export const authClient = axios.create({
  baseURL: env.authBaseUrl,
  headers: {
    "Content-Type": "application/json",
  },
});

for (const client of [apiClient, authClient]) {
  client.interceptors.request.use((config) => {
    const token = getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  });
}
