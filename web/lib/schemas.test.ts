import { describe, expect, it } from "vitest";

import { FieldSummarySchema, RiskPredictionSchema } from "./schemas";

const validField = {
  id: "f1",
  name: "North block",
  crop: "wheat",
  location: { lat: 1, lon: 2 },
  area_ha: 10,
  risk_class: "low",
  risk_score: 0.1,
  confidence: "high",
  coverage: 0.9,
  last_flight: "2026-01-01",
};

describe("FieldSummarySchema", () => {
  it("parses a valid payload", () => {
    expect(FieldSummarySchema.parse(validField).id).toBe("f1");
  });

  it("strips unknown keys (forward-compatible with new backend fields)", () => {
    const parsed = FieldSummarySchema.parse({ ...validField, extra: "ignored" });
    expect("extra" in parsed).toBe(false);
  });

  it("rejects an out-of-domain risk_class", () => {
    expect(() => FieldSummarySchema.parse({ ...validField, risk_class: "extreme" })).toThrow();
  });

  it("rejects a non-numeric risk_score", () => {
    expect(() => FieldSummarySchema.parse({ ...validField, risk_score: "high" })).toThrow();
  });
});

describe("RiskPredictionSchema", () => {
  it("accepts null provenance but requires the key to be present", () => {
    const pred = {
      zone_id: "z1",
      risk_class: "high",
      risk_score: 0.82,
      confidence: "ood",
      action: "send_to_lab",
      reason_codes: [],
      provenance: null,
    };
    expect(RiskPredictionSchema.parse(pred).provenance).toBeNull();
    const { provenance: _omit, ...withoutProvenance } = pred;
    expect(() => RiskPredictionSchema.parse(withoutProvenance)).toThrow();
  });
});
