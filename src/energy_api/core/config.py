# Author: Jerry Onyango
# Contribution: Centralizes environment-based runtime configuration for API, auth, and database integration.
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    env: str
    api_host: str
    api_port: int
    jwt_secret: str
    jwt_algorithm: str
    db_url: str



def load_settings() -> Settings:
    return Settings(
        env=os.getenv("EA_ENV", "development"),
        api_host=os.getenv("EA_API_HOST", "0.0.0.0"),
        api_port=int(os.getenv("EA_API_PORT", "8000")),
        jwt_secret=os.getenv("EA_JWT_SECRET", "dev-secret-change-me"),
        jwt_algorithm=os.getenv("EA_JWT_ALGORITHM", "HS256"),
        db_url=os.getenv("EA_DATABASE_URL", "postgresql+psycopg://energyallocation:energyallocation@localhost:5432/energyallocation"),
    )
