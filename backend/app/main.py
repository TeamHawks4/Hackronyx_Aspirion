"""
FastAPI application — Multi-Temporal Urban Heat Island Analysis Platform.

Serves colormapped raster layers, spatial analytics, and ML scenario
predictions for the Nagpur UHI study.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import settings
from backend.app.routers import metadata, tiles, analysis, scenario

app = FastAPI(
    title="Nagpur UHI Analysis Platform",
    description=(
        "Multi-Temporal Urban Heat Island Analysis & AI Prediction API. "
        "Provides geospatial layer rendering, temporal analytics, and "
        "scenario-based LST estimation for Nagpur, Maharashtra."
    ),
    version="1.0.0",
)

# ── CORS ─────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ──────────────────────────────────────────────────────
app.include_router(metadata.router, prefix=settings.API_PREFIX)
app.include_router(tiles.router, prefix=settings.API_PREFIX)
app.include_router(analysis.router, prefix=settings.API_PREFIX)
app.include_router(scenario.router, prefix=settings.API_PREFIX)


@app.get("/")
async def root():
    return {
        "name": "Nagpur UHI Analysis Platform",
        "version": "1.0.0",
        "docs": "/docs",
        "api_prefix": settings.API_PREFIX,
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
