"""
Tile / image router — serves colormapped raster layers as PNG images.
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from backend.app.services.tile_service import get_layer_image

router = APIRouter(prefix="/layers", tags=["layers"])


@router.get("/{layer}/{year}/image")
async def layer_image(
    layer: str,
    year: int,
    opacity: float = Query(0.85, ge=0, le=1),
):
    """Render a full-extent colormapped PNG for a layer/year."""
    try:
        png_bytes = get_layer_image(layer, year, opacity)
        return Response(content=png_bytes, media_type="image/png")
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{layer}/image")
async def static_layer_image(
    layer: str,
    opacity: float = Query(0.85, ge=0, le=1),
):
    """Render a static layer (e.g., hotspots_persistent, water_mask)."""
    try:
        png_bytes = get_layer_image(layer, year=None, opacity=opacity)
        return Response(content=png_bytes, media_type="image/png")
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
