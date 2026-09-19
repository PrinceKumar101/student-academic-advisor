import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { ACCESS_TOKEN_KEY, createMemoryStore } from "../../auth/token";
import { AppRoutes } from "../../routes";
import { jsonResponse, teacherMe } from "../../test/fixtures";
import { renderApp } from "../../test/render";
import { studentPageFixture, taughtSubjectsFixture } from "../../test/teacherFixtures";

function teacherListFetch(page = studentPageFixture()) {
  return vi.fn(async (input: RequestInfo | URL) => {
    const url = String(input);
    if (url.endsWith("/auth/me")) {
      return jsonResponse(200, teacherMe());
    }
    if (url.includes("/subjects?")) {
      return jsonResponse(200, taughtSubjectsFixture());
    }
    if (url.includes("/teacher/students")) {
      return jsonResponse(200, page);
    }
    return jsonResponse(404, { error: { code: "NOT_FOUND", message: "Not found", details: null } });
  });
}

describe("Teacher students page", () => {
  it("sends applied filter combinations as query params and sorts by risk", async () => {
    const user = userEvent.setup();
    const fetchImpl = teacherListFetch();
    renderApp(<AppRoutes />, {
      route: "/teacher/students",
      store: createMemoryStore({ [ACCESS_TOKEN_KEY]: "test-token" }),
      fetchImpl,
    });

    expect(await screen.findByRole("heading", { name: "Students" })).toBeInTheDocument();
    expect(await screen.findByText("Rahul Venn")).toBeInTheDocument();
    const names = screen.getAllByRole("link", { name: /Rahul Venn|Low Risk/ });
    expect(names[0]).toHaveTextContent("Rahul Venn");

    await user.selectOptions(screen.getByRole("combobox", { name: "Risk level" }), "HIGH");
    await user.type(screen.getByRole("textbox", { name: "Department" }), "CSE");
    await user.type(screen.getByRole("textbox", { name: "Semester" }), "5");
    await user.type(screen.getByRole("textbox", { name: "Section" }), "B");
    await user.selectOptions(screen.getByRole("combobox", { name: "Subject" }), "1");
    await user.type(screen.getByRole("textbox", { name: "Search" }), "rahul");
    await user.click(screen.getByRole("button", { name: /apply filters/i }));

    const listCalls = fetchImpl.mock.calls
      .map(([request]) => String(request))
      .filter((url) => url.includes("/teacher/students"));
    const last = listCalls[listCalls.length - 1];
    const query = new URL(last, "http://localhost").searchParams;
    expect(query.get("risk_level")).toBe("HIGH");
    expect(query.get("department")).toBe("CSE");
    expect(query.get("semester")).toBe("5");
    expect(query.get("section")).toBe("B");
    expect(query.get("subject_id")).toBe("1");
    expect(query.get("search")).toBe("rahul");
    expect(query.get("page")).toBe("1");
  });

  it("shows an empty results state", async () => {
    renderApp(<AppRoutes />, {
      route: "/teacher/students",
      store: createMemoryStore({ [ACCESS_TOKEN_KEY]: "test-token" }),
      fetchImpl: teacherListFetch({ items: [], total: 0, page: 1, page_size: 20 }),
    });

    expect(await screen.findByText("No students match these filters")).toBeInTheDocument();
  });
});
