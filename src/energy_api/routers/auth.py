# Author: Jerry Onyango
# Contribution: Provides auth bootstrap endpoint for minting development JWTs with role and tenant claims.
from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/v1/auth", tags=["Auth"])

ALLOWED_ROLES = {
    "client_admin",
    "facility_manager",
    "energy_analyst",
    "viewer",
    "ops_admin",
    "ml_engineer",
    "customer_success",
    "support_analyst",
}


def _is_truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


@router.post("/dev-token")
def mint_dev_token(payload: dict[str, Any]) -> dict[str, Any]:
    env = os.getenv("EA_ENV", "development")
    dev_auth_enabled = _is_truthy(os.getenv("EA_ENABLE_DEV_AUTH")) or env == "development"
    if not dev_auth_enabled:
        raise HTTPException(status_code=404, detail="Not found")

    secret = os.getenv("EA_JWT_SECRET", "dev-secret-change-me")
    algorithm = os.getenv("EA_JWT_ALGORITHM", "HS256")
    expiry_minutes = int(os.getenv("EA_JWT_EXP_MIN", "120"))
    requested_roles = payload.get("roles", ["viewer"])
    if isinstance(requested_roles, str):
        requested_roles = [requested_roles]

    roles = [str(role) for role in requested_roles if str(role) in ALLOWED_ROLES]
    if not roles:
        raise HTTPException(status_code=400, detail="At least one valid role is required")

    now = datetime.now(UTC)
    claims = {
        "sub": payload.get("sub", "usr_dev"),
        "roles": roles,
        "client_id": payload.get("client_id"),
        "facility_ids": payload.get("facility_ids", []),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expiry_minutes)).timestamp()),
    }
    token = jwt.encode(claims, secret, algorithm=algorithm)
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in_minutes": expiry_minutes,
        "claims": claims,
    }
