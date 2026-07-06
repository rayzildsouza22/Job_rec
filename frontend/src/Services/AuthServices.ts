import type {
  LoginData,
  RegisterData,
  TokenResponse,
  User,
} from "../types/auth";
import { AUTH_TOKEN_KEY, api } from "./api";

export async function registerUser(data: RegisterData): Promise<User> {
  const response = await api.post<User>("/auth/register", data);
  return response.data;
}

export async function loginUser(data: LoginData): Promise<void> {
  const response = await api.post<TokenResponse>("/auth/login", data);
  localStorage.setItem(AUTH_TOKEN_KEY, response.data.access_token);
}

export async function getCurrentUser(): Promise<User> {
  const response = await api.get<User>("/users/me");
  return response.data;
}

export function getToken(): string | null {
  return localStorage.getItem(AUTH_TOKEN_KEY);
}

export function logoutUser(): void {
  localStorage.removeItem(AUTH_TOKEN_KEY);
}
