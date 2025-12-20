import { create } from "zustand";
import { persist } from "zustand/middleware";
import api from "@/lib/api";
import {
  setToken,
  removeToken,
  setRefreshToken,
  removeRefreshToken,
  getUserFromToken,
  clearAuth,
} from "@/lib/auth";

export interface User {
  id: string;
  email: string;
  name: string;
  department?: string;
  role?: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  login: (email: string, password: string) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
  setUser: (user: User | null) => void;
  clearError: () => void;
  initializeAuth: () => void;
}

export interface RegisterData {
  name: string;
  email: string;
  password: string;
  department?: string;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isLoading: false,
      error: null,

      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null });
        try {
          const response = await api.post("/auth/login", {
            email,
            password,
          });

          const { access_token, refresh_token, user } = response.data;

          setToken(access_token);
          if (refresh_token) {
            setRefreshToken(refresh_token);
          }

          set({
            user,
            token: access_token,
            isLoading: false,
            error: null,
          });
        } catch (error: any) {
          const errorMessage =
            error.response?.data?.message || error.message || "Login failed";
          set({
            error: errorMessage,
            isLoading: false,
            user: null,
            token: null,
          });
          throw error;
        }
      },

      register: async (data: RegisterData) => {
        set({ isLoading: true, error: null });
        try {
          await api.post("/auth/register", data);
          set({ isLoading: false, error: null });
        } catch (error: any) {
          const errorMessage =
            error.response?.data?.message ||
            error.message ||
            "Registration failed";
          set({ error: errorMessage, isLoading: false });
          throw error;
        }
      },

      logout: () => {
        clearAuth();
        set({
          user: null,
          token: null,
          error: null,
        });
      },

      refreshToken: async () => {
        try {
          const refreshToken = localStorage.getItem("refresh_token");
          if (!refreshToken) {
            throw new Error("No refresh token available");
          }

          const response = await api.post("/auth/refresh", {
            refresh_token: refreshToken,
          });

          const { access_token } = response.data;
          setToken(access_token);

          set({ token: access_token });
        } catch (error) {
          get().logout();
          throw error;
        }
      },

      setUser: (user: User | null) => {
        set({ user });
      },

      clearError: () => {
        set({ error: null });
      },

      initializeAuth: () => {
        try {
          const userFromToken = getUserFromToken();
          if (userFromToken) {
            set({
              user: {
                id: userFromToken.sub,
                email: userFromToken.email,
                name: userFromToken.name || userFromToken.email,
              },
            });
          }
        } catch (error) {
          // Token invalid or expired
          clearAuth();
          set({ user: null, token: null });
        }
      },
    }),
    {
      name: "auth-storage",
      partialize: (state) => ({
        user: state.user,
      }),
    }
  )
);
