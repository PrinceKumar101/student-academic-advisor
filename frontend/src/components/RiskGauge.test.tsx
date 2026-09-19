import { render, screen } from "@testing-library/react";

import { RiskGauge } from "./RiskGauge";

describe("RiskGauge", () => {
  it("prints the backend score and level with a labelled bar", () => {
    render(<RiskGauge score={82} level="HIGH" />);
    expect(screen.getByText("Risk score 82")).toBeInTheDocument();
    expect(screen.getByLabelText("Risk level HIGH")).toBeInTheDocument();
    expect(screen.getByRole("img", { name: "Risk score 82, level HIGH" })).toBeInTheDocument();
  });
});
