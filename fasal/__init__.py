"""FASAL — drone hyperspectral + AI pesticide-residue risk screening (backend).

FASAL produces a geospatial low/medium/high pesticide-**risk** map (screening, not
certification). See ``docs/`` for design and ``docs/science.md`` for the scientific basis.

Package layout
--------------
- ``fasal.shared``    : contracts — the 8 data objects + the risk output contract
- ``fasal.pipeline``  : spectroscopy science — calibration → reflectance → preprocess → QC → segment
- ``fasal.features``  : feature extraction (vegetation/red-edge/water indices, derivatives)
- ``fasal.models``    : ML core — baselines, uncertainty, score calibration, explainability
- ``fasal.models.deep``: PyTorch 1D-CNN + spectral/spatial/metadata fusion (optional extra)
- ``fasal.synth``     : synthetic data generation (run/test without real captures)
- ``fasal.hardware``  : sensor/drone integration interfaces + a simulated driver
- ``fasal.services``  : light orchestration (screening service)
- ``fasal.db`` / ``fasal.storage`` / ``fasal.api`` : intentionally light this phase
"""

__version__ = "0.1.0"
