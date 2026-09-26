"""
Scenario service — ML-based what-if estimation with SHAP explanations.
"""

import json
import numpy as np
import joblib
from pathlib import Path
from functools import lru_cache

from backend.app.config import settings
from backend.app.services.tile_service import get_window_data


FEATURE_NAMES = ["ndvi", "ndbi", "ndwi", "lulc", "urban_intensity", "year_index"]


@lru_cache(maxsize=1)
def _load_model():
    """Load the trained ML model."""
    model_path = settings.MODEL_DIR / "uhi_model.joblib"
    if not model_path.exists():
        raise FileNotFoundError("Model not found. Run train_scenario_model.py first.")
    return joblib.load(str(model_path))


@lru_cache(maxsize=1)
def _load_metadata() -> dict:
    """Load model metadata."""
    meta_path = settings.MODEL_DIR / "model_metadata.json"
    if not meta_path.exists():
        return {}
    with open(meta_path) as f:
        return json.load(f)


def _year_to_index(year: int) -> int:
    """Convert year to year_index used in training."""
    year_map = {2016: 0, 2019: 1, 2022: 2, 2025: 3}
    return year_map.get(year, 3)


def run_scenario(west: float, east: float, south: float, north: float,
                 year: int, ndvi_change: float, ndbi_change: float,
                 ndwi_change: float) -> dict:
    """
    Run a what-if scenario:
    1. Extract current pixel features in the bounding box
    2. Predict baseline LST with the model
    3. Apply the user's changes to NDVI/NDBI/NDWI
    4. Re-predict → get new LST
    5. Compute SHAP-like feature attribution for the change
    """
    model = _load_model()
    metadata = _load_metadata()

    year_idx = _year_to_index(year)

    # ── Extract features for the region ──────────────────────────
    ndvi_data = get_window_data("ndvi", year, west, east, south, north)
    ndbi_data = get_window_data("ndbi", year, west, east, south, north)
    ndwi_data = get_window_data("ndwi", year, west, east, south, north)
    lulc_data = get_window_data("lulc", year, west, east, south, north)

    if ndvi_data is None or ndvi_data.size == 0:
        return {"error": "No data in the specified region"}

    n_pixels = ndvi_data.size

    # Build feature matrix (base scenario)
    # urban_intensity is approximated from NDBI
    urban_intensity = np.clip(ndbi_data.flatten() * 1.5 + 0.3, 0, 1)

    X_base = np.column_stack([
        ndvi_data.flatten(),
        ndbi_data.flatten(),
        ndwi_data.flatten(),
        lulc_data.flatten().astype(float),
        urban_intensity,
        np.full(n_pixels, year_idx, dtype=float),
    ])

    # ── Baseline prediction ──────────────────────────────────────
    lst_base = model.predict(X_base)

    # ── Scenario: apply changes ──────────────────────────────────
    ndvi_mod = np.clip(ndvi_data.flatten() + ndvi_change, -0.2, 0.85)
    ndbi_mod = np.clip(ndbi_data.flatten() + ndbi_change, -0.4, 0.6)
    ndwi_mod = np.clip(ndwi_data.flatten() + ndwi_change, -0.5, 0.7)

    # Update urban intensity based on NDBI change
    urban_mod = np.clip(ndbi_mod * 1.5 + 0.3, 0, 1)

    X_scenario = np.column_stack([
        ndvi_mod,
        ndbi_mod,
        ndwi_mod,
        lulc_data.flatten().astype(float),
        urban_mod,
        np.full(n_pixels, year_idx, dtype=float),
    ])

    lst_scenario = model.predict(X_scenario)

    # ── SHAP-like attribution ────────────────────────────────────
    # Approximate per-feature contribution by perturbing one at a time
    shap_features = []
    for i, fname in enumerate(FEATURE_NAMES):
        X_perturbed = X_base.copy()
        X_perturbed[:, i] = X_scenario[:, i]
        lst_perturbed = model.predict(X_perturbed)
        contribution = float(np.mean(lst_perturbed - lst_base))
        shap_features.append({
            "name": fname,
            "value": float(np.mean(X_scenario[:, i] - X_base[:, i])),
            "shap_value": round(contribution, 4),
        })

    # Sort by absolute contribution
    shap_features.sort(key=lambda x: abs(x["shap_value"]), reverse=True)

    delta = float(np.mean(lst_scenario) - np.mean(lst_base))

    disclaimer = metadata.get("disclaimer",
        "This is a scenario-based estimation. LST ≠ air temperature.")

    return {
        "base_lst_mean": round(float(np.mean(lst_base)), 3),
        "scenario_lst_mean": round(float(np.mean(lst_scenario)), 3),
        "delta_lst": round(delta, 3),
        "base_lst_min": round(float(np.min(lst_base)), 3),
        "base_lst_max": round(float(np.max(lst_base)), 3),
        "scenario_lst_min": round(float(np.min(lst_scenario)), 3),
        "scenario_lst_max": round(float(np.max(lst_scenario)), 3),
        "pixel_count": n_pixels,
        "shap_features": shap_features,
        "disclaimer": disclaimer,
    }


def get_model_info() -> dict:
    """Return model metadata for the frontend."""
    metadata = _load_metadata()
    return {
        "model_type": metadata.get("model_type", "Unknown"),
        "features": metadata.get("features", FEATURE_NAMES),
        "metrics": metadata.get("metrics", {}),
        "feature_importances": metadata.get("feature_importances", {}),
        "shap_importance": metadata.get("shap_importance", {}),
        "disclaimer": metadata.get("disclaimer", ""),
    }
