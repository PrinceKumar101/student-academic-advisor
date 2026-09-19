import { render, screen } from "@testing-library/react";

import { SimpleTable } from "./SimpleTable";

describe("SimpleTable", () => {
  it("scrolls wide tables inside a captioned container", () => {
    const { container } = render(
      <SimpleTable
        caption="Risk components"
        columns={["Key", "Note"]}
        rows={[["attendance", "long note"]]}
      />,
    );
    expect(screen.getByText("Risk components")).toBeInTheDocument();
    expect(container.firstElementChild).toHaveClass("overflow-x-auto");
    expect(screen.getByRole("columnheader", { name: "Key" })).toBeInTheDocument();
  });

  it("uses EmptyState when there are no rows", () => {
    render(<SimpleTable caption="Empty" columns={["A"]} rows={[]} empty="No flags" />);
    expect(screen.getByRole("status")).toHaveTextContent("No flags");
    expect(screen.queryByRole("table")).not.toBeInTheDocument();
  });
});
