import { render, screen } from "@testing-library/react";

import { Loading } from "./Loading";

describe("Loading", () => {
  it("announces a polite status with a visible label", () => {
    render(<Loading label="Loading overview…" rows={2} />);
    expect(screen.getByRole("status")).toHaveTextContent("Loading overview…");
  });
});
