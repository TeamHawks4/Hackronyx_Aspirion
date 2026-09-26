"""
Central configuration for the FastAPI backend.
"""

from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings — all paths relative to project root."""

    PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = PROJECT_ROOT / "data"
    RASTER_DIR: Path = DATA_DIR / "rasters"
    MODEL_DIR: Path = DATA_DIR / "models"
    VECTOR_DIR: Path = DATA_DIR / "vectors"

    # Geographic extent of the study area
    WEST: float = 78.95
    EAST: float = 79.20
    SOUTH: float = 21.04
    NORTH: float = 21.26

    # Available analysis years
    YEARS: list[int] = [2016, 2019, 2022, 2025]

    # Available raster layers
    LAYERS: list[str] = ["lst", "ndvi", "ndbi", "ndwi", "lulc", "hotspots_persistent", "water_mask"]

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"]

    # API
    API_PREFIX: str = "/api"

    class Config:
        env_prefix = "UHI_"


settings = Settings()
