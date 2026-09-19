import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { Tabs } from "./Tabs";

describe("Tabs", () => {
  it("shows the selected panel and hides the others", async () => {
    const user = userEvent.setup();
    render(
      <Tabs
        items={[
          { id: "type", label: "By type", content: <p>Type panel</p> },
          { id: "subject", label: "By subject", content: <p>Subject panel</p> },
        ]}
      />,
    );

    expect(screen.getByRole("tab", { name: "By type" })).toHaveAttribute("aria-selected", "true");
    expect(screen.getByText("Type panel")).toBeVisible();
    expect(screen.getByText("Subject panel")).not.toBeVisible();

    await user.click(screen.getByRole("tab", { name: "By subject" }));
    expect(screen.getByRole("tab", { name: "By subject" })).toHaveAttribute("aria-selected", "true");
    expect(screen.getByText("Subject panel")).toBeVisible();
  });
});
