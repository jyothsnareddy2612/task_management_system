import { authClient } from "../../../lib/http";
import type { LoginRequest, RegisterRequest, TokenPair, User } from "../../../types/auth";

export const authService = {
  async login(payload: LoginRequest) {
    const { data } = await authClient.post<TokenPair>("/auth/login", payload);
    return data;
  },

  async register(payload: RegisterRequest) {
    const { data } = await authClient.post<User>("/auth/register", payload);
    return data;
  },

  async me() {
    const { data } = await authClient.get<User>("/auth/me");
    return data;
  },

  getGoogleLoginUrl() {
    return `${authClient.defaults.baseURL}/auth/google/login`;
  },
};
