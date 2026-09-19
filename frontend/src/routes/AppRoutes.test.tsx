import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { ACCESS_TOKEN_KEY, createMemoryStore, getAccessToken } from "../auth/token";
import { AppRoutes } from "./index";
import { jsonResponse, studentMe, teacherMe, tokenResponse } from "../test/fixtures";
import { renderApp } from "../test/render";

function authFetch(me = studentMe()) {
  return vi.fn(async (input: RequestInfo | URL) => {
    const url = String(input);
    if (url.endsWith("/auth/login")) {
      return jsonResponse(200, tokenResponse(me));
    }
    if (url.endsWith("/auth/me")) {
      return jsonResponse(200, me);
    }
    if (url.endsWith("/auth/logout")) {
      return new Response(null, { status: 204 });
    }
    return jsonResponse(404, { error: { code: "NOT_FOUND", message: "Not found", details: null } });
  });
}

describe("auth routes", () => {
  it("stores the token on login and lands on the student home", async () => {
    const user = userEvent.setup();
    const store = createMemoryStore();
    renderApp(<AppRoutes />, { route: "/login", store, fetchImpl: authFetch() });

    await user.type(screen.getByLabelText(/email/i), "rahul@demo.edu");
    await user.type(screen.getByLabelText(/password/i), "Demo@1234");
    await user.click(screen.getByRole("button", { name: /sign in/i }));

    expect(getAccessToken(store)).toBe("test-token");
    expect(await screen.findByRole("heading", { name: "Student dashboard" })).toBeInTheDocument();
  });

  it("clears the token on logout", async () => {
    const user = userEvent.setup();
    const store = createMemoryStore({ [ACCESS_TOKEN_KEY]: "test-token" });
    renderApp(<AppRoutes />, { route: "/student", store, fetchImpl: authFetch() });

    expect(await screen.findByRole("heading", { name: "Student dashboard" })).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: /log out/i }));
    expect(getAccessToken(store)).toBeNull();
    expect(await screen.findByRole("heading", { name: "Log in" })).toBeInTheDocument();
  });

  it("redirects to login when a stored token is rejected with 401", async () => {
    const store = createMemoryStore({ [ACCESS_TOKEN_KEY]: "expired" });
    const fetchImpl = vi.fn(async () =>
      jsonResponse(401, {
        error: { code: "UNAUTHENTICATED", message: "Unauthenticated", details: null },
      }),
    );
    renderApp(<AppRoutes />, { route: "/student", store, fetchImpl });

    expect(await screen.findByRole("heading", { name: "Log in" })).toBeInTheDocument();
    expect(getAccessToken(store)).toBeNull();
  });

  it("does not let a student open a teacher route", async () => {
    const store = createMemoryStore({ [ACCESS_TOKEN_KEY]: "test-token" });
    renderApp(<AppRoutes />, { route: "/teacher", store, fetchImpl: authFetch(studentMe()) });

    expect(await screen.findByRole("heading", { name: "Forbidden" })).toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: "Teacher dashboard" })).not.toBeInTheDocument();
  });

  it("opens the teacher home for a teacher", async () => {
    const store = createMemoryStore({ [ACCESS_TOKEN_KEY]: "test-token" });
    renderApp(<AppRoutes />, { route: "/teacher", store, fetchImpl: authFetch(teacherMe()) });

    expect(await screen.findByRole("heading", { name: "Teacher dashboard" })).toBeInTheDocument();
  });
});
