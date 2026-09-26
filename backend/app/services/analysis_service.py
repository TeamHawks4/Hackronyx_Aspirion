"""
Analysis service — zonal statistics, correlations, temporal trends.
"""

import numpy as np
from scipy import stats

from backend.app.config import settings
from backend.app.services.tile_service import get_window_data, get_point_value


def compute_zonal_stats(layer: str, year: int,
                        west: float, east: float,
                        south: float, north: float) -> dict:
    """Compute basic statistics for a spatial window."""
    data = get_window_data(layer, year, west, east, south, north)
    if data is None or data.size == 0:
        return {"error": "No data in the specified region"}

    flat = data.flatten()
    flat = flat[np.isfinite(flat)]

    if len(flat) == 0:
        return {"error": "All values are NaN in the region"}

    return {
        "layer": layer,
        "year": year,
        "mean": round(float(np.mean(flat)), 3),
        "median": round(float(np.median(flat)), 3),
        "min": round(float(np.min(flat)), 3),
        "max": round(float(np.max(flat)), 3),
        "std": round(float(np.std(flat)), 3),
        "pixel_count": int(len(flat)),
    }


def compute_correlation(year: int,
                        x_layer: str = "ndvi",
                        y_layer: str = "lst",
                        max_points: int = 2000) -> dict:
    """
    Compute point-wise correlation between two layers for a given year.
    Returns a subsample of points + regression stats.
    """
    x_data = get_window_data(x_layer, year,
                             settings.WEST, settings.EAST,
                             settings.SOUTH, settings.NORTH)
    y_data = get_window_data(y_layer, year,
                             settings.WEST, settings.EAST,
                             settings.SOUTH, settings.NORTH)

    if x_data is None or y_data is None:
        return {"error": "Layer data not found"}

    x_flat = x_data.flatten()
    y_flat = y_data.flatten()

    # Filter valid values
    valid = np.isfinite(x_flat) & np.isfinite(y_flat)
    x_flat = x_flat[valid]
    y_flat = y_flat[valid]

    if len(x_flat) < 10:
        return {"error": "Insufficient data points"}

    # Subsample for the scatter plot
    if len(x_flat) > max_points:
        idx = np.random.default_rng(42).choice(len(x_flat), max_points, replace=False)
        x_sub = x_flat[idx]
        y_sub = y_flat[idx]
    else:
        x_sub = x_flat
        y_sub = y_flat

    # Regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(x_flat, y_flat)

    points = [{"x": round(float(x), 4), "y": round(float(y), 3)}
              for x, y in zip(x_sub, y_sub)]

    return {
        "year": year,
        "x_layer": x_layer,
        "y_layer": y_layer,
        "points": points,
        "correlation": round(float(r_value), 4),
        "slope": round(float(slope), 4),
        "intercept": round(float(intercept), 4),
    }


def compute_temporal_trend(lat: float, lon: float,
                           layer: str = "lst") -> dict:
    """Extract time series for a point across all years."""
    trend = []
    for year in settings.YEARS:
        val = get_point_value(layer, lat, lon, year)
        if val is not None:
            trend.append({"year": year, "value": round(val, 3)})

    return {
        "lat": lat,
        "lon": lon,
        "layer": layer,
        "trend": trend,
    }


def get_all_point_values(lat: float, lon: float) -> dict:
    """Get all layer values at a point across all years."""
    values = []
    for year in settings.YEARS:
        entry = {"year": year}
        for layer in ["lst", "ndvi", "ndbi", "ndwi", "lulc"]:
            val = get_point_value(layer, lat, lon, year)
            if val is not None:
                entry[layer] = round(val, 3) if layer != "lulc" else int(val)
        values.append(entry)

    hotspot = get_point_value("hotspots_persistent", lat, lon)

    return {
        "lat": lat,
        "lon": lon,
        "values": values,
        "hotspot_score": round(hotspot, 3) if hotspot is not None else None,
    }
