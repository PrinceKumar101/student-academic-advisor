import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { ACCESS_TOKEN_KEY, createMemoryStore } from "../auth/token";
import { AppRoutes } from "../routes";
import { jsonResponse, studentMe } from "../test/fixtures";
import { renderApp } from "../test/render";
import { overviewFixture } from "../test/studentFixtures";

describe("Layout polish", () => {
  it("exposes a skip link, main landmark, and mobile menu", async () => {
    const user = userEvent.setup();
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

    expect(await screen.findByRole("link", { name: "Skip to main content" })).toHaveAttribute(
      "href",
      "#main-content",
    );
    expect(document.getElementById("main-content")).toBeTruthy();
    expect(screen.getByRole("heading", { name: "Student dashboard" })).toBeInTheDocument();
    expect(screen.getByText("Risk indicator, not a prediction.")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Open menu" }));
    expect(screen.getByRole("navigation", { name: "Main" })).toBeVisible();
    await user.keyboard("{Escape}");
    expect(screen.getByRole("button", { name: "Open menu" })).toHaveAttribute("aria-expanded", "false");
  });
});
