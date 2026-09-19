import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { ACCESS_TOKEN_KEY, createMemoryStore } from "../../auth/token";
import { AppRoutes } from "../../routes";
import { jsonResponse, studentMe } from "../../test/fixtures";
import { renderApp } from "../../test/render";
import { analysisFixture, emptyChatHistory } from "../../test/studentFixtures";

describe("AI Advisor page", () => {
  it("keeps facts and advice separate and shows the fallback banner", async () => {
    const user = userEvent.setup();
    const fetchImpl = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith("/auth/me")) {
        return jsonResponse(200, studentMe());
      }
      if (url.endsWith("/ai/chat/history") && init?.method !== "DELETE") {
        return jsonResponse(200, emptyChatHistory());
      }
      if (url.endsWith("/ai/analysis")) {
        return jsonResponse(200, analysisFixture("FALLBACK"));
      }
      return jsonResponse(404, { error: { code: "NOT_FOUND", message: "Not found", details: null } });
    });

    renderApp(<AppRoutes />, {
      route: "/student/advisor",
      store: createMemoryStore({ [ACCESS_TOKEN_KEY]: "test-token" }),
      fetchImpl,
    });

    expect(await screen.findByRole("heading", { name: "AI Advisor" })).toBeInTheDocument();
    expect(await screen.findByText("No chat messages")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: /get analysis/i }));

    expect(await screen.findByRole("heading", { name: "Facts" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "AI advice" })).toBeInTheDocument();
    expect(screen.getByLabelText("Fallback banner")).toBeInTheDocument();
    expect(screen.getByText(/NOT_CONFIGURED/)).toBeInTheDocument();
    expect(screen.getByText(/Focus on attendance/)).toBeInTheDocument();
    expect(screen.getByText(/"risk_score": 82/)).toBeInTheDocument();
  });
});
