import { render, screen } from "@testing-library/react";

import { ApiError } from "../lib/errors";
import { ErrorMessage } from "./ErrorMessage";

describe("ErrorMessage", () => {
  it("shows the API error message", () => {
    render(<ErrorMessage error={new ApiError(401, "UNAUTHENTICATED", "Invalid email or password")} />);
    expect(screen.getByRole("alert")).toHaveTextContent("Invalid email or password");
  });
});
