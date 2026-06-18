import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { RiskBadge } from "./RiskBadge";

describe("RiskBadge", () => {
  it("renders the human-readable risk label", () => {
    render(<RiskBadge riskClass="high" />);
    expect(screen.getByText("High risk")).toBeInTheDocument();
  });

  it("renders the formatted score when provided", () => {
    render(<RiskBadge riskClass="low" score={0.42} />);
    expect(screen.getByText(/0\.42/)).toBeInTheDocument();
  });

  it("omits the score segment when none is given", () => {
    render(<RiskBadge riskClass="medium" />);
    expect(screen.queryByText(/·/)).not.toBeInTheDocument();
  });
});
