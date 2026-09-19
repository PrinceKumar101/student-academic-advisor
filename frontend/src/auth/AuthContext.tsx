import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { useSearchParams } from "react-router-dom";

import { createApiClient, type ApiClient } from "../api/client";
import { loginRequest, logoutRequest, meRequest, registerRequest } from "../api/auth";
import type { MeResponse, RegisterRequest } from "../api/auth";
import { clearAccessToken, getAccessToken, setAccessToken, type TokenStore } from "./token";

export type AuthUser = MeResponse;

type AuthContextValue = {
  user: AuthUser | null;
  token: string | null;
  ready: boolean;
  client: ApiClient;
  login: (email: string, password: string) => Promise<AuthUser>;
  register: (payload: RegisterRequest) => Promise<void>;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

type AuthProviderProps = {
  children: ReactNode;
  store?: TokenStore;
  fetchImpl?: typeof fetch;
  baseUrl?: string;
};

export function AuthProvider({
  children,
  store = localStorage,
  fetchImpl,
  baseUrl = import.meta.env.VITE_API_BASE_URL ?? "",
}: AuthProviderProps) {
  const [searchParams] = useSearchParams();
  const asOf = searchParams.get("as_of");
  const [token, setToken] = useState<string | null>(() => getAccessToken(store));
  const [user, setUser] = useState<AuthUser | null>(null);
  const [ready, setReady] = useState(false);

  const handleUnauthorized = useCallback(() => {
    clearAccessToken(store);
    setToken(null);
    setUser(null);
  }, [store]);

  const client = useMemo(
    () =>
      createApiClient({
        baseUrl,
        fetchImpl,
        getToken: () => getAccessToken(store),
        getAsOf: () => asOf,
        onUnauthorized: handleUnauthorized,
      }),
    [asOf, baseUrl, fetchImpl, handleUnauthorized, store],
  );

  useEffect(() => {
    let cancelled = false;
    const existing = getAccessToken(store);
    if (!existing) {
      setReady(true);
      return;
    }
    meRequest(client)
      .then((me) => {
        if (!cancelled) {
          setUser(me);
          setToken(existing);
        }
      })
      .catch(() => {
        if (!cancelled) {
          handleUnauthorized();
        }
      })
      .finally(() => {
        if (!cancelled) {
          setReady(true);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [client, handleUnauthorized, store]);

  const login = useCallback(
    async (email: string, password: string) => {
      const result = await loginRequest(client, email, password);
      setAccessToken(result.access_token, store);
      const me = await meRequest(client);
      setToken(result.access_token);
      setUser(me);
      return me;
    },
    [client, store],
  );

  const register = useCallback(
    async (payload: RegisterRequest) => {
      await registerRequest(client, payload);
    },
    [client],
  );

  const logout = useCallback(async () => {
    try {
      if (getAccessToken(store)) {
        await logoutRequest(client);
      }
    } catch {
      // Client-side logout still clears the stored token.
    } finally {
      handleUnauthorized();
    }
  }, [client, handleUnauthorized, store]);

  const value = useMemo(
    () => ({ user, token, ready, client, login, register, logout }),
    [user, token, ready, client, login, register, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const value = useContext(AuthContext);
  if (!value) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return value;
}
