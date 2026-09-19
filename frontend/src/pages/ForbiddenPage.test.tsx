import { screen } from "@testing-library/react";

import { ACCESS_TOKEN_KEY, createMemoryStore } from "../auth/token";
import { jsonResponse, studentMe } from "../test/fixtures";
import { renderApp } from "../test/render";
import { ForbiddenPage } from "./ForbiddenPage";

describe("ForbiddenPage", () => {
  it("links a student back to their dashboard", async () => {
    const fetchImpl = vi.fn(async () => jsonResponse(200, studentMe()));
    renderApp(<ForbiddenPage />, {
      store: createMemoryStore({ [ACCESS_TOKEN_KEY]: "test-token" }),
      fetchImpl,
    });

    expect(await screen.findByRole("link", { name: "Go to your dashboard" })).toHaveAttribute(
      "href",
      "/student",
    );
    expect(screen.getByRole("button", { name: "Log out" })).toBeInTheDocument();
  });
});
