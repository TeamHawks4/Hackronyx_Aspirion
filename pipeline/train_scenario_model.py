"""
Train the Random Forest scenario model and generate SHAP explainer.

Input : data/models/training_features.npz (from generate_sample_data)
Output: data/models/uhi_model.joblib
        data/models/shap_values.npz
        data/models/model_metadata.json
"""

import sys
import json
from pathlib import Path
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
MODEL_DIR = DATA_DIR / "models"

FEATURE_NAMES = ["ndvi", "ndbi", "ndwi", "lulc", "urban_intensity", "year_index"]
TARGET = "lst"


def main():
    print("=" * 60)
    print("  Nagpur UHI — ML Scenario Model Training")
    print("=" * 60)

    # ── Load features ────────────────────────────────────────────
    npz_path = MODEL_DIR / "training_features.npz"
    if not npz_path.exists():
        raise FileNotFoundError(
            f"{npz_path} not found. Run generate_sample_data.py first."
        )

    data = np.load(str(npz_path))
    X = np.column_stack([data[f] for f in FEATURE_NAMES])
    y = data[TARGET]

    print(f"  Samples : {len(y):,}")
    print(f"  Features: {FEATURE_NAMES}")
    print(f"  Target  : {TARGET}  (range {y.min():.1f} – {y.max():.1f} °C)")
    print()

    # ── Train / test split ───────────────────────────────────────
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # ── Train Gradient Boosted Trees ─────────────────────────────
    print("▸ Training GradientBoostingRegressor …")
    model = GradientBoostingRegressor(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.08,
        subsample=0.8,
        min_samples_leaf=10,
        random_state=42,
    )
    model.fit(X_train, y_train)

    # ── Evaluate ─────────────────────────────────────────────────
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    print(f"  MAE : {mae:.3f} °C")
    print(f"  R²  : {r2:.4f}")
    print()

    # ── Feature importance (built-in) ────────────────────────────
    importances = dict(zip(FEATURE_NAMES, model.feature_importances_.tolist()))
    print("  Feature importances:")
    for feat, imp in sorted(importances.items(), key=lambda x: -x[1]):
        bar = "█" * int(imp * 50)
        print(f"    {feat:<18s} {imp:.4f}  {bar}")
    print()

    # ── SHAP values (on a subsample for speed) ───────────────────
    print("▸ Computing SHAP values …")
    try:
        import shap

        # Use a subsample for SHAP (full dataset is too slow)
        shap_sample_size = min(500, len(X_test))
        X_shap = X_test[:shap_sample_size]

        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_shap)

        # Save SHAP values for the API to use
        np.savez_compressed(
            str(MODEL_DIR / "shap_values.npz"),
            shap_values=shap_values,
            feature_names=FEATURE_NAMES,
            X_sample=X_shap,
            base_value=explainer.expected_value,
        )
        print(f"  ✓ SHAP values computed for {shap_sample_size} samples")

        # Mean absolute SHAP for global importance
        mean_shap = np.abs(shap_values).mean(axis=0)
        shap_importance = dict(zip(FEATURE_NAMES, mean_shap.tolist()))
    except Exception as e:
        print(f"  ⚠ SHAP computation failed: {e}")
        print("    Falling back to built-in feature importance only.")
        shap_importance = importances

    # ── Save model ───────────────────────────────────────────────
    model_path = MODEL_DIR / "uhi_model.joblib"
    joblib.dump(model, str(model_path))
    print(f"  ✓ Model saved → {model_path.name}")

    # ── Save metadata ────────────────────────────────────────────
    metadata = {
        "model_type": "GradientBoostingRegressor",
        "n_estimators": 300,
        "max_depth": 6,
        "features": FEATURE_NAMES,
        "target": TARGET,
        "metrics": {"mae": round(mae, 4), "r2": round(r2, 4)},
        "feature_importances": importances,
        "shap_importance": {k: round(v, 4) for k, v in shap_importance.items()},
        "target_range": {"min": float(y.min()), "max": float(y.max())},
        "disclaimer": (
            "This model provides scenario-based estimation of Land Surface "
            "Temperature (LST) changes. LST ≠ air temperature. Results are "
            "empirical surrogates learned from historical spatial correlations, "
            "not physical climate simulations."
        ),
    }
    meta_path = MODEL_DIR / "model_metadata.json"
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"  ✓ Metadata saved → {meta_path.name}")

    print()
    print("✅ Model training complete.")


if __name__ == "__main__":
    main()
