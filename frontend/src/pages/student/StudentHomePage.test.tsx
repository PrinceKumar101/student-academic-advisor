import { screen } from "@testing-library/react";

import { ACCESS_TOKEN_KEY, createMemoryStore } from "../../auth/token";
import { AppRoutes } from "../../routes";
import { jsonResponse, studentMe } from "../../test/fixtures";
import { renderApp } from "../../test/render";
import { overviewFixture } from "../../test/studentFixtures";

describe("Student dashboard", () => {
  it("renders overview risk, warnings, and empty interventions", async () => {
    const fetchImpl = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith("/auth/me")) {
        return jsonResponse(200, studentMe());
      }
      if (url.endsWith("/students/me/overview")) {
        return jsonResponse(200, overviewFixture());
      }
      return jsonResponse(404, { error: { code: "NOT_FOUND", message: "Not found", details: null } });
    });

    renderApp(<AppRoutes />, {
      route: "/student",
      store: createMemoryStore({ [ACCESS_TOKEN_KEY]: "test-token" }),
      fetchImpl,
    });

    expect(await screen.findByText("ATTENDANCE_DROP")).toBeInTheDocument();
    expect(screen.getByText("CS2025001", { exact: false })).toBeInTheDocument();
    expect(screen.getByText(/Risk score 82/)).toBeInTheDocument();
    expect(screen.getByLabelText("Risk level HIGH")).toBeInTheDocument();
    expect(screen.getByText("No open interventions")).toBeInTheDocument();
  });

  it("shows an error state", async () => {
    const fetchImpl = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith("/auth/me")) {
        return jsonResponse(200, studentMe());
      }
      return jsonResponse(500, {
        error: { code: "INTERNAL_ERROR", message: "Overview failed", details: null },
      });
    });

    renderApp(<AppRoutes />, {
      route: "/student",
      store: createMemoryStore({ [ACCESS_TOKEN_KEY]: "test-token" }),
      fetchImpl,
    });

    expect(await screen.findByRole("alert")).toHaveTextContent("Overview failed");
  });
});
