"""
Analysis router — point queries, zonal stats, correlations, trends.
"""

from fastapi import APIRouter, Query

from backend.app.services.analysis_service import (
    compute_zonal_stats,
    compute_correlation,
    compute_temporal_trend,
    get_all_point_values,
)

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.get("/point")
async def point_query(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
):
    """Get all layer values at a geographic point across all years."""
    return get_all_point_values(lat, lon)


@router.get("/trend")
async def temporal_trend(
    lat: float = Query(...),
    lon: float = Query(...),
    layer: str = Query("lst"),
):
    """Get time series for a layer at a point."""
    return compute_temporal_trend(lat, lon, layer)


@router.get("/zonal")
async def zonal_stats(
    west: float = Query(...),
    east: float = Query(...),
    south: float = Query(...),
    north: float = Query(...),
    year: int = Query(2025),
    layer: str = Query("lst"),
):
    """Compute zonal statistics for a bounding box."""
    return compute_zonal_stats(layer, year, west, east, south, north)


@router.get("/correlation")
async def correlation(
    year: int = Query(2025),
    x_layer: str = Query("ndvi"),
    y_layer: str = Query("lst"),
):
    """Compute and return scatter plot data + regression for two layers."""
    return compute_correlation(year, x_layer, y_layer)
