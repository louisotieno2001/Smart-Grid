# Author: Jerry Onyango
# Contribution: Boots the FastAPI application, registers domain routers, and serves health and contract endpoints.
from __future__ import annotations

from pathlib import Path
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .core import configure_logging, load_settings
from .routers import auth, ingestion, integrations, integrations_partners, modeling, monitoring, onboarding, public, recommendations

app = FastAPI(
    title="Energy Allocation API",
    version="1.0.0",
    description="FastAPI scaffold for Energy Allocation v1 contract",
)

cors_origins = [
    origin.strip()
    for origin in os.getenv("EA_CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
    if origin.strip()
]
allow_all_origins = len(cors_origins) == 1 and cors_origins[0] == "*"
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=not allow_all_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(onboarding.router)
app.include_router(auth.router)
app.include_router(ingestion.router)
app.include_router(modeling.router)
app.include_router(recommendations.router)
app.include_router(monitoring.router)
app.include_router(integrations.router)
app.include_router(integrations_partners.router)
app.include_router(public.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/openapi.v1.yaml", include_in_schema=False)
def get_contract() -> FileResponse:
    root = Path(__file__).resolve().parents[2]
    contract_path = root / "openapi" / "openapi.v1.yaml"
    return FileResponse(contract_path)


def run() -> None:
    import uvicorn

    settings = load_settings()
    configure_logging()
    uvicorn.run("energy_api.main:app", host=settings.api_host, port=settings.api_port, reload=settings.env == "development")
