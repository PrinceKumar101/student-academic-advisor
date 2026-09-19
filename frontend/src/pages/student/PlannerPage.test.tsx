import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { ACCESS_TOKEN_KEY, createMemoryStore } from "../../auth/token";
import { AppRoutes } from "../../routes";
import { jsonResponse, studentMe } from "../../test/fixtures";
import { renderApp } from "../../test/render";
import { planDetail, planSummary } from "../../test/studentFixtures";

describe("Study Planner page", () => {
  it("creates a plan and ticks an item via PATCH", async () => {
    const user = userEvent.setup();
    const fetchImpl = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith("/auth/me")) {
        return jsonResponse(200, studentMe());
      }
      if (url.endsWith("/study-plans") && (!init?.method || init.method === "GET")) {
        return jsonResponse(200, []);
      }
      if (url.endsWith("/study-plans") && init?.method === "POST") {
        return jsonResponse(200, planDetail());
      }
      if (url.includes("/study-plans/5/items/1") && init?.method === "PATCH") {
        return jsonResponse(200, {
          ...planDetail().items[0],
          is_completed: true,
          completed_at: "2026-09-19T12:00:00Z",
        });
      }
      if (url.endsWith("/study-plans/5")) {
        return jsonResponse(200, planDetail());
      }
      return jsonResponse(404, { error: { code: "NOT_FOUND", message: "Not found", details: null } });
    });

    renderApp(<AppRoutes />, {
      route: "/student/planner",
      store: createMemoryStore({ [ACCESS_TOKEN_KEY]: "test-token" }),
      fetchImpl,
    });

    expect(await screen.findByRole("heading", { name: "Study Planner" })).toBeInTheDocument();
    expect(await screen.findByText("No study plans")).toBeInTheDocument();

    await user.type(screen.getByLabelText(/exam date/i), "2026-10-15");
    await user.clear(screen.getByLabelText(/available hours per day/i));
    await user.type(screen.getByLabelText(/available hours per day/i), "3");
    await user.click(screen.getByRole("button", { name: /generate plan/i }));

    expect(await screen.findByText(/Trees/)).toBeInTheDocument();
    expect(
      screen.getByText(/Fallback: this response was generated without the AI/),
    ).toBeInTheDocument();

    const createCall = fetchImpl.mock.calls.find(
      ([request, init]) => String(request).endsWith("/study-plans") && init?.method === "POST",
    );
    expect(JSON.parse(String((createCall?.[1] as RequestInit).body))).toEqual({
      exam_date: "2026-10-15",
      available_hours_per_day: 3,
    });

    await user.click(screen.getByRole("checkbox"));
    const patchCall = fetchImpl.mock.calls.find(
      ([request, init]) => String(request).includes("/items/1") && init?.method === "PATCH",
    );
    expect(patchCall).toBeDefined();
    expect(JSON.parse(String((patchCall?.[1] as RequestInit).body))).toEqual({
      is_completed: true,
    });
  });

  it("lists saved plans", async () => {
    const fetchImpl = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith("/auth/me")) {
        return jsonResponse(200, studentMe());
      }
      if (url.endsWith("/study-plans")) {
        return jsonResponse(200, [planSummary()]);
      }
      return jsonResponse(404, { error: { code: "NOT_FOUND", message: "Not found", details: null } });
    });

    renderApp(<AppRoutes />, {
      route: "/student/planner",
      store: createMemoryStore({ [ACCESS_TOKEN_KEY]: "test-token" }),
      fetchImpl,
    });

    expect(await screen.findByRole("button", { name: /plan 5/i })).toBeInTheDocument();
  });
});
