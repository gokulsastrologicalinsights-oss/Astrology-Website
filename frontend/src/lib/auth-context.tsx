"use client";

import React, { createContext, useContext, useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { UserRole } from "./supabase/types";
import { createClient } from "./supabase/client";
import type { Session } from "@supabase/supabase-js";

export interface AuthUser {
  id: string;
  email: string | null;
  username: string;
  displayName: string;
  role: UserRole;
  mustChangePassword: boolean;
  createdAt?: string;
}

interface AuthContextType {
  user: AuthUser | null;
  session: Session | null;
  role: UserRole | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  mustChangePassword: boolean;
  refreshUser: () => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  session: null,
  role: null,
  isAuthenticated: false,
  isLoading: true,
  mustChangePassword: false,
  refreshUser: async () => {},
  logout: async () => {},
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  const refreshUser = useCallback(async () => {
    try {
      const res = await fetch("/api/auth/me", {
        headers: { Accept: "application/json" },
        cache: "no-store",
      });
      if (res.ok) {
        const data = await res.json();
        if (data.authenticated && data.user) {
          setUser(data.user);
        } else {
          setUser(null);
        }
      } else {
        setUser(null);
      }
      try {
        const supabase = createClient();
        const { data: sData } = await supabase.auth.getSession();
        setSession(sData?.session || null);
      } catch {
        // Ignored
      }
    } catch {
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    let isMounted = true;
    const supabase = createClient();

    async function initAuth() {
      try {
        await Promise.allSettled([
          refreshUser(),
          supabase.auth.getSession().then(({ data }) => {
            if (isMounted && data?.session) {
              setSession(data.session);
            }
          }),
        ]);
      } finally {
        if (isMounted) setIsLoading(false);
      }
    }

    initAuth();

    const { data: authListener } = supabase.auth.onAuthStateChange((_event, sess) => {
      if (isMounted) setSession(sess);
    });
    return () => {
      isMounted = false;
      authListener?.subscription?.unsubscribe();
    };
  }, [refreshUser]);

  const logout = async () => {
    try {
      await fetch("/api/auth/logout", { method: "POST" });
      const supabase = createClient();
      await supabase.auth.signOut();
    } catch (err) {
      console.error("Logout request failed:", err);
    } finally {
      setUser(null);
      setSession(null);
      router.push("/login");
      router.refresh();
    }
  };

  const value: AuthContextType = {
    user,
    session,
    role: user?.role || null,
    isAuthenticated: !!user,
    isLoading,
    mustChangePassword: !!user?.mustChangePassword,
    refreshUser,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
