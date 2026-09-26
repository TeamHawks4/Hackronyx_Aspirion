"""
Pydantic request / response models for the UHI API.
"""

from pydantic import BaseModel, Field


# ── Metadata ─────────────────────────────────────────────────────
class BoundsResponse(BaseModel):
    west: float
    east: float
    south: float
    north: float


class MetadataResponse(BaseModel):
    years: list[int]
    layers: list[str]
    bounds: BoundsResponse
    disclaimer: str


# ── Point query ──────────────────────────────────────────────────
class PointValues(BaseModel):
    year: int
    lst: float | None = None
    ndvi: float | None = None
    ndbi: float | None = None
    ndwi: float | None = None
    lulc: int | None = None


class PointQueryResponse(BaseModel):
    lat: float
    lon: float
    values: list[PointValues]
    hotspot_score: float | None = None


# ── Zonal statistics ─────────────────────────────────────────────
class ZonalStatsRequest(BaseModel):
    west: float
    east: float
    south: float
    north: float
    year: int
    layer: str = "lst"


class ZonalStatsResponse(BaseModel):
    layer: str
    year: int
    mean: float
    median: float
    min: float
    max: float
    std: float
    pixel_count: int


# ── Correlation ──────────────────────────────────────────────────
class CorrelationPoint(BaseModel):
    x: float
    y: float


class CorrelationResponse(BaseModel):
    year: int
    x_layer: str
    y_layer: str
    points: list[CorrelationPoint]
    correlation: float
    slope: float
    intercept: float


# ── Scenario ─────────────────────────────────────────────────────
class ScenarioRequest(BaseModel):
    west: float = Field(..., description="Bounding box west longitude")
    east: float = Field(..., description="Bounding box east longitude")
    south: float = Field(..., description="Bounding box south latitude")
    north: float = Field(..., description="Bounding box north latitude")
    year: int = Field(2025, description="Base year for the scenario")
    ndvi_change: float = Field(0.0, description="NDVI change (-1 to +1)")
    ndbi_change: float = Field(0.0, description="NDBI change (-1 to +1)")
    ndwi_change: float = Field(0.0, description="NDWI change (-1 to +1)")


class ShapFeature(BaseModel):
    name: str
    value: float
    shap_value: float


class ScenarioResponse(BaseModel):
    base_lst_mean: float
    scenario_lst_mean: float
    delta_lst: float
    base_lst_min: float
    base_lst_max: float
    scenario_lst_min: float
    scenario_lst_max: float
    pixel_count: int
    shap_features: list[ShapFeature]
    disclaimer: str


# ── Temporal trend ───────────────────────────────────────────────
class TrendPoint(BaseModel):
    year: int
    value: float


class TemporalTrendResponse(BaseModel):
    lat: float
    lon: float
    layer: str
    trend: list[TrendPoint]
