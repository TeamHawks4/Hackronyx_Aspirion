"""
Tile service — reads GeoTIFFs and renders colormapped PNG images.

Supports both full-layer image rendering and XYZ tile serving.
"""

import io
import numpy as np
from PIL import Image
import rasterio
from rasterio.windows import from_bounds as window_from_bounds
from functools import lru_cache
from pathlib import Path

from backend.app.config import settings


# ── Color ramps ──────────────────────────────────────────────────
def _lst_colormap(val: np.ndarray) -> np.ndarray:
    """Blue → Cyan → Yellow → Orange → Red → Dark Red (25–55 °C)."""
    norm = np.clip((val - 25) / 30, 0, 1)
    r = np.clip(2.0 * norm, 0, 1)
    g = np.clip(2.0 * norm - 0.3, 0, 1) * np.clip(2.0 * (1 - norm), 0, 1)
    g = np.where(norm < 0.35, norm * 2.5, g)
    b = np.clip(1.0 - 2.5 * norm, 0, 1)
    return np.stack([r, g, b], axis=-1)


def _ndvi_colormap(val: np.ndarray) -> np.ndarray:
    """Brown → Tan → Light Green → Dark Green (-0.2 – 0.85)."""
    norm = np.clip((val + 0.2) / 1.05, 0, 1)
    r = np.clip(0.7 - 0.6 * norm, 0, 1)
    g = np.clip(0.3 + 0.7 * norm, 0, 1)
    b = np.clip(0.15 - 0.1 * norm + 0.15 * norm ** 2, 0, 1)
    return np.stack([r, g, b], axis=-1)


def _ndbi_colormap(val: np.ndarray) -> np.ndarray:
    """Green → Gray → Orange → Red (-0.4 – 0.6)."""
    norm = np.clip((val + 0.4) / 1.0, 0, 1)
    r = np.clip(1.5 * norm - 0.2, 0, 1)
    g = np.clip(0.8 - 0.8 * norm + 0.3 * (1 - np.abs(norm - 0.5) * 2), 0, 1)
    b = np.clip(0.4 * (1 - norm), 0, 1)
    return np.stack([r, g, b], axis=-1)


def _ndwi_colormap(val: np.ndarray) -> np.ndarray:
    """Tan → Light Blue → Deep Blue (-0.5 – 0.7)."""
    norm = np.clip((val + 0.5) / 1.2, 0, 1)
    r = np.clip(0.8 - 0.7 * norm, 0, 1)
    g = np.clip(0.6 - 0.2 * norm + 0.3 * norm, 0, 1)
    b = np.clip(0.3 + 0.7 * norm, 0, 1)
    return np.stack([r, g, b], axis=-1)


def _lulc_colormap(val: np.ndarray) -> np.ndarray:
    """Categorical: 0=Water(blue), 1=Dense Veg(green), 2=Sparse(lightgreen),
    3=Built Low(orange), 4=Built High(red), 5=Barren(tan)."""
    lut = np.array([
        [0.15, 0.40, 0.85],  # 0 Water
        [0.10, 0.55, 0.15],  # 1 Dense Vegetation
        [0.55, 0.78, 0.35],  # 2 Sparse Vegetation
        [0.90, 0.65, 0.25],  # 3 Built-up Low
        [0.85, 0.20, 0.15],  # 4 Built-up High
        [0.82, 0.75, 0.55],  # 5 Barren
    ], dtype=np.float32)
    idx = np.clip(val.astype(int), 0, 5)
    return lut[idx]


def _hotspot_colormap(val: np.ndarray) -> np.ndarray:
    """Transparent → Yellow → Orange → Red (0 – max)."""
    vmax = max(val.max(), 1)
    norm = np.clip(val / vmax, 0, 1)
    r = np.clip(1.5 * norm, 0, 1)
    g = np.clip(1.2 * norm - 0.3 * norm ** 2, 0, 1) * np.clip(1.5 * (1 - norm) + 0.3, 0, 1)
    b = np.zeros_like(norm)
    return np.stack([r, g, b], axis=-1)


def _water_colormap(val: np.ndarray) -> np.ndarray:
    """Transparent → Blue."""
    norm = np.clip(val, 0, 1)
    r = 0.1 * norm
    g = 0.3 * norm
    b = 0.8 * norm
    return np.stack([r, g, b], axis=-1)


COLORMAPS = {
    "lst": _lst_colormap,
    "ndvi": _ndvi_colormap,
    "ndbi": _ndbi_colormap,
    "ndwi": _ndwi_colormap,
    "lulc": _lulc_colormap,
    "hotspots_persistent": _hotspot_colormap,
    "water_mask": _water_colormap,
}

ALPHA_LAYERS = {"hotspots_persistent", "water_mask"}


# ── Raster cache ─────────────────────────────────────────────────
@lru_cache(maxsize=32)
def _read_raster(path_str: str) -> tuple[np.ndarray, dict]:
    """Read entire raster into memory (small files — <1 MB each)."""
    with rasterio.open(path_str) as src:
        data = src.read(1)
        meta = {
            "width": src.width,
            "height": src.height,
            "bounds": src.bounds,
            "transform": src.transform,
            "crs": str(src.crs),
        }
    return data, meta


def _get_raster_path(layer: str, year: int | None = None) -> Path:
    """Resolve raster file path."""
    if layer in ("hotspots_persistent", "water_mask"):
        return settings.RASTER_DIR / f"{layer}.tif"
    return settings.RASTER_DIR / f"{layer}_{year}.tif"


# ── Public API ───────────────────────────────────────────────────
def get_layer_image(layer: str, year: int | None = None,
                    opacity: float = 0.85) -> bytes:
    """
    Render a full-extent colormapped PNG for a layer/year combo.
    Returns PNG bytes.
    """
    path = _get_raster_path(layer, year)
    if not path.exists():
        raise FileNotFoundError(f"Raster not found: {path}")

    data, meta = _read_raster(str(path))
    cmap_fn = COLORMAPS.get(layer, _lst_colormap)
    rgb = cmap_fn(data.astype(np.float32))

    # Convert to uint8
    rgb_u8 = (np.clip(rgb, 0, 1) * 255).astype(np.uint8)

    # Add alpha channel
    if layer in ALPHA_LAYERS:
        alpha = (data > 0.1).astype(np.uint8) * int(opacity * 255)
    else:
        alpha = np.full(data.shape, int(opacity * 255), dtype=np.uint8)

    rgba = np.dstack([rgb_u8, alpha])

    img = Image.fromarray(rgba, "RGBA")
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def get_point_value(layer: str, lat: float, lon: float,
                    year: int | None = None) -> float | None:
    """Read the raster value at a geographic point."""
    path = _get_raster_path(layer, year)
    if not path.exists():
        return None

    data, meta = _read_raster(str(path))
    bounds = meta["bounds"]

    if not (bounds.left <= lon <= bounds.right and
            bounds.bottom <= lat <= bounds.top):
        return None

    col = int((lon - bounds.left) / (bounds.right - bounds.left) * meta["width"])
    row = int((bounds.top - lat) / (bounds.top - bounds.bottom) * meta["height"])

    col = max(0, min(col, meta["width"] - 1))
    row = max(0, min(row, meta["height"] - 1))

    return float(data[row, col])


def get_window_data(layer: str, year: int | None,
                    west: float, east: float,
                    south: float, north: float) -> np.ndarray | None:
    """Extract a spatial window from a raster layer."""
    path = _get_raster_path(layer, year)
    if not path.exists():
        return None

    data, meta = _read_raster(str(path))
    bounds = meta["bounds"]

    # Compute pixel indices
    c1 = int((west - bounds.left) / (bounds.right - bounds.left) * meta["width"])
    c2 = int((east - bounds.left) / (bounds.right - bounds.left) * meta["width"])
    r1 = int((bounds.top - north) / (bounds.top - bounds.bottom) * meta["height"])
    r2 = int((bounds.top - south) / (bounds.top - bounds.bottom) * meta["height"])

    c1, c2 = max(0, c1), min(meta["width"], c2)
    r1, r2 = max(0, r1), min(meta["height"], r2)

    if c2 <= c1 or r2 <= r1:
        return None

    return data[r1:r2, c1:c2]
