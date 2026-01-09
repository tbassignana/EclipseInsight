"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { authApi } from "@/lib/api";
import type { User } from "@/types";

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  // Load token from localStorage on mount
  useEffect(() => {
    const storedToken = localStorage.getItem("access_token");
    if (storedToken) {
      setToken(storedToken);
      fetchUser(storedToken);
    } else {
      setIsLoading(false);
    }
  }, []);

  const fetchUser = async (authToken: string) => {
    try {
      const userData = await authApi.me(authToken);
      setUser({
        id: userData.id,
        email: userData.email,
        is_active: true,
        is_admin: userData.is_admin,
        created_at: new Date().toISOString(),
      });
    } catch {
      localStorage.removeItem("access_token");
      setToken(null);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  const login = useCallback(async (email: string, password: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await authApi.login(email, password);
      localStorage.setItem("access_token", response.access_token);
      setToken(response.access_token);
      await fetchUser(response.access_token);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [router]);

  const register = useCallback(async (email: string, password: string) => {
    setIsLoading(true);
    setError(null);
    try {
      await authApi.register(email, password);
      // Auto-login after registration
      await login(email, password);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [login]);

  const logout = useCallback(() => {
    localStorage.removeItem("access_token");
    setToken(null);
    setUser(null);
    router.push("/");
  }, [router]);

  return {
    user,
    token,
    isLoading,
    error,
    isAuthenticated: !!user,
    login,
    register,
    logout,
  };
}
