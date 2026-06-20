import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

import { clearTokens, getAccessToken, saveTokens } from "../../../lib/storage";
import type { LoginRequest, RegisterRequest, User } from "../../../types/auth";
import { getApiErrorMessage } from "../../../services/apiError";
import { authService } from "../services/authService";

type AuthContextValue = {
  error: string | null;
  isLoading: boolean;
  login: (payload: LoginRequest) => Promise<void>;
  logout: () => void;
  register: (payload: RegisterRequest) => Promise<void>;
  user: User | null;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(Boolean(getAccessToken()));

  const loadCurrentUser = useCallback(async () => {
    const params = new URLSearchParams(window.location.search);
    const accessToken = params.get("access_token");
    const refreshToken = params.get("refresh_token");

    if (accessToken && refreshToken) {
      saveTokens(accessToken, refreshToken);
      window.history.replaceState({}, document.title, window.location.pathname);
    }

    if (!getAccessToken()) {
      setIsLoading(false);
      return;
    }

    try {
      setUser(await authService.me());
    } catch {
      clearTokens();
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadCurrentUser();
  }, [loadCurrentUser]);

  const login = useCallback(async (payload: LoginRequest) => {
    setError(null);
    setIsLoading(true);
    try {
      const tokens = await authService.login(payload);
      saveTokens(tokens.access_token, tokens.refresh_token);
      setUser(await authService.me());
    } catch (error) {
      setError(getApiErrorMessage(error));
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const register = useCallback(async (payload: RegisterRequest) => {
    setError(null);
    setIsLoading(true);
    try {
      await authService.register(payload);
      const tokens = await authService.login({ email: payload.email, password: payload.password });
      saveTokens(tokens.access_token, tokens.refresh_token);
      setUser(await authService.me());
    } catch (error) {
      setError(getApiErrorMessage(error));
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    clearTokens();
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({ error, isLoading, login, logout, register, user }),
    [error, isLoading, login, logout, register, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return value;
}
