"""
Realistic multi-temporal sample data generator for Nagpur UHI analysis.

Generates Cloud-Optimized GeoTIFFs for LST, NDVI, NDBI, NDWI, and LULC
across 4 time periods (2016, 2019, 2022, 2025) with:
  - Spatial patterns mimicking real Nagpur urban structure
  - Temporal progression showing increasing urbanization
  - Physically consistent relationships between indices
  - Persistent hotspot overlay from multi-temporal analysis
"""

import sys
from pathlib import Path
import json
import numpy as np
from scipy.ndimage import gaussian_filter

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Geographic constants — Nagpur, Maharashtra
# ---------------------------------------------------------------------------
WEST, EAST = 78.95, 79.20
SOUTH, NORTH = 21.04, 21.26
WIDTH, HEIGHT = 250, 220  # pixels (~100 m effective resolution)
YEARS = [2016, 2019, 2022, 2025]

# Nagpur landmarks (lat, lon)
LANDMARKS = {
    "city_center":     (21.1458, 79.0882),
    "ambazari_lake":   (21.1300, 79.0480),
    "futala_lake":     (21.1500, 79.0400),
    "seminary_hills":  (21.1500, 79.0600),
    "railway_station": (21.1490, 79.0890),
    "midc_hingna":     (21.1050, 79.0300),
    "midc_butibori":   (21.0600, 79.0700),
    "university":      (21.1420, 79.0750),
    "dharampeth":      (21.1530, 79.0700),
    "mankapur":        (21.1680, 79.0750),
    "koradi_lake":     (21.2200, 79.1050),
    "gorewada":        (21.1750, 79.0500),
    "wardha_road":     (21.1200, 79.1100),
    "kamptee":         (21.2150, 79.1850),
}

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
RASTER_DIR = DATA_DIR / "rasters"
VECTOR_DIR = DATA_DIR / "vectors"
MODEL_DIR = DATA_DIR / "models"


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------
def _ll_to_pixel(lat: float, lon: float) -> tuple[int, int]:
    """Convert (lat, lon) → (row, col) in pixel space."""
    col = int((lon - WEST) / (EAST - WEST) * WIDTH)
    row = int((NORTH - lat) / (NORTH - SOUTH) * HEIGHT)
    return (
        max(0, min(row, HEIGHT - 1)),
        max(0, min(col, WIDTH - 1)),
    )


def _gaussian_blob(lat: float, lon: float, sigma: float = 15,
                    amplitude: float = 1.0) -> np.ndarray:
    """2-D Gaussian centered at a geographic point."""
    cy, cx = _ll_to_pixel(lat, lon)
    yy, xx = np.ogrid[:HEIGHT, :WIDTH]
    d2 = (yy - cy) ** 2 + (xx - cx) ** 2
    return amplitude * np.exp(-d2 / (2 * sigma ** 2))


def _boundary_mask() -> np.ndarray:
    """Binary mask from the Nagpur boundary GeoJSON (rasterised)."""
    boundary_file = VECTOR_DIR / "nagpur_boundary.geojson"
    with open(boundary_file) as f:
        geojson = json.load(f)
    coords = geojson["features"][0]["geometry"]["coordinates"][0]

    from shapely.geometry import Polygon, Point

    poly = Polygon(coords)
    mask = np.zeros((HEIGHT, WIDTH), dtype=bool)
    for r in range(HEIGHT):
        for c in range(WIDTH):
            lon = WEST + (c + 0.5) / WIDTH * (EAST - WEST)
            lat = NORTH - (r + 0.5) / HEIGHT * (NORTH - SOUTH)
            if poly.contains(Point(lon, lat)):
                mask[r, c] = True
    return mask


# ---------------------------------------------------------------------------
# Layer generators
# ---------------------------------------------------------------------------
def _urbanisation_field(year_idx: int, rng: np.random.Generator) -> np.ndarray:
    """Continuous urbanisation intensity ∈ [0, 1]. Grows with year_idx."""
    field = np.zeros((HEIGHT, WIDTH), dtype=np.float64)

    # Core urban — strongest signal
    field += _gaussian_blob(*LANDMARKS["city_center"], sigma=35, amplitude=0.85)
    field += _gaussian_blob(*LANDMARKS["railway_station"], sigma=18, amplitude=0.60)
    field += _gaussian_blob(*LANDMARKS["dharampeth"], sigma=14, amplitude=0.55)

    # Industrial zones
    field += _gaussian_blob(*LANDMARKS["midc_hingna"], sigma=18, amplitude=0.50)
    field += _gaussian_blob(*LANDMARKS["midc_butibori"], sigma=14, amplitude=0.35)

    # Secondary urban clusters
    field += _gaussian_blob(*LANDMARKS["wardha_road"], sigma=16, amplitude=0.45)
    field += _gaussian_blob(*LANDMARKS["mankapur"], sigma=14, amplitude=0.40)
    field += _gaussian_blob(*LANDMARKS["kamptee"], sigma=12, amplitude=0.30)

    # Suburban expansion patches — more each year
    n_patches = 6 + year_idx * 4
    for _ in range(n_patches):
        lat = rng.uniform(21.06, 21.22)
        lon = rng.uniform(79.00, 79.17)
        amp = rng.uniform(0.08, 0.30)
        sig = rng.uniform(6, 14)
        field += _gaussian_blob(lat, lon, sigma=sig, amplitude=amp)

    # Growth factor
    growth = 1.0 + year_idx * 0.12
    field *= growth

    # Spatial noise for texture
    noise = rng.standard_normal((HEIGHT, WIDTH)) * 0.08
    noise = gaussian_filter(noise, sigma=3)
    field += noise

    return np.clip(field, 0, 1)


def _water_field() -> np.ndarray:
    """Continuous water presence probability."""
    w = np.zeros((HEIGHT, WIDTH), dtype=np.float64)
    w += _gaussian_blob(*LANDMARKS["ambazari_lake"], sigma=5, amplitude=1.0)
    w += _gaussian_blob(*LANDMARKS["futala_lake"], sigma=4, amplitude=0.95)
    w += _gaussian_blob(*LANDMARKS["koradi_lake"], sigma=6, amplitude=0.90)
    # Nag river — approximate as a thin elongated gaussian
    for frac in np.linspace(0, 1, 30):
        lat = 21.14 + frac * 0.02
        lon = 79.06 + frac * 0.06
        w += _gaussian_blob(lat, lon, sigma=2, amplitude=0.40)
    return np.clip(w, 0, 1)


def _green_field(year_idx: int) -> np.ndarray:
    """Vegetation concentration — decreases with urbanisation over time."""
    g = np.zeros((HEIGHT, WIDTH), dtype=np.float64)

    # Seminary Hills / Gorewada forest
    g += _gaussian_blob(*LANDMARKS["seminary_hills"], sigma=14, amplitude=0.90)
    g += _gaussian_blob(*LANDMARKS["gorewada"], sigma=18, amplitude=0.95)

    # University campus
    g += _gaussian_blob(*LANDMARKS["university"], sigma=10, amplitude=0.65)

    # Peripheral agriculture
    yy, xx = np.ogrid[:HEIGHT, :WIDTH]
    cy, cx = _ll_to_pixel(*LANDMARKS["city_center"])
    dist = np.sqrt((yy - cy) ** 2 + (xx - cx) ** 2)
    g += 0.55 * np.clip((dist - 50) / 40, 0, 1)

    # Decrease vegetation over time (urban encroachment)
    decay = 1.0 - year_idx * 0.08
    g *= decay

    return np.clip(g, 0, 1)


def generate_ndvi(urban: np.ndarray, green: np.ndarray, water: np.ndarray,
                  rng: np.random.Generator) -> np.ndarray:
    """NDVI ∈ [-0.2, 0.85]. High green → high NDVI; high urban → low."""
    ndvi = 0.75 * green - 0.40 * urban - 0.10 * water + 0.15
    noise = rng.standard_normal((HEIGHT, WIDTH)) * 0.04
    noise = gaussian_filter(noise, sigma=2)
    ndvi += noise
    return np.clip(ndvi, -0.2, 0.85).astype(np.float32)


def generate_ndbi(urban: np.ndarray, green: np.ndarray, water: np.ndarray,
                  rng: np.random.Generator) -> np.ndarray:
    """NDBI ∈ [-0.4, 0.6]. High urban → high NDBI."""
    ndbi = 0.55 * urban - 0.35 * green - 0.25 * water + 0.05
    noise = rng.standard_normal((HEIGHT, WIDTH)) * 0.04
    noise = gaussian_filter(noise, sigma=2)
    ndbi += noise
    return np.clip(ndbi, -0.4, 0.6).astype(np.float32)


def generate_ndwi(water: np.ndarray, green: np.ndarray,
                  rng: np.random.Generator) -> np.ndarray:
    """NDWI ∈ [-0.5, 0.7]. High water → high NDWI."""
    ndwi = 0.65 * water + 0.15 * green - 0.20
    noise = rng.standard_normal((HEIGHT, WIDTH)) * 0.03
    noise = gaussian_filter(noise, sigma=2)
    ndwi += noise
    return np.clip(ndwi, -0.5, 0.7).astype(np.float32)


def generate_lst(ndvi: np.ndarray, ndbi: np.ndarray, ndwi: np.ndarray,
                 urban: np.ndarray, year_idx: int,
                 rng: np.random.Generator) -> np.ndarray:
    """
    Land Surface Temperature (°C).

    Empirical surrogate: LST is driven by built-up fraction (positive),
    vegetation fraction (negative cooling), and water presence (negative).
    Nagpur pre-monsoon typical range: ~30–52 °C.
    """
    base_temp = 35.0 + year_idx * 0.8  # warming trend

    lst = (
        base_temp
        + 14.0 * ndbi            # built-up raises temperature
        - 10.0 * ndvi            # vegetation cools
        - 6.0 * ndwi             # water cools
        + 5.0 * urban            # additional urban heat
    )

    # Spatial noise
    noise = rng.standard_normal((HEIGHT, WIDTH)) * 1.2
    noise = gaussian_filter(noise, sigma=3)
    lst += noise

    return np.clip(lst, 25.0, 55.0).astype(np.float32)


def generate_lulc(urban: np.ndarray, green: np.ndarray,
                  water: np.ndarray) -> np.ndarray:
    """
    Land-use / land-cover classification (integer labels).

    Classes:
      0 — Water
      1 — Dense Vegetation / Forest
      2 — Sparse Vegetation / Agriculture
      3 — Built-up (Low Density)
      4 — Built-up (High Density)
      5 — Barren / Open Land
    """
    lulc = np.full((HEIGHT, WIDTH), 5, dtype=np.uint8)  # default barren

    # Layer by priority (highest last wins)
    lulc[green > 0.25] = 2   # sparse veg
    lulc[green > 0.55] = 1   # dense veg
    lulc[urban > 0.25] = 3   # low-density built-up
    lulc[urban > 0.55] = 4   # high-density built-up
    lulc[water > 0.40] = 0   # water

    return lulc


# ---------------------------------------------------------------------------
# GeoTIFF writer (COG profile)
# ---------------------------------------------------------------------------
def _write_geotiff(data: np.ndarray, path: Path, dtype: str = "float32",
                   nodata: float | None = None):
    """Write a single-band GeoTIFF with COG-friendly settings."""
    import rasterio
    from rasterio.transform import from_bounds
    from rasterio.crs import CRS

    transform = from_bounds(WEST, SOUTH, EAST, NORTH, WIDTH, HEIGHT)
    profile = {
        "driver": "GTiff",
        "dtype": dtype,
        "width": WIDTH,
        "height": HEIGHT,
        "count": 1,
        "crs": CRS.from_epsg(4326),
        "transform": transform,
        "compress": "deflate",
        "tiled": True,
        "blockxsize": 256,
        "blockysize": 256,
    }
    if nodata is not None:
        profile["nodata"] = nodata

    path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(str(path), "w", **profile) as dst:
        dst.write(data, 1)

    print(f"  ✓ {path.name}")


# ---------------------------------------------------------------------------
# Persistent hotspot analysis
# ---------------------------------------------------------------------------
def compute_persistent_hotspots(lst_stack: dict[int, np.ndarray]) -> np.ndarray:
    """
    Simplified Getis-Ord–inspired persistent hotspot detection.

    For each year, pixels above the 85th percentile are flagged hot.
    The persistence score = number of years a pixel is flagged.
    """
    hot_counts = np.zeros((HEIGHT, WIDTH), dtype=np.float32)
    for year, lst in lst_stack.items():
        threshold = np.nanpercentile(lst, 85)
        hot_counts += (lst >= threshold).astype(np.float32)

    # Smooth for spatial coherence
    hot_counts = gaussian_filter(hot_counts, sigma=2)

    return hot_counts  # 0 → never hot, len(YEARS) → always hot


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("  Nagpur UHI — Sample Data Generator")
    print("=" * 60)
    print(f"  Extent : {WEST}°E – {EAST}°E, {SOUTH}°N – {NORTH}°N")
    print(f"  Grid   : {WIDTH} × {HEIGHT} pixels")
    print(f"  Years  : {YEARS}")
    print()

    RASTER_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(seed=2025)
    water = _water_field()

    lst_stack: dict[int, np.ndarray] = {}
    all_features = []  # for ML training data

    for idx, year in enumerate(YEARS):
        print(f"▸ Generating layers for {year} …")
        year_rng = np.random.default_rng(seed=2025 + idx * 100)

        urban = _urbanisation_field(idx, year_rng)
        green = _green_field(idx)

        ndvi = generate_ndvi(urban, green, water, year_rng)
        ndbi = generate_ndbi(urban, green, water, year_rng)
        ndwi = generate_ndwi(water, green, year_rng)
        lst = generate_lst(ndvi, ndbi, ndwi, urban, idx, year_rng)
        lulc = generate_lulc(urban, green, water)

        # Write GeoTIFFs
        _write_geotiff(lst,  RASTER_DIR / f"lst_{year}.tif")
        _write_geotiff(ndvi, RASTER_DIR / f"ndvi_{year}.tif")
        _write_geotiff(ndbi, RASTER_DIR / f"ndbi_{year}.tif")
        _write_geotiff(ndwi, RASTER_DIR / f"ndwi_{year}.tif")
        _write_geotiff(lulc, RASTER_DIR / f"lulc_{year}.tif", dtype="uint8")

        lst_stack[year] = lst

        # Collect per-pixel feature vectors for ML training
        for r in range(0, HEIGHT, 2):  # subsample for speed
            for c in range(0, WIDTH, 2):
                all_features.append({
                    "ndvi": float(ndvi[r, c]),
                    "ndbi": float(ndbi[r, c]),
                    "ndwi": float(ndwi[r, c]),
                    "lulc": int(lulc[r, c]),
                    "urban_intensity": float(urban[r, c]),
                    "year_index": idx,
                    "lst": float(lst[r, c]),
                })

    # Persistent hotspots
    print("▸ Computing persistent hotspots …")
    hotspots = compute_persistent_hotspots(lst_stack)
    _write_geotiff(hotspots, RASTER_DIR / "hotspots_persistent.tif")

    # Water mask (static)
    _write_geotiff(water.astype(np.float32), RASTER_DIR / "water_mask.tif")

    # Save training features as .npz for the ML pipeline
    print("▸ Saving ML training features …")
    import pandas as pd  # noqa: delayed import — not in hot path
    df = __import__("pandas").DataFrame(all_features)
    npz_path = MODEL_DIR / "training_features.npz"
    np.savez_compressed(
        str(npz_path),
        ndvi=df["ndvi"].values,
        ndbi=df["ndbi"].values,
        ndwi=df["ndwi"].values,
        lulc=df["lulc"].values,
        urban_intensity=df["urban_intensity"].values,
        year_index=df["year_index"].values,
        lst=df["lst"].values,
    )
    print(f"  ✓ {npz_path.name}  ({len(df):,} samples)")

    print()
    print("✅ Data generation complete.")
    print(f"   Rasters → {RASTER_DIR}")
    print(f"   Models  → {MODEL_DIR}")


if __name__ == "__main__":
    main()
