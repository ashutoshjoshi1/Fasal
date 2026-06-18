import { describe, expect, it } from "vitest";

import { ACTION_META, RISK_META, fmtCoord, fmtPct, fmtScore } from "./risk";

describe("formatters", () => {
  it("fmtPct scales to percent and rounds to the requested digits", () => {
    expect(fmtPct(0.1234)).toBe("12%");
    expect(fmtPct(0.1234, 1)).toBe("12.3%");
  });

  it("fmtScore fixes two decimals", () => {
    expect(fmtScore(0.5)).toBe("0.50");
  });

  it("fmtCoord uses N/S and E/W hemisphere suffixes", () => {
    expect(fmtCoord(-12.5, 77.25)).toBe("12.50°S 77.25°E");
    expect(fmtCoord(28.6, -81.2)).toBe("28.60°N 81.20°W");
  });
});

describe("presentation metadata", () => {
  it("defines exactly the three risk classes", () => {
    expect(Object.keys(RISK_META).sort()).toEqual(["high", "low", "medium"]);
  });

  it("gives every action a short label", () => {
    expect(ACTION_META.send_to_lab.short).toBe("Send to lab");
    for (const meta of Object.values(ACTION_META)) {
      expect(meta.short.length).toBeGreaterThan(0);
    }
  });
});
