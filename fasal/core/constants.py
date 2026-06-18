"""Scientific constants — wavelength regions, diagnostic bands, and pipeline defaults.

All wavelengths are in nanometres (nm). References point to ``docs/science.md``.
"""

from __future__ import annotations

# --- Spectral region edges (nm) --- (science.md §3.3)
VIS_RANGE: tuple[float, float] = (400.0, 700.0)
RED_EDGE_RANGE: tuple[float, float] = (680.0, 750.0)
NIR_RANGE: tuple[float, float] = (750.0, 1000.0)
SWIR_RANGE: tuple[float, float] = (1000.0, 2500.0)
VNIR_RANGE: tuple[float, float] = (400.0, 1000.0)

# --- Diagnostic band centres (nm) --- (science.md §3.3, §4)
CHLOROPHYLL_ABSORPTION: tuple[float, float] = (430.0, 660.0)  # pigment electronic transitions
WATER_ABSORPTION: tuple[float, ...] = (970.0, 1200.0, 1450.0, 1940.0)  # O-H overtones/combinations

# Common index anchor bands (nm)
BAND_BLUE: float = 470.0
BAND_GREEN: float = 550.0
BAND_RED: float = 670.0
BAND_RED_EDGE: float = 705.0
BAND_NIR: float = 800.0
BAND_WATER: float = 970.0

# --- Preprocessing defaults --- (science.md §8.1)
SG_WINDOW: int = 11  # Savitzky-Golay window length (must be odd)
SG_POLYORDER: int = 2  # Savitzky-Golay polynomial order
DERIVATIVE_DEFAULT: int = 1

# --- Risk class thresholds (calibrated score -> class) --- (output contract, science.md §5)
RISK_LOW_MAX: float = 0.34  # score <= -> low
RISK_MEDIUM_MAX: float = 0.66  # score <= -> medium ; otherwise high

# --- Confidence / out-of-distribution thresholds --- (science.md §10, docs/04 §5)
CONFIDENCE_UNCERTAIN_BAND: tuple[float, float] = (0.40, 0.60)  # near decision boundary -> uncertain
OOD_TRAIN_QUANTILE: float = 0.99  # feature-distance above this training quantile -> OOD

# --- Avantes (AvaSpec) point spectrometer defaults --- (placeholders; supply your device's values)
# Raw output is counts vs detector pixel; pixel→wavelength uses the device calibration polynomial.
AVANTES_PIXELS: int = 2048
AVANTES_WAVELENGTH_RANGE: tuple[float, float] = (200.0, 1100.0)  # VNIR
DEFAULT_INTEGRATION_TIME_MS: float = 50.0
DEFAULT_FOV_DEG: float = 25.0  # circular fiber FOV; footprint = 2*d*tan(FOV/2)
