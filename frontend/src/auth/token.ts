export const ACCESS_TOKEN_KEY = "saa_access_token";

export type TokenStore = {
  getItem: (key: string) => string | null;
  setItem: (key: string, value: string) => void;
  removeItem: (key: string) => void;
};

export function getAccessToken(store: TokenStore = localStorage): string | null {
  return store.getItem(ACCESS_TOKEN_KEY);
}

export function setAccessToken(token: string, store: TokenStore = localStorage): void {
  store.setItem(ACCESS_TOKEN_KEY, token);
}

export function clearAccessToken(store: TokenStore = localStorage): void {
  store.removeItem(ACCESS_TOKEN_KEY);
}

export function createMemoryStore(initial: Record<string, string> = {}): TokenStore {
  const data = { ...initial };
  return {
    getItem: (key) => (key in data ? data[key] : null),
    setItem: (key, value) => {
      data[key] = value;
    },
    removeItem: (key) => {
      delete data[key];
    },
  };
}
