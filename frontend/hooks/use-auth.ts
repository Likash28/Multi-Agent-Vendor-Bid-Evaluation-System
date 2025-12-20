import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useAuthStore, type RegisterData } from "@/stores/auth-store";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export function useAuth() {
  const router = useRouter();
  const queryClient = useQueryClient();

  const {
    user,
    token,
    isLoading: storeLoading,
    error,
    login: storeLogin,
    register: storeRegister,
    logout: storeLogout,
    clearError,
    initializeAuth,
  } = useAuthStore();

  // Initialize auth on mount
  useEffect(() => {
    initializeAuth();
  }, [initializeAuth]);

  const loginMutation = useMutation({
    mutationFn: async ({
      email,
      password,
    }: {
      email: string;
      password: string;
    }) => {
      await storeLogin(email, password);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["user"] });
      router.push("/dashboard");
    },
  });

  const registerMutation = useMutation({
    mutationFn: async (data: RegisterData) => {
      await storeRegister(data);
    },
    onSuccess: () => {
      router.push("/login");
    },
  });

  const logout = () => {
    storeLogout();
    queryClient.clear();
    router.push("/login");
  };

  return {
    user,
    token,
    isLoading: storeLoading || loginMutation.isPending || registerMutation.isPending,
    error: error || loginMutation.error || registerMutation.error,
    login: loginMutation.mutate,
    register: registerMutation.mutate,
    logout,
    clearError,
    isAuthenticated: !!user && !!token,
  };
}

export function useRequireAuth() {
  const { user, isAuthenticated } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login");
    }
  }, [isAuthenticated, router]);

  return { user, isAuthenticated };
}
