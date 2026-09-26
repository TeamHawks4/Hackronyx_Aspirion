"""
Scenario router — ML-based what-if estimation.
"""

from fastapi import APIRouter
from backend.app.models.schemas import ScenarioRequest
from backend.app.services.scenario_service import run_scenario, get_model_info

router = APIRouter(prefix="/scenario", tags=["scenario"])


@router.post("/predict")
async def predict_scenario(req: ScenarioRequest):
    """
    Run a what-if scenario estimation.

    Perturbs NDVI/NDBI/NDWI within a bounding box and returns
    estimated LST change with feature attributions.
    """
    result = run_scenario(
        west=req.west,
        east=req.east,
        south=req.south,
        north=req.north,
        year=req.year,
        ndvi_change=req.ndvi_change,
        ndbi_change=req.ndbi_change,
        ndwi_change=req.ndwi_change,
    )
    return result


@router.get("/model-info")
async def model_info():
    """Return model metadata, metrics, and feature importances."""
    return get_model_info()
