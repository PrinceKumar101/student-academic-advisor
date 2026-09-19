import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { ACCESS_TOKEN_KEY, createMemoryStore } from "../../auth/token";
import { AppRoutes } from "../../routes";
import { jsonResponse, teacherMe } from "../../test/fixtures";
import { renderApp } from "../../test/render";
import {
  subjectAnalysisFixture,
  taughtSubjectsFixture,
  teacherOverviewFixture,
  teacherRiskFixture,
  teacherTrendsFixture,
} from "../../test/teacherFixtures";

function detailFetch(createResponse: Response) {
  return vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input);
    if (url.endsWith("/auth/me")) {
      return jsonResponse(200, teacherMe());
    }
    if (url.includes("/subjects?")) {
      return jsonResponse(200, taughtSubjectsFixture());
    }
    if (url.endsWith("/students/12/overview")) {
      return jsonResponse(200, teacherOverviewFixture());
    }
    if (url.endsWith("/risk/12")) {
      return jsonResponse(200, teacherRiskFixture());
    }
    if (url.endsWith("/trends/12")) {
      return jsonResponse(200, teacherTrendsFixture());
    }
    if (url.endsWith("/analytics/students/12/subjects")) {
      return jsonResponse(200, subjectAnalysisFixture());
    }
    if (url.includes("/interventions") && init?.method === "POST") {
      return createResponse;
    }
    if (url.includes("/interventions")) {
      return jsonResponse(200, []);
    }
    return jsonResponse(404, { error: { code: "NOT_FOUND", message: "Not found", details: null } });
  });
}

describe("Create intervention form", () => {
  it("shows validation errors from the API", async () => {
    const user = userEvent.setup();
    renderApp(<AppRoutes />, {
      route: "/teacher/students/12",
      store: createMemoryStore({ [ACCESS_TOKEN_KEY]: "test-token" }),
      fetchImpl: detailFetch(
        jsonResponse(422, {
          error: { code: "VALIDATION_ERROR", message: "Title is required", details: null },
        }),
      ),
    });

    expect(await screen.findByRole("heading", { name: "Create intervention" })).toBeInTheDocument();
    await user.type(screen.getByRole("textbox", { name: "Title" }), "Meet after class");
    await user.click(screen.getByRole("button", { name: /create intervention/i }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Title is required");
  });

  it("posts the create payload", async () => {
    const user = userEvent.setup();
    const fetchImpl = detailFetch(
      jsonResponse(200, {
        id: 9,
        student_id: 12,
        teacher_id: 1,
        subject_id: null,
        title: "Meet after class",
        description: null,
        priority: "HIGH",
        status: "PENDING",
        due_date: null,
        baseline_score: 82,
        baseline_level: "HIGH",
        baseline_at: "2026-09-19T00:00:00Z",
        outcome_score: null,
        outcome_level: null,
        outcome_at: null,
        completion_note: null,
        created_at: "2026-09-19T00:00:00Z",
        updated_at: "2026-09-19T00:00:00Z",
      }),
    );
    renderApp(<AppRoutes />, {
      route: "/teacher/students/12",
      store: createMemoryStore({ [ACCESS_TOKEN_KEY]: "test-token" }),
      fetchImpl,
    });

    expect(await screen.findByRole("heading", { name: "Create intervention" })).toBeInTheDocument();
    await user.type(screen.getByLabelText(/^title$/i), "Meet after class");
    await user.selectOptions(screen.getByLabelText(/^priority$/i), "HIGH");
    await user.click(screen.getByRole("button", { name: /create intervention/i }));

    const createCall = fetchImpl.mock.calls.find(
      ([request, init]) => String(request).includes("/interventions") && init?.method === "POST",
    );
    expect(createCall).toBeDefined();
    expect(JSON.parse(String((createCall?.[1] as RequestInit).body))).toEqual({
      student_id: 12,
      title: "Meet after class",
      description: null,
      priority: "HIGH",
      due_date: null,
      subject_id: null,
    });
  });
});
