import { render, type RenderOptions } from "@testing-library/react";
import type { ReactElement, ReactNode } from "react";
import { MemoryRouter } from "react-router-dom";

import { AuthProvider } from "../auth/AuthContext";
import { createMemoryStore, type TokenStore } from "../auth/token";

type Options = Omit<RenderOptions, "wrapper"> & {
  route?: string;
  store?: TokenStore;
  fetchImpl?: typeof fetch;
};

export function renderApp(ui: ReactElement, options: Options = {}) {
  const { route = "/", store = createMemoryStore(), fetchImpl, ...rest } = options;

  function Wrapper({ children }: { children: ReactNode }) {
    return (
      <MemoryRouter
        initialEntries={[route]}
        future={{ v7_startTransition: true, v7_relativeSplatPath: true }}
      >
        <AuthProvider store={store} fetchImpl={fetchImpl}>
          {children}
        </AuthProvider>
      </MemoryRouter>
    );
  }

  return { store, ...render(ui, { wrapper: Wrapper, ...rest }) };
}
