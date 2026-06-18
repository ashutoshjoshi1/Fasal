"""Numpy-backed hyperspectral cube container.

Shape convention: ``data`` is ``(H, W, B)`` with the band axis last; ``wavelengths`` is
``(B,)`` in nm, strictly increasing. A boolean ``mask`` ``(H, W)`` marks valid pixels
(``True`` = valid). The cube is immutable — mutating helpers return new cubes.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


def nearest_band_index(wavelengths: np.ndarray, target_nm: float) -> int:
    """Index of the band whose wavelength is closest to ``target_nm``."""
    wl = np.asarray(wavelengths, dtype=float)
    return int(np.argmin(np.abs(wl - float(target_nm))))


@dataclass(frozen=True)
class HSICube:
    """An immutable hyperspectral image cube."""

    data: np.ndarray  # (H, W, B)
    wavelengths: np.ndarray  # (B,)
    mask: np.ndarray | None = None  # (H, W) bool, True = valid
    is_reflectance: bool = False
    meta: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        data = np.asarray(self.data, dtype=float)
        wl = np.asarray(self.wavelengths, dtype=float)
        if data.ndim != 3:
            raise ValueError(f"data must be (H, W, B); got shape {data.shape}")
        if data.shape[2] != wl.shape[0]:
            raise ValueError(f"band axis ({data.shape[2]}) != len(wavelengths) ({wl.shape[0]})")
        if wl.ndim != 1 or np.any(np.diff(wl) <= 0):
            raise ValueError("wavelengths must be 1-D and strictly increasing")
        object.__setattr__(self, "data", data)
        object.__setattr__(self, "wavelengths", wl)
        if self.mask is not None:
            m = np.asarray(self.mask, dtype=bool)
            if m.shape != data.shape[:2]:
                raise ValueError("mask shape must equal (H, W)")
            object.__setattr__(self, "mask", m)

    # --- shape helpers ---
    @property
    def height(self) -> int:
        return self.data.shape[0]

    @property
    def width(self) -> int:
        return self.data.shape[1]

    @property
    def n_bands(self) -> int:
        return self.data.shape[2]

    @property
    def n_pixels(self) -> int:
        return self.height * self.width

    # --- band access ---
    def band_index(self, wavelength_nm: float) -> int:
        return nearest_band_index(self.wavelengths, wavelength_nm)

    def band_at(self, wavelength_nm: float) -> np.ndarray:
        """The ``(H, W)`` image at the band nearest ``wavelength_nm``."""
        return self.data[:, :, self.band_index(wavelength_nm)]

    # --- reshaping ---
    def to_2d(self) -> np.ndarray:
        """Flatten to ``(H*W, B)`` spectra."""
        return self.data.reshape(-1, self.n_bands)

    @classmethod
    def from_2d(
        cls,
        spectra: np.ndarray,
        shape_hw: tuple[int, int],
        wavelengths: np.ndarray,
        **kwargs,
    ) -> HSICube:
        arr = np.asarray(spectra, dtype=float)
        h, w = shape_hw
        return cls(arr.reshape(h, w, arr.shape[-1]), wavelengths, **kwargs)

    # --- immutable updates ---
    def with_data(
        self,
        data: np.ndarray,
        *,
        wavelengths: np.ndarray | None = None,
        is_reflectance: bool | None = None,
    ) -> HSICube:
        return HSICube(
            data=data,
            wavelengths=self.wavelengths if wavelengths is None else wavelengths,
            mask=self.mask,
            is_reflectance=self.is_reflectance if is_reflectance is None else is_reflectance,
            meta=dict(self.meta),
        )

    def with_mask(self, mask: np.ndarray) -> HSICube:
        return HSICube(
            data=self.data,
            wavelengths=self.wavelengths,
            mask=mask,
            is_reflectance=self.is_reflectance,
            meta=dict(self.meta),
        )
