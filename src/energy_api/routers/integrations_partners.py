# Author: Jerry Onyango
# Contribution: Manages third-party partner integrations, API keys, webhooks, and authorized access with scoped permissions.
from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta
from typing import Any
from secrets import token_urlsafe
import hmac
import hashlib

from fastapi import APIRouter, Depends, HTTPException, status, Header

from energy_api.security import enforce_client_scope, require_roles, Principal, get_current_principal
from energy_api.store import store

router = APIRouter(prefix="/v1/integrations", tags=["Partner Integrations"])


# ============================================================================
# Partner Registration & Management
# ============================================================================

@router.post("/partners", status_code=201)
def register_partner(
    payload: dict[str, Any],
    _principal: Principal = Depends(require_roles("ops_admin", "customer_success")),
) -> dict[str, Any]:
    """
    Register a new third-party partner organization.
    
    Only internal ops_admin or customer_success can register partners.
    Partners get assigned a unique ID and initial credentials (to be rotated).
    """
    partner_id = store.make_id("ptn")
    
    partner = {
        "partner_id": partner_id,
        "name": payload.get("name"),
        "industry": payload.get("industry"),
        "contact_email": payload.get("contact_email"),
        "contact_name": payload.get("contact_name"),
        "status": "active",
        "created_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "created_by": _principal.subject,
        "assigned_clients": [],  # clients this partner can access
        "assigned_scopes": payload.get("scopes", ["read:facilities", "read:recommendations"]),  # default scopes
    }
    store.partners[partner_id] = partner
    record_integration_audit("partner.registered", partner_id, _principal, partner)
    
    return {
        "partner_id": partner_id,
        "status": "active",
        "created_at": partner["created_at"],
        "next_step": f"Create API key via POST /v1/integrations/partners/{partner_id}/keys",
    }


@router.get("/partners/{partner_id}")
def get_partner(
    partner_id: str,
    _principal: Principal = Depends(require_roles("ops_admin", "customer_success")),
) -> dict[str, Any]:
    """Get partner details (internal only)."""
    partner = store.partners.get(partner_id)
    if not partner:
        raise HTTPException(status_code=404, detail="partner not found")
    return partner


@router.get("/partners")
def list_partners(
    status: str | None = None,
    limit: int = 50,
    _principal: Principal = Depends(require_roles("ops_admin", "customer_success")),
) -> dict[str, Any]:
    """List all registered partners (internal only)."""
    items = [
        p for p in store.partners.values()
        if status is None or p.get("status") == status
    ]
    return {"items": items[:limit], "total": len(items)}


@router.patch("/partners/{partner_id}")
def update_partner(
    partner_id: str,
    payload: dict[str, Any],
    _principal: Principal = Depends(require_roles("ops_admin", "customer_success")),
) -> dict[str, Any]:
    """Update partner metadata (status, assigned clients, scopes)."""
    partner = store.partners.get(partner_id)
    if not partner:
        raise HTTPException(status_code=404, detail="partner not found")
    
    partner["status"] = payload.get("status", partner["status"])
    if "assigned_clients" in payload:
        partner["assigned_clients"] = payload.get("assigned_clients", [])
    if "assigned_scopes" in payload:
        partner["assigned_scopes"] = payload.get("assigned_scopes", [])
    
    store.partners[partner_id] = partner
    record_integration_audit("partner.updated", partner_id, _principal, payload)
    
    return partner


# ============================================================================
# API Key Management (OAuth2-style)
# ============================================================================

@router.post("/partners/{partner_id}/keys", status_code=201)
def create_partner_api_key(
    partner_id: str,
    payload: dict[str, Any],
    _principal: Principal = Depends(require_roles("ops_admin", "customer_success")),
) -> dict[str, Any]:
    """
    Create a new API key for a partner.
    
    Returns both the key ID and secret. Secret is only shown once—
    partner must store it securely. Recommend rotation every 90 days.
    """
    partner = store.partners.get(partner_id)
    if not partner:
        raise HTTPException(status_code=404, detail="partner not found")
    
    key_id = store.make_id("key")
    secret = token_urlsafe(32)  # 256-bit secret in URL-safe base64
    secret_hash = hashlib.sha256(secret.encode()).hexdigest()
    
    api_key = {
        "key_id": key_id,
        "partner_id": partner_id,
        "name": payload.get("name", "Integration Key"),
        "scopes": payload.get("scopes", partner.get("assigned_scopes", [])),
        "status": "active",
        "created_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "created_by": _principal.subject,
        "last_used_at": None,
        "expires_at": (datetime.now(UTC) + timedelta(days=90)).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "secret_hash": secret_hash,  # only hash is stored, never the actual secret
    }
    store.partner_api_keys[key_id] = api_key
    record_integration_audit("api_key.created", key_id, _principal, {"partner_id": partner_id})
    
    return {
        "key_id": key_id,
        "secret": secret,  # Only returned once
        "partner_id": partner_id,
        "scopes": api_key["scopes"],
        "created_at": api_key["created_at"],
        "expires_at": api_key["expires_at"],
        "warning": "Store the secret securely. It will not be shown again. Rotate every 90 days.",
    }


@router.get("/partners/{partner_id}/keys")
def list_partner_api_keys(
    partner_id: str,
    status: str | None = None,
    _principal: Principal = Depends(require_roles("ops_admin", "customer_success")),
) -> dict[str, Any]:
    """List API keys for a partner (secret not included, only hashes shown)."""
    partner = store.partners.get(partner_id)
    if not partner:
        raise HTTPException(status_code=404, detail="partner not found")
    
    items = [
        {k: v for k, v in key.items() if k != "secret_hash"}
        for key in store.partner_api_keys.values()
        if key.get("partner_id") == partner_id
        and (status is None or key.get("status") == status)
    ]
    return {"items": items, "partner_id": partner_id}


@router.patch("/partners/{partner_id}/keys/{key_id}")
def rotate_partner_api_key(
    partner_id: str,
    key_id: str,
    payload: dict[str, Any],
    _principal: Principal = Depends(require_roles("ops_admin", "customer_success")),
) -> dict[str, Any]:
    """
    Rotate or revoke a partner API key.
    
    - To rotate: send action=rotate → returns new key with secret
    - To revoke: send action=revoke → marks as inactive, cannot be used
    """
    api_key = store.partner_api_keys.get(key_id)
    if not api_key or api_key.get("partner_id") != partner_id:
        raise HTTPException(status_code=404, detail="key not found")
    
    action = payload.get("action", "rotate")
    
    if action == "revoke":
        api_key["status"] = "revoked"
        api_key["revoked_at"] = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        store.partner_api_keys[key_id] = api_key
        record_integration_audit("api_key.revoked", key_id, _principal, {"partner_id": partner_id})
        return {"key_id": key_id, "status": "revoked"}
    
    elif action == "rotate":
        # Keep old key as revoked, create new one
        api_key["status"] = "revoked"
        api_key["revoked_at"] = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        store.partner_api_keys[key_id] = api_key
        
        new_key_id = store.make_id("key")
        new_secret = token_urlsafe(32)
        new_secret_hash = hashlib.sha256(new_secret.encode()).hexdigest()
        
        new_api_key = {
            "key_id": new_key_id,
            "partner_id": partner_id,
            "name": api_key.get("name", "Integration Key"),
            "scopes": api_key.get("scopes", []),
            "status": "active",
            "created_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "created_by": _principal.subject,
            "last_used_at": None,
            "expires_at": (datetime.now(UTC) + timedelta(days=90)).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "secret_hash": new_secret_hash,
        }
        store.partner_api_keys[new_key_id] = new_api_key
        record_integration_audit("api_key.rotated", new_key_id, _principal, {"old_key": key_id, "partner_id": partner_id})
        
        return {
            "key_id": new_key_id,
            "secret": new_secret,
            "partner_id": partner_id,
            "scopes": new_api_key["scopes"],
            "created_at": new_api_key["created_at"],
            "expires_at": new_api_key["expires_at"],
            "warning": "Store the secret securely. It will not be shown again.",
        }
    
    else:
        raise HTTPException(status_code=400, detail="Unknown action. Use 'rotate' or 'revoke'.")


# ============================================================================
# Webhook Management for Partner Integrations
# ============================================================================

@router.post("/partners/{partner_id}/webhooks", status_code=201)
def create_partner_webhook(
    partner_id: str,
    payload: dict[str, Any],
    _principal: Principal = Depends(require_roles("ops_admin", "customer_success", "client_admin")),
) -> dict[str, Any]:
    """
    Register a webhook endpoint for a partner integration.
    
    Partner will receive signed webhook payloads for:
    - connector.sync_failed, connector.sync_succeeded
    - ingestion.import_started, ingestion.import_completed
    - model.run_completed, model.run_failed
    - recommendation.created, recommendation.accepted, recommendation.rejected
    - drift.detected
    - retraining.triggered
    - savings.realized_update
    """
    partner = store.partners.get(partner_id)
    if not partner:
        raise HTTPException(status_code=404, detail="partner not found")
    
    webhook_id = store.make_id("whp")
    webhook = {
        "webhook_id": webhook_id,
        "partner_id": partner_id,
        "url": payload.get("url"),
        "description": payload.get("description", ""),
        "status": "active",
        "events": payload.get("events", [
            "connector.sync_failed",
            "ingestion.import_completed",
            "model.run_completed",
            "recommendation.created",
        ]),
        "created_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "created_by": _principal.subject,
        "retry_policy": {
            "max_retries": payload.get("max_retries", 3),
            "backoff_seconds": payload.get("backoff_seconds", 60),
        },
        "signature_algorithm": "hmac-sha256",  # All webhooks signed with partner's API key
    }
    store.partner_webhooks[webhook_id] = webhook
    record_integration_audit("webhook.created", webhook_id, _principal, {"partner_id": partner_id})
    
    return {
        "webhook_id": webhook_id,
        "partner_id": partner_id,
        "status": "active",
        "created_at": webhook["created_at"],
        "url": webhook["url"],
        "events": webhook["events"],
    }


@router.get("/partners/{partner_id}/webhooks")
def list_partner_webhooks(
    partner_id: str,
    _principal: Principal = Depends(require_roles("ops_admin", "customer_success", "client_admin")),
) -> dict[str, Any]:
    """List webhooks for a partner."""
    partner = store.partners.get(partner_id)
    if not partner:
        raise HTTPException(status_code=404, detail="partner not found")
    
    items = [
        w for w in store.partner_webhooks.values()
        if w.get("partner_id") == partner_id
    ]
    return {"items": items, "partner_id": partner_id}


@router.patch("/partners/{partner_id}/webhooks/{webhook_id}")
def update_partner_webhook(
    partner_id: str,
    webhook_id: str,
    payload: dict[str, Any],
    _principal: Principal = Depends(require_roles("ops_admin", "customer_success", "client_admin")),
) -> dict[str, Any]:
    """Update webhook URL, events, or status."""
    webhook = store.partner_webhooks.get(webhook_id)
    if not webhook or webhook.get("partner_id") != partner_id:
        raise HTTPException(status_code=404, detail="webhook not found")
    
    webhook["url"] = payload.get("url", webhook["url"])
    webhook["events"] = payload.get("events", webhook["events"])
    webhook["status"] = payload.get("status", webhook["status"])
    
    store.partner_webhooks[webhook_id] = webhook
    record_integration_audit("webhook.updated", webhook_id, _principal, {"partner_id": partner_id})
    
    return webhook


# ============================================================================
# Partner Access & Allocation Management
# ============================================================================

@router.post("/partners/{partner_id}/allocations", status_code=201)
def assign_partner_to_client(
    partner_id: str,
    payload: dict[str, Any],
    _principal: Principal = Depends(require_roles("ops_admin", "customer_success")),
) -> dict[str, Any]:
    """
    Assign a partner to access a specific client's data.
    
    This creates a scoped grant allowing the partner to read/write
    data for the assigned client and its facilities.
    """
    partner = store.partners.get(partner_id)
    if not partner:
        raise HTTPException(status_code=404, detail="partner not found")
    
    client_id = payload.get("client_id")
    if not client_id:
        raise HTTPException(status_code=400, detail="client_id required")
    
    allocation_id = store.make_id("alloc")
    allocation = {
        "allocation_id": allocation_id,
        "partner_id": partner_id,
        "client_id": client_id,
        "status": "active",
        "scopes": payload.get("scopes", partner.get("assigned_scopes", [])),
        "created_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "created_by": _principal.subject,
        "read_only": payload.get("read_only", True),  # Default: read-only access
    }
    store.partner_allocations[allocation_id] = allocation
    
    # Also update partner's assigned_clients
    if "assigned_clients" not in partner:
        partner["assigned_clients"] = []
    if client_id not in partner["assigned_clients"]:
        partner["assigned_clients"].append(client_id)
    store.partners[partner_id] = partner
    
    record_integration_audit("allocation.created", allocation_id, _principal, {
        "partner_id": partner_id,
        "client_id": client_id,
    })
    
    return {
        "allocation_id": allocation_id,
        "partner_id": partner_id,
        "client_id": client_id,
        "status": "active",
        "scopes": allocation["scopes"],
        "created_at": allocation["created_at"],
    }


@router.get("/partners/{partner_id}/allocations")
def list_partner_allocations(
    partner_id: str,
    _principal: Principal = Depends(require_roles("ops_admin", "customer_success")),
) -> dict[str, Any]:
    """List all clients/facilities a partner has been allocated access to."""
    partner = store.partners.get(partner_id)
    if not partner:
        raise HTTPException(status_code=404, detail="partner not found")
    
    items = [
        a for a in store.partner_allocations.values()
        if a.get("partner_id") == partner_id
    ]
    return {"items": items, "partner_id": partner_id}


@router.patch("/partners/{partner_id}/allocations/{allocation_id}")
def update_partner_allocation(
    partner_id: str,
    allocation_id: str,
    payload: dict[str, Any],
    _principal: Principal = Depends(require_roles("ops_admin", "customer_success")),
) -> dict[str, Any]:
    """Revoke, modify scopes, or change read_only flag for an allocation."""
    allocation = store.partner_allocations.get(allocation_id)
    if not allocation or allocation.get("partner_id") != partner_id:
        raise HTTPException(status_code=404, detail="allocation not found")
    
    allocation["status"] = payload.get("status", allocation["status"])
    if "scopes" in payload:
        allocation["scopes"] = payload["scopes"]
    if "read_only" in payload:
        allocation["read_only"] = payload["read_only"]
    
    store.partner_allocations[allocation_id] = allocation
    record_integration_audit("allocation.updated", allocation_id, _principal, {
        "partner_id": partner_id,
        "status": allocation["status"],
    })
    
    return allocation


# ============================================================================
# Integration Audit & Usage Tracking
# ============================================================================

@router.get("/partners/{partner_id}/usage")
def get_partner_usage(
    partner_id: str,
    start_date: str | None = None,
    end_date: str | None = None,
    _principal: Principal = Depends(require_roles("ops_admin", "customer_success")),
) -> dict[str, Any]:
    """
    Get API usage stats and audit logs for a partner.
    
    Includes:
    - API calls made (by key_id, endpoint, status)
    - Webhook deliveries (success/failure/retry)
    - Data accessed (by resource type)
    """
    partner = store.partners.get(partner_id)
    if not partner:
        raise HTTPException(status_code=404, detail="partner not found")
    
    audit_events = [
        e for e in store.integration_audit_logs.values()
        if e.get("partner_id") == partner_id
    ]
    
    return {
        "partner_id": partner_id,
        "audit_events": audit_events[-100:],  # Last 100 events
        "summary": {
            "total_events": len(audit_events),
            "api_keys": len([k for k in store.partner_api_keys.values() if k.get("partner_id") == partner_id]),
            "allocations": len([a for a in store.partner_allocations.values() if a.get("partner_id") == partner_id]),
            "webhooks": len([w for w in store.partner_webhooks.values() if w.get("partner_id") == partner_id]),
        },
    }


def record_integration_audit(
    action: str,
    resource_id: str,
    principal: Principal,
    metadata: dict[str, Any],
) -> None:
    """Internal helper to record integration audit events."""
    audit_id = store.make_id("audit")
    audit_event = {
        "audit_id": audit_id,
        "action": action,
        "resource_id": resource_id,
        "partner_id": metadata.get("partner_id"),
        "actor": principal.subject,
        "actor_roles": list(principal.roles),
        "timestamp": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "metadata": metadata,
    }
    store.integration_audit_logs[audit_id] = audit_event
