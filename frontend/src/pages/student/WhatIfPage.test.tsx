import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { ACCESS_TOKEN_KEY, createMemoryStore } from "../../auth/token";
import { AppRoutes } from "../../routes";
import { jsonResponse, studentMe } from "../../test/fixtures";
import { renderApp } from "../../test/render";
import { whatIfFixture } from "../../test/studentFixtures";

function studentFetch() {
  return vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input);
    if (url.endsWith("/auth/me")) {
      return jsonResponse(200, studentMe());
    }
    if (url.includes("/risk/me/what-if") && init?.method === "POST") {
      return jsonResponse(200, whatIfFixture());
    }
    return jsonResponse(404, { error: { code: "NOT_FOUND", message: "Not found", details: null } });
  });
}

describe("What-If page", () => {
  it("sends only filled override fields and shows current vs simulated", async () => {
    const user = userEvent.setup();
    const fetchImpl = studentFetch();
    renderApp(<AppRoutes />, {
      route: "/student/what-if",
      store: createMemoryStore({ [ACCESS_TOKEN_KEY]: "test-token" }),
      fetchImpl,
    });

    expect(await screen.findByRole("heading", { name: "What-If" })).toBeInTheDocument();
    expect(screen.getByText("No simulation yet")).toBeInTheDocument();
    await user.type(screen.getByLabelText(/attendance percent/i), "80");
    await user.click(screen.getByRole("button", { name: /simulate/i }));

    expect(await screen.findByText(/difference/i)).toBeInTheDocument();
    expect(screen.getByText("-10")).toBeInTheDocument();
    expect(screen.getAllByText("MEDIUM").length).toBeGreaterThan(0);

    const whatIfCall = fetchImpl.mock.calls.find(([request]) =>
      String(request).includes("/risk/me/what-if"),
    );
    expect(whatIfCall).toBeDefined();
    const body = JSON.parse(String((whatIfCall?.[1] as RequestInit).body));
    expect(body).toEqual({ overrides: { attendance_percent: 80 } });
  });

  it("shows an API error", async () => {
    const user = userEvent.setup();
    const fetchImpl = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith("/auth/me")) {
        return jsonResponse(200, studentMe());
      }
      if (url.includes("/risk/me/what-if")) {
        return jsonResponse(422, {
          error: { code: "VALIDATION_ERROR", message: "Out of range", details: null },
        });
      }
      return jsonResponse(404, { error: { code: "NOT_FOUND", message: "Not found", details: null } });
    });
    renderApp(<AppRoutes />, {
      route: "/student/what-if",
      store: createMemoryStore({ [ACCESS_TOKEN_KEY]: "test-token" }),
      fetchImpl,
    });

    await screen.findByRole("heading", { name: "What-If" });
    await user.type(screen.getByLabelText(/attendance percent/i), "200");
    await user.click(screen.getByRole("button", { name: /simulate/i }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Out of range");
  });
});
