import { screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { ACCESS_TOKEN_KEY, createMemoryStore } from "../auth/token";
import { LandingPage } from "./LandingPage";
import { jsonResponse, studentMe, teacherMe } from "../test/fixtures";
import { renderApp } from "../test/render";

function signedInAs(me: ReturnType<typeof studentMe>) {
  return {
    store: createMemoryStore({ [ACCESS_TOKEN_KEY]: "test-token" }),
    fetchImpl: vi.fn(async () => jsonResponse(200, me)),
  };
}

describe("LandingPage", () => {
  it("renders a single h1 with the hero headline", () => {
    renderApp(<LandingPage />);

    const headings = screen.getAllByRole("heading", { level: 1 });
    expect(headings).toHaveLength(1);
    expect(headings[0]).toHaveTextContent(/slipping/i);
  });

  it("makes no API requests", () => {
    const fetchImpl = vi.fn();
    renderApp(<LandingPage />, { fetchImpl });

    expect(fetchImpl).not.toHaveBeenCalled();
  });

  it("points the calls to action at register and login", () => {
    renderApp(<LandingPage />);

    expect(screen.getAllByRole("link", { name: "Get started" })[0]).toHaveAttribute(
      "href",
      "/register",
    );
    expect(screen.getAllByRole("link", { name: "Log in" })[0]).toHaveAttribute("href", "/login");
  });

  it("scopes the landing typography with saa-landing so dashboards are unaffected", () => {
    const { container } = renderApp(<LandingPage />);

    expect(container.querySelector(".saa-landing")).not.toBeNull();
  });

  it("renders the landing sections that the navigation anchors to", () => {
    const { container } = renderApp(<LandingPage />);

    expect(container.querySelector("#product")).not.toBeNull();
    expect(container.querySelector("#how-it-works")).not.toBeNull();
    expect(container.querySelector("#explainability")).not.toBeNull();
  });
});

/** Both the hero panel and the dashboard preview are figures. */
function heroPanel() {
  return within(screen.getByRole("figure", { name: /not a real student/i }));
}

describe("LandingPage hero panel", () => {
  it("labels the demo panel as example data", () => {
    renderApp(<LandingPage />);

    const panel = heroPanel();
    expect(panel.getByText(/example data/i)).toBeInTheDocument();
    expect(panel.getByText(/not a real student/i)).toBeInTheDocument();
  });

  it("shows the risk score, trend and contributing factors from the static demo data", () => {
    renderApp(<LandingPage />);

    const panel = heroPanel();
    expect(panel.getByRole("img", { name: /risk score 67.1, level HIGH/i })).toBeInTheDocument();
    expect(panel.getByRole("status", { name: /risk level HIGH/i })).toBeInTheDocument();
    expect(panel.getByRole("img", { name: /weekly attendance falling/i })).toBeInTheDocument();
    expect(panel.getByText("Attendance is 64.0%, below the 75% cutoff.")).toBeInTheDocument();
    expect(panel.getByText(/the AI only wrote this paragraph/i)).toBeInTheDocument();
  });
});

describe("LandingPage product sections", () => {
  it("states product facts rather than customer logos in the trust strip", () => {
    renderApp(<LandingPage />);

    const strip = within(screen.getByRole("region", { name: "Product facts" }));
    expect(strip.getByText("Deterministic score")).toBeInTheDocument();
    expect(strip.getByText("Weighted factors")).toBeInTheDocument();
    expect(strip.getByText("AI calls to score")).toBeInTheDocument();
    expect(strip.getByText("Roles")).toBeInTheDocument();
  });

  it("labels the dashboard preview as example data and reuses the risk gauge", () => {
    renderApp(<LandingPage />);

    const preview = within(screen.getByRole("figure", { name: /student dashboard layout/i }));
    expect(preview.getByText(/not a live account/i)).toBeInTheDocument();
    expect(preview.getByRole("img", { name: /risk score 67.1, level HIGH/i })).toBeInTheDocument();
    expect(preview.getAllByText("DECLINING")).toHaveLength(2);
    expect(preview.getByText("slope -5.7")).toBeInTheDocument();
    expect(
      preview.getByText("Attendance dropped from 72.5% to 59.8% over the last 4 weeks."),
    ).toBeInTheDocument();
  });

  it("calls out the risk gauge, the trend and the contributing factors", () => {
    renderApp(<LandingPage />);

    const product = within(
      screen.getByRole("region", { name: "One page that says what is slipping" }),
    );
    expect(product.getByText(/· Risk gauge$/)).toBeInTheDocument();
    expect(product.getByText(/· Trend$/)).toBeInTheDocument();
    expect(product.getByText(/· Contributing factors$/)).toBeInTheDocument();
  });

  it("lists six capabilities with the real risk weights", () => {
    renderApp(<LandingPage />);

    const features = within(screen.getByRole("region", { name: "What the advisor does" }));
    const titles = features.getAllByRole("heading", { level: 3 }).map((node) => node.textContent);
    expect(titles).toEqual([
      "Risk you can audit",
      "Trend detection",
      "Weak-area analysis",
      "What-if simulation",
      "AI advisor and study planner",
      "Teacher class analytics",
    ]);
    expect(features.getByText("Weights 0.25 · 0.25 · 0.15 · 0.15 · 0.10 · 0.10")).toBeInTheDocument();
  });

  it("explains the three stages in order", () => {
    renderApp(<LandingPage />);

    const how = within(screen.getByRole("region", { name: "Python computes. AI explains." }));
    const titles = how.getAllByRole("heading", { level: 3 }).map((node) => node.textContent);
    expect(titles).toEqual([
      "Academic data is recorded",
      "Python computes the numbers",
      "AI explains and helps plan",
    ]);
    expect(how.getByText(/INSUFFICIENT_DATA instead of a guess/)).toBeInTheDocument();
  });
});

describe("LandingPage explainability, call to action and footer", () => {
  it("shows the six real risk weights and how each component is scaled", () => {
    renderApp(<LandingPage />);

    const explainability = within(
      screen.getByRole("region", { name: "Risk indicator, not a prediction." }),
    );
    const names = [
      "Attendance",
      "Internal marks",
      "Assignments",
      "Quizzes",
      "Previous performance",
      "Study habits",
    ];
    names.forEach((name) => expect(explainability.getByText(name)).toBeInTheDocument());
    expect(explainability.getAllByText("0.25")).toHaveLength(2);
    expect(explainability.getAllByText("0.15")).toHaveLength(2);
    expect(explainability.getAllByText("0.10")).toHaveLength(2);
    expect(explainability.getByText("Sum 1.00")).toBeInTheDocument();
  });

  it("states that the weights are chosen, that thin data is reported and that the AI does not score", () => {
    renderApp(<LandingPage />);

    const explainability = within(
      screen.getByRole("region", { name: "Risk indicator, not a prediction." }),
    );
    expect(explainability.getByText(/not learned from data/i)).toBeInTheDocument();
    expect(explainability.getByText(/only INSUFFICIENT_DATA/)).toBeInTheDocument();
    expect(explainability.getByText(/make no AI call/i)).toBeInTheDocument();
  });

  it("routes the final call to action at register and login", () => {
    renderApp(<LandingPage />);

    const cta = within(
      screen.getByRole("region", { name: "Start with the data you already have" }),
    );
    expect(cta.getByRole("link", { name: "Get started" })).toHaveAttribute("href", "/register");
    expect(cta.getByRole("link", { name: "Log in" })).toHaveAttribute("href", "/login");
  });

  it("links the footer to every landing section and to the account routes", () => {
    renderApp(<LandingPage />);

    const footer = within(screen.getByRole("contentinfo"));
    const nav = within(footer.getByRole("navigation", { name: "Footer" }));
    expect(nav.getByRole("link", { name: "The product" })).toHaveAttribute("href", "#product");
    expect(nav.getByRole("link", { name: "Capabilities" })).toHaveAttribute("href", "#features");
    expect(nav.getByRole("link", { name: "How it works" })).toHaveAttribute("href", "#how-it-works");
    expect(nav.getByRole("link", { name: "Explainability" })).toHaveAttribute(
      "href",
      "#explainability",
    );
    expect(nav.getByRole("link", { name: "Log in" })).toHaveAttribute("href", "/login");
    expect(nav.getByRole("link", { name: "Create an account" })).toHaveAttribute("href", "/register");
  });

  it("carries the synthetic-data and risk disclaimers in the footer", () => {
    renderApp(<LandingPage />);

    const footer = within(screen.getByRole("contentinfo"));
    expect(footer.getByText(/synthetic example data, not a real student record/i)).toBeInTheDocument();
    expect(footer.getByText("Risk indicator, not a prediction.")).toBeInTheDocument();
  });
});

/** jsdom has no IntersectionObserver, so Reveal would otherwise never be pending. */
function stubNeverIntersecting() {
  vi.stubGlobal(
    "IntersectionObserver",
    class {
      observe() {}
      unobserve() {}
      disconnect() {}
    },
  );
}

function stubReducedMotion(reduce: boolean) {
  vi.stubGlobal("matchMedia", (media: string) => ({
    media,
    matches: reduce,
    addEventListener() {},
    removeEventListener() {},
  }));
}

describe("LandingPage motion", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("keeps sections hidden until they scroll into view", () => {
    stubNeverIntersecting();
    stubReducedMotion(false);

    const { container } = renderApp(<LandingPage />);

    expect(container.querySelectorAll(".saa-reveal-pending").length).toBeGreaterThan(0);
  });

  it("holds nothing back when prefers-reduced-motion is set", () => {
    stubNeverIntersecting();
    stubReducedMotion(true);

    const { container } = renderApp(<LandingPage />);

    expect(container.querySelectorAll(".saa-reveal-pending")).toHaveLength(0);
  });

  it("draws the hero panel data with the shared motion primitives", () => {
    const { container } = renderApp(<LandingPage />);

    const panel = container.querySelector(".saa-hero-panel");
    expect(panel).not.toBeNull();
    // One sweeping bar per contributing factor, plus the attendance draw.
    expect(panel?.querySelectorAll(".saa-landing-sweep")).toHaveLength(3);
    expect(panel?.querySelector(".saa-landing-draw")).not.toBeNull();
    // The end-point dot and the AI explanation fade in last.
    expect(panel?.querySelectorAll(".saa-landing-fade")).toHaveLength(2);
  });

  it("runs the ambient loops on the decorative hero backdrop only", () => {
    const { container } = renderApp(<LandingPage />);

    const ambient = container.querySelectorAll(".saa-ambient-grid, .saa-ambient-glow");
    expect(ambient).toHaveLength(2);
    ambient.forEach((node) => {
      expect(node.closest("[aria-hidden='true']")).not.toBeNull();
    });
  });
});

describe("LandingPage navigation", () => {
  it("keeps the mobile menu collapsed until it is opened, and closes it on Escape", async () => {
    const user = userEvent.setup();
    const { container } = renderApp(<LandingPage />);
    const menu = container.querySelector("#landing-menu");

    const toggle = screen.getByRole("button", { name: "Menu" });
    expect(toggle).toHaveAttribute("aria-expanded", "false");
    expect(menu).not.toBeVisible();

    await user.click(toggle);
    expect(screen.getByRole("button", { name: "Close" })).toHaveAttribute("aria-expanded", "true");
    expect(menu).toBeVisible();

    await user.keyboard("{Escape}");
    const reopened = screen.getByRole("button", { name: "Menu" });
    expect(reopened).toHaveAttribute("aria-expanded", "false");
    expect(reopened).toHaveFocus();
    expect(menu).not.toBeVisible();
  });

  it("sends a signed-in student to the student dashboard instead of offering sign-up", async () => {
    renderApp(<LandingPage />, signedInAs(studentMe()));

    const cta = await screen.findAllByRole("link", { name: "Go to your dashboard" });
    expect(cta[0]).toHaveAttribute("href", "/student");
    const nav = within(screen.getByRole("banner"));
    expect(nav.queryByRole("link", { name: "Get started" })).not.toBeInTheDocument();
    expect(nav.queryByRole("link", { name: "Log in" })).not.toBeInTheDocument();
  });

  it("sends a signed-in teacher to the teacher dashboard", async () => {
    renderApp(<LandingPage />, signedInAs(teacherMe()));

    const cta = await screen.findAllByRole("link", { name: "Go to your dashboard" });
    expect(cta[0]).toHaveAttribute("href", "/teacher");
  });
});
