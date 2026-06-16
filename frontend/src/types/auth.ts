export type UserRole = "ADMIN" | "WORKER";

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  is_active: boolean;
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest extends LoginRequest {
  name: string;
  role: UserRole;
}
