import { render, screen } from "@testing-library/react";

import { RiskBadge } from "./RiskBadge";

describe("RiskBadge", () => {
  it("always shows the risk level as text, including INSUFFICIENT_DATA", () => {
    const { rerender } = render(<RiskBadge level="HIGH" />);
    expect(screen.getByRole("status")).toHaveTextContent("HIGH");

    rerender(<RiskBadge level="INSUFFICIENT_DATA" />);
    expect(screen.getByRole("status")).toHaveTextContent("INSUFFICIENT_DATA");
    expect(screen.getByLabelText("Risk level INSUFFICIENT_DATA")).toBeInTheDocument();
  });
});
