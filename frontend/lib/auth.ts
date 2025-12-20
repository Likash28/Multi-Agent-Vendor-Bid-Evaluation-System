import { jwtDecode } from "jwt-decode";

const TOKEN_KEY = "auth_token";
const REFRESH_TOKEN_KEY = "refresh_token";

export interface DecodedToken {
  sub: string;
  email: string;
  name?: string;
  exp: number;
  iat: number;
}

/**
 * Get the stored authentication token
 */
export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

/**
 * Store the authentication token
 */
export function setToken(token: string): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(TOKEN_KEY, token);
}

/**
 * Remove the authentication token
 */
export function removeToken(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem(TOKEN_KEY);
}

/**
 * Get the stored refresh token
 */
export function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

/**
 * Store the refresh token
 */
export function setRefreshToken(token: string): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(REFRESH_TOKEN_KEY, token);
}

/**
 * Remove the refresh token
 */
export function removeRefreshToken(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  const token = getToken();
  if (!token) return false;

  try {
    const decoded = decodeToken(token);
    // Check if token is expired
    const currentTime = Date.now() / 1000;
    return decoded.exp > currentTime;
  } catch (error) {
    return false;
  }
}

/**
 * Decode the JWT token
 */
export function decodeToken(token?: string): DecodedToken {
  const authToken = token || getToken();
  if (!authToken) {
    throw new Error("No token available");
  }

  try {
    return jwtDecode<DecodedToken>(authToken);
  } catch (error) {
    throw new Error("Invalid token");
  }
}

/**
 * Get user info from token
 */
export function getUserFromToken(): DecodedToken | null {
  try {
    const token = getToken();
    if (!token) return null;
    return decodeToken(token);
  } catch (error) {
    return null;
  }
}

/**
 * Clear all authentication data
 */
export function clearAuth(): void {
  removeToken();
  removeRefreshToken();
}
