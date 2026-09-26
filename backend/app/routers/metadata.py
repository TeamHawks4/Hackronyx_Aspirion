"""
Metadata router — layer info, bounds, years.
"""

import json
from fastapi import APIRouter, HTTPException
from backend.app.config import settings

router = APIRouter(prefix="/metadata", tags=["metadata"])


@router.get("")
async def get_metadata():
    """Return platform metadata: available years, layers, bounds."""
    return {
        "years": settings.YEARS,
        "layers": settings.LAYERS,
        "bounds": {
            "west": settings.WEST,
            "east": settings.EAST,
            "south": settings.SOUTH,
            "north": settings.NORTH,
        },
        "center": {
            "lat": (settings.SOUTH + settings.NORTH) / 2,
            "lon": (settings.WEST + settings.EAST) / 2,
        },
        "lulc_classes": {
            "0": "Water",
            "1": "Dense Vegetation",
            "2": "Sparse Vegetation",
            "3": "Built-up (Low Density)",
            "4": "Built-up (High Density)",
            "5": "Barren / Open Land",
        },
        "disclaimer": (
            "Land Surface Temperature (LST) values represent surface "
            "radiometric temperature derived from satellite thermal bands. "
        ),
    }


@router.get("/boundary")
async def get_boundary():
    """Return Nagpur municipal boundary GeoJSON."""
    boundary_path = settings.VECTOR_DIR / "nagpur_boundary.geojson"
    if not boundary_path.exists():
        raise HTTPException(status_code=404, detail="Boundary file not found")
    with open(boundary_path, "r", encoding="utf-8") as f:
        return json.load(f)

