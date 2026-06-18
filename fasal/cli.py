"""FASAL backend CLI. ``fasal version`` and ``fasal demo`` (end-to-end synthetic screening)."""

from __future__ import annotations

import argparse


def _demo(seed: int) -> None:
    from fasal.models import create
    from fasal.pipeline import PipelineConfig, preprocess_spectra
    from fasal.services import ScreeningConfig, ScreeningService, build_sample_plan
    from fasal.synth import default_wavelengths, make_cube, make_dataset

    config = PipelineConfig()
    wavelengths = default_wavelengths()
    spectra, _, labels, _ = make_dataset(400, wavelengths, seed=0)
    prepared, _ = preprocess_spectra(spectra, wavelengths, config)
    service = ScreeningService(create("rf").fit(prepared, labels), config=ScreeningConfig(pipeline_config=config))

    cube, _ = make_cube(24, 24, wavelengths, seed=seed)
    result = service.screen_cube(cube, zone_id="demo-field")
    pred = result.prediction
    print(f"risk={pred.risk_class.value} score={pred.risk_score:.2f} confidence={pred.confidence.value} action={pred.action.value}")
    print("reasons:", [c.type.value for c in pred.reason_codes])
    plan = build_sample_plan(result, per_class=2)
    print(f"sample points: {len(plan.points)} covering {sorted(c.value for c in plan.covered_classes)}")


def _demo_avantes(seed: int) -> None:
    from fasal.hardware import SimulatedAvantes
    from fasal.models import create
    from fasal.pipeline import PipelineConfig, calibrate_raw, preprocess_spectra
    from fasal.services import ScreeningConfig, ScreeningService, build_sample_plan_from_points

    spec = SimulatedAvantes(n_pixels=512, seed=7)
    samples, labels, white, dark = spec.scan_dataset(400, 50.0, signal_strength=0.04, seed=0)
    point = calibrate_raw(samples, white, dark, spec.wavelength_calibration)
    config = PipelineConfig()
    prepared, _ = preprocess_spectra(point.reflectance, point.wavelengths, config)
    service = ScreeningService(create("rf").fit(prepared, labels), config=ScreeningConfig(pipeline_config=config))

    test, _, white2, dark2 = spec.scan_dataset(40, 50.0, signal_strength=0.04, seed=seed)
    result = service.screen_avantes(test, white2, dark2, spec.wavelength_calibration, zone_id="avantes-field")
    pred = result.field_prediction
    print(f"[avantes] {len(result.per_point)} scans | field risk={pred.risk_class.value} score={pred.risk_score:.2f} confidence={pred.confidence.value} action={pred.action.value}")
    print("reasons:", [c.type.value for c in pred.reason_codes])
    plan = build_sample_plan_from_points(result, per_class=2)
    print(f"sample points: {len(plan.points)}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="fasal", description="FASAL backend CLI")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("version")
    demo = sub.add_parser("demo", help="run an end-to-end synthetic (imaging) screening")
    demo.add_argument("--seed", type=int, default=1)
    demo_av = sub.add_parser("demo-avantes", help="end-to-end Avantes point-spectrometer screening")
    demo_av.add_argument("--seed", type=int, default=1)
    args = parser.parse_args(argv)

    if args.command == "demo":
        _demo(args.seed)
    elif args.command == "demo-avantes":
        _demo_avantes(args.seed)
    else:
        from fasal import __version__

        print(f"FASAL backend {__version__}")


if __name__ == "__main__":
    main()
