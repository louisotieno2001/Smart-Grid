# Partner Integration API Guide

## Overview

The Energy Allocation Platform provides a comprehensive Partner Integration API that enables authorized third-party entities to build applications and services on top of the platform. This guide covers API key management, webhook integration, client access allocation, and best practices for third-party integrations.

## Table of Contents

1. [Authentication](#authentication)
2. [Partner Registration](#partner-registration)
3. [API Key Management](#api-key-management)
4. [Partner Allocation](#partner-allocation)
5. [Webhook Integration](#webhook-integration)
6. [Usage & Audit Tracking](#usage--audit-tracking)
7. [Scopes & Permissions](#scopes--permissions)
8. [Security Best Practices](#security-best-practices)
9. [Rate Limiting](#rate-limiting)
10. [Example Integrations](#example-integrations)

---

## Authentication

### API Key Authentication

All partner API requests must include a valid API key in the `X-API-Key` header:

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
     https://api.energyallocation.com/v1/facilities/fac_xxxxx
```

### Key Components

- **Key ID**: Identifies the key (e.g., `key_a1b2c3d4`)
- **Secret**: 256-bit URL-safe base64 string (shown only once at creation)
- **Scopes**: Define what the key can access (read:facilities, write:recommendations, etc.)
- **Expiration**: All keys expire after 90 days and must be rotated

### Request Signature Verification

All API requests are logged and verified. The system tracks:
- Which key was used
- IP address of the request
- Timestamp
- Resource accessed
- Action performed (read/write)

---

## Partner Registration

### Register a New Partner

**Only internal users (ops_admin, customer_success) can register partners.**

```bash
POST /v1/integrations/partners
Authorization: Bearer {INTERNAL_JWT_TOKEN}
Content-Type: application/json

{
  "name": "Energy Analytics Corp",
  "industry": "SaaS",
  "contact_email": "api-team@energyanalytics.com",
  "contact_name": "Sarah Chen",
  "scopes": ["read:facilities", "read:recommendations", "write:webhooks"],
  "assigned_clients": ["cli_001", "cli_002"]
}
```

**Response (201 Created)**

```json
{
  "partner_id": "ptn_a1b2c3d4",
  "status": "active",
  "created_at": "2026-03-24T21:15:00Z",
  "next_step": "Create API key via POST /v1/integrations/partners/ptn_a1b2c3d4/keys"
}
```

### Get Partner Details

```bash
GET /v1/integrations/partners/{partner_id}
Authorization: Bearer {INTERNAL_JWT_TOKEN}
```

### List All Partners

```bash
GET /v1/integrations/partners?status=active&limit=50
Authorization: Bearer {INTERNAL_JWT_TOKEN}
```

### Update Partner

```bash
PATCH /v1/integrations/partners/{partner_id}
Authorization: Bearer {INTERNAL_JWT_TOKEN}
Content-Type: application/json

{
  "status": "active",
  "assigned_clients": ["cli_001", "cli_002", "cli_003"],
  "assigned_scopes": ["read:facilities", "read:recommendations"]
}
```

---

## API Key Management

### Create API Key

Once a partner is registered, create API keys for authentication:

```bash
POST /v1/integrations/partners/{partner_id}/keys
Authorization: Bearer {INTERNAL_JWT_TOKEN}
Content-Type: application/json

{
  "name": "Production Key - Q1 2026",
  "scopes": ["read:facilities", "read:recommendations", "write:webhooks"]
}
```

**Response (201 Created)**

```json
{
  "key_id": "key_a1b2c3d4",
  "secret": "Kv3Q7pL8jW9_aB4cD5eF6gH7iJ8kL-M",
  "partner_id": "ptn_a1b2c3d4",
  "scopes": ["read:facilities", "read:recommendations", "write:webhooks"],
  "created_at": "2026-03-24T21:15:00Z",
  "expires_at": "2026-06-22T21:15:00Z",
  "warning": "Store the secret securely. It will not be shown again. Rotate every 90 days."
}
```

**IMPORTANT**: The secret is only shown once. Store it securely (e.g., in environment variables, secrets manager, or encrypted configuration).

### List Partner Keys

```bash
GET /v1/integrations/partners/{partner_id}/keys?status=active
Authorization: Bearer {INTERNAL_JWT_TOKEN}
```

**Response**

```json
{
  "items": [
    {
      "key_id": "key_a1b2c3d4",
      "partner_id": "ptn_a1b2c3d4",
      "name": "Production Key - Q1 2026",
      "scopes": ["read:facilities", "read:recommendations"],
      "status": "active",
      "created_at": "2026-03-24T21:15:00Z",
      "expires_at": "2026-06-22T21:15:00Z",
      "last_used_at": "2026-03-24T21:50:00Z"
    }
  ]
}
```

### Rotate API Key

Rotate a key to generate a new secret while revoking the old one:

```bash
PATCH /v1/integrations/partners/{partner_id}/keys/{key_id}
Authorization: Bearer {INTERNAL_JWT_TOKEN}
Content-Type: application/json

{
  "action": "rotate"
}
```

**Response (200 OK)**

```json
{
  "key_id": "key_b2c3d4e5",
  "secret": "Mv4R8qM9kX0_bC5dE6fG7hI8jK9lM-N",
  "partner_id": "ptn_a1b2c3d4",
  "scopes": ["read:facilities", "read:recommendations"],
  "created_at": "2026-03-24T21:20:00Z",
  "expires_at": "2026-06-22T21:20:00Z",
  "warning": "Store the secret securely. It will not be shown again."
}
```

### Revoke API Key

Immediately deactivate a key (cannot be used for authentication):

```bash
PATCH /v1/integrations/partners/{partner_id}/keys/{key_id}
Authorization: Bearer {INTERNAL_JWT_TOKEN}
Content-Type: application/json

{
  "action": "revoke"
}
```

**Response (200 OK)**

```json
{
  "key_id": "key_a1b2c3d4",
  "status": "revoked"
}
```

---

## Partner Allocation

Partners must be explicitly allocated access to client data. Allocations define:
- Which clients the partner can access
- Which scopes apply (read vs. write)
- Read-only vs. read-write permissions

### Assign Partner to Client

```bash
POST /v1/integrations/partners/{partner_id}/allocations
Authorization: Bearer {INTERNAL_JWT_TOKEN}
Content-Type: application/json

{
  "client_id": "cli_001",
  "scopes": ["read:facilities", "read:recommendations"],
  "read_only": true
}
```

**Response (201 Created)**

```json
{
  "allocation_id": "alloc_a1b2c3d4",
  "partner_id": "ptn_a1b2c3d4",
  "client_id": "cli_001",
  "status": "active",
  "scopes": ["read:facilities", "read:recommendations"],
  "created_at": "2026-03-24T21:15:00Z"
}
```

### List Partner Allocations

```bash
GET /v1/integrations/partners/{partner_id}/allocations
Authorization: Bearer {INTERNAL_JWT_TOKEN}
```

### Update Allocation

Modify scopes or revoke access:

```bash
PATCH /v1/integrations/partners/{partner_id}/allocations/{allocation_id}
Authorization: Bearer {INTERNAL_JWT_TOKEN}
Content-Type: application/json

{
  "status": "revoked",
  "scopes": ["read:facilities"]
}
```

---

## Webhook Integration

Partners can register webhooks to receive real-time notifications of events within their allocated clients.

### Create Webhook

```bash
POST /v1/integrations/partners/{partner_id}/webhooks
Authorization: Bearer {INTERNAL_JWT_TOKEN}
Content-Type: application/json

{
  "url": "https://yourapi.example.com/webhooks/energy-allocation",
  "description": "Receive facility and recommendation updates",
  "events": [
    "connector.sync_failed",
    "connector.sync_succeeded",
    "ingestion.import_completed",
    "model.run_completed",
    "recommendation.created",
    "recommendation.accepted",
    "drift.detected",
    "savings.realized_update"
  ],
  "max_retries": 5,
  "backoff_seconds": 60
}
```

**Response (201 Created)**

```json
{
  "webhook_id": "whp_a1b2c3d4",
  "partner_id": "ptn_a1b2c3d4",
  "status": "active",
  "created_at": "2026-03-24T21:15:00Z",
  "url": "https://yourapi.example.com/webhooks/energy-allocation",
  "events": [
    "connector.sync_failed",
    "ingestion.import_completed",
    "model.run_completed",
    "recommendation.created"
  ]
}
```

### Webhook Event Structure

All webhook payloads are signed with HMAC-SHA256 using the partner's API key secret. Include the signature header for verification:

**Headers**
```
X-Webhook-ID: whp_a1b2c3d4
X-Signature-Algorithm: hmac-sha256
X-Signature: sha256=abcdef123456...
X-Event-Type: recommendation.created
X-Timestamp: 2026-03-24T21:15:00Z
```

**Payload** (Example: `recommendation.created` event)

```json
{
  "event_id": "evt_a1b2c3d4",
  "event_type": "recommendation.created",
  "timestamp": "2026-03-24T21:15:00Z",
  "data": {
    "recommendation_id": "rec_x1y2z3a4",
    "facility_id": "fac_xxxxx",
    "client_id": "cli_001",
    "title": "Optimize compressor scheduling",
    "description": "Switch to lower-load scheduling during peak price periods",
    "estimated_savings_eur": 1200.00,
    "confidence": 0.92,
    "implementation_effort": "medium",
    "created_at": "2026-03-24T21:15:00Z"
  }
}
```

### Verify Webhook Signature

```python
import hmac
import hashlib

def verify_webhook(secret: str, payload: bytes, signature: str) -> bool:
    expected = "sha256=" + hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)
```

### Update Webhook

```bash
PATCH /v1/integrations/partners/{partner_id}/webhooks/{webhook_id}
Authorization: Bearer {INTERNAL_JWT_TOKEN}
Content-Type: application/json

{
  "url": "https://api2.example.com/webhooks/energy",
  "events": ["recommendation.created", "recommendation.accepted"],
  "status": "active"
}
```

### List Partner Webhooks

```bash
GET /v1/integrations/partners/{partner_id}/webhooks
Authorization: Bearer {INTERNAL_JWT_TOKEN}
```

---

## Usage & Audit Tracking

### Get Partner Usage Statistics

```bash
GET /v1/integrations/partners/{partner_id}/usage?start_date=2026-03-01&end_date=2026-03-31
Authorization: Bearer {INTERNAL_JWT_TOKEN}
```

**Response**

```json
{
  "partner_id": "ptn_a1b2c3d4",
  "summary": {
    "total_events": 1247,
    "api_keys": 2,
    "allocations": 3,
    "webhooks": 2
  },
  "audit_events": [
    {
      "audit_id": "audit_xxx",
      "action": "api_key.created",
      "resource_id": "key_a1b2c3d4",
      "partner_id": "ptn_a1b2c3d4",
      "actor": "user@company.com",
      "actor_roles": ["customer_success"],
      "timestamp": "2026-03-24T21:15:00Z",
      "metadata": {}
    }
  ]
}
```

### Audit Events

All partner actions are logged:

- `partner.registered` — New partner onboarded
- `partner.updated` — Partner metadata changed
- `api_key.created` — API key generated
- `api_key.rotated` — API key rotated
- `api_key.revoked` — API key deactivated
- `allocation.created` — Partner assigned to client
- `allocation.updated` — Allocation modified or revoked
- `webhook.created` — Webhook registered
- `webhook.updated` — Webhook configuration changed

---

## Scopes & Permissions

### Available Scopes

| Scope | Description | Resource Types |
|-------|-------------|-----------------|
| `read:facilities` | Read facility data | Facilities, connectors, appliances |
| `read:imports` | Read import history and status | Import jobs, data quality |
| `read:models` | Read model run details | Model runs, metrics |
| `read:recommendations` | Read recommendations | Recommendations, implementation status |
| `read:drift` | Read drift events | Drift detection, severity |
| `read:savings` | Read realized savings | Savings tracking, ROI |
| `write:webhooks` | Create/update webhooks | Webhook subscriptions |
| `write:recommendations` | Accept/reject recommendations | Recommendation decisions |
| `admin:partner` | Full partner admin access | All partner endpoints |

### Scope Combinations

- **Read-Only Analytics**: `read:facilities read:models read:recommendations read:savings`
- **Recommendation Engine**: `read:facilities read:recommendations write:recommendations`
- **Real-Time Integration**: `read:facilities read:recommendations write:webhooks`
- **Full Integration**: All scopes (only for trusted partners)

---

## Security Best Practices

### API Key Security

1. **Store Securely**: Use environment variables, secrets managers, or encrypted config
2. **Rotation**: Rotate keys every 90 days (keys auto-expire)
3. **Scope Limitation**: Use minimal scopes required for your integration
4. **IP Whitelisting**: For machine-to-machine integrations, request IP allowlisting
5. **Monitoring**: Monitor audit logs for unauthorized access

### Webhook Security

1. **HTTPS Only**: All webhook URLs must use HTTPS
2. **Signature Verification**: Always verify `X-Signature` header
3. **Timeout Handling**: Implement request timeouts (default: 30 seconds)
4. **Replay Protection**: Verify `X-Timestamp` is recent (within 5 minutes)
5. **Retry Logic**: Implement exponential backoff for failed webhooks

### Request Validation

```python
import hashlib
import hmac
import json
from datetime import datetime, timedelta

def validate_webhook(request_body: str, headers: dict, secret: str) -> bool:
    # Verify signature
    expected_sig = "sha256=" + hmac.new(
        secret.encode(),
        request_body.encode(),
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(headers.get("X-Signature", ""), expected_sig):
        return False
    
    # Verify timestamp (prevent replay attacks)
    timestamp = headers.get("X-Timestamp")
    event_time = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    if datetime.now(timezone.utc) - event_time > timedelta(minutes=5):
        return False
    
    return True
```

---

## Rate Limiting

All partner APIs are rate-limited based on subscription tier:

| Tier | Requests/Minute | Requests/Day | Concurrent |
|------|-----------------|--------------|-----------|
| Starter | 60 | 10,000 | 5 |
| Growth | 300 | 100,000 | 25 |
| Enterprise | Unlimited | Unlimited | Unlimited |

Rate limit headers are included in all responses:

```
X-RateLimit-Limit: 300
X-RateLimit-Remaining: 287
X-RateLimit-Reset: 1711294500
```

---

## Example Integrations

### Example 1: Energy Recommendation Dashboard

A SaaS analytics platform that pulls facility data and recommendations:

```python
import os
import requests
from datetime import datetime

API_KEY = os.getenv("EA_API_KEY")
API_BASE = "https://api.energyallocation.com"

def get_partner_facilities():
    """List all facilities the partner has access to."""
    response = requests.get(
        f"{API_BASE}/v1/clients/cli_001/facilities",
        headers={"X-API-Key": API_KEY}
    )
    return response.json()["items"]

def get_active_recommendations(facility_id: str):
    """Get active recommendations for a facility."""
    response = requests.get(
        f"{API_BASE}/v1/facilities/{facility_id}/recommendations?status=active",
        headers={"X-API-Key": API_KEY}
    )
    return response.json()["items"]

def accept_recommendation(facility_id: str, rec_id: str, decision_note: str):
    """Accept a recommendation and log the decision."""
    response = requests.post(
        f"{API_BASE}/v1/facilities/{facility_id}/recommendations/{rec_id}/decision",
        json={"status": "accepted", "note": decision_note},
        headers={"X-API-Key": API_KEY}
    )
    return response.json()

# Main workflow
facilities = get_partner_facilities()
for fac in facilities:
    recs = get_active_recommendations(fac["facility_id"])
    for rec in recs:
        if rec["confidence"] > 0.85:
            accept_recommendation(
                fac["facility_id"],
                rec["recommendation_id"],
                "Auto-accepted: High confidence recommendation"
            )
```

### Example 2: Webhook-Based Real-Time Monitoring

A monitoring service that receives drift alerts via webhooks:

```python
from fastapi import FastAPI, Header, Request, HTTPException
import hmac
import hashlib
import json
from datetime import datetime, timezone, timedelta

app = FastAPI()
WEBHOOK_SECRET = "your_api_key_secret"

@app.post("/webhooks/drift-detection")
async def handle_drift_webhook(
    request: Request,
    x_signature: str = Header(...),
    x_timestamp: str = Header(...)
):
    body = await request.body()
    
    # Verify signature
    expected = "sha256=" + hmac.new(
        WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(x_signature, expected):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Verify timestamp (prevent replay)
    event_time = datetime.fromisoformat(x_timestamp.replace("Z", "+00:00"))
    if datetime.now(timezone.utc) - event_time > timedelta(minutes=5):
        raise HTTPException(status_code=401, detail="Timestamp too old")
    
    # Process event
    event = json.loads(body)
    print(f"Drift detected in facility {event['data']['facility_id']}")
    print(f"Severity: {event['data']['severity']}")
    print(f"Action needed: Review model retraining strategy")
    
    return {"status": "received"}
```

---

## Support & Documentation

- **API Reference**: Available at `https://api.energyallocation.com/docs`
- **OpenAPI Spec**: `https://api.energyallocation.com/openapi.v1.yaml`
- **Issues & Questions**: Contact integration-support@energyallocation.com
- **SLA**: Enterprise SLA with 99.95% uptime guarantee

---

## Change Log

### Version 1.0.0 (March 2026)
- Initial partner integration API release
- API key management with automatic expiration
- Webhook integration with HMAC-SHA256 signing
- Partner allocation and scope-based access control
- Full audit logging and usage tracking
