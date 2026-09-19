import { render, screen } from "@testing-library/react";

import { Button } from "./Button";

describe("Button", () => {
  it("renders the accessible name and can be disabled", () => {
    render(
      <Button disabled variant="secondary">
        Apply filters
      </Button>,
    );
    expect(screen.getByRole("button", { name: "Apply filters" })).toBeDisabled();
  });
});
