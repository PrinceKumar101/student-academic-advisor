import { useState } from "react";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { Button } from "./Button";
import { Modal } from "./Modal";

function Harness() {
  const [open, setOpen] = useState(false);
  return (
    <>
      <Button onClick={() => setOpen(true)}>About risk</Button>
      <Modal open={open} title="About risk" onClose={() => setOpen(false)}>
        <p>Risk is an indicator, not a prediction of failure.</p>
      </Modal>
    </>
  );
}

describe("Modal", () => {
  it("opens a labelled dialog and closes on Escape", async () => {
    const user = userEvent.setup();
    render(<Harness />);
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "About risk" }));
    expect(screen.getByRole("dialog", { name: "About risk" })).toBeInTheDocument();
    await user.keyboard("{Escape}");
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });
});
