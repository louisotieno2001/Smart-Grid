# Author: Jerry Onyango
# Contribution: Smoke test for third-party partner integration APIs to verify authorization, API key management, webhook registration, and allocation workflows.
import os
import json

os.environ.setdefault("EA_ENV", "development")
os.environ.setdefault("EA_ENABLE_DEV_AUTH", "true")
os.environ.setdefault("EA_JWT_SECRET", "dev-secret-change-me-at-least-32-bytes")
os.environ.setdefault("EA_ALLOW_WEAK_JWT_SECRET", "false")
os.environ.setdefault("EA_DATABASE_URL", "postgresql://energyallocation:energyallocation@localhost:5432/energyallocation")
os.environ.setdefault("EA_STORE_BACKEND", "postgres")

from fastapi.testclient import TestClient
from energy_api.main import app

client = TestClient(app)

# ============================================================================
# Helper: Create internal auth token for ops_admin
# ============================================================================

ops_token = client.post(
    "/v1/auth/dev-token",
    json={"sub": "ops_admin_user", "roles": ["ops_admin"], "client_id": None},
).json()["access_token"]
ops_headers = {"Authorization": f"Bearer {ops_token}"}


# ============================================================================
# Test Suite: Partner Integration APIs
# ============================================================================

checks = []


# Test 1: Register a new partner
print("\n=== Test 1: Register Partner ===")
register_response = client.post(
    "/v1/integrations/partners",
    headers=ops_headers,
    json={
        "name": "EnergyTech Analytics",
        "industry": "SaaS",
        "contact_email": "api@energytech.com",
        "contact_name": "Sarah Chen",
        "scopes": ["read:facilities", "read:recommendations", "write:webhooks"],
    },
)
checks.append(("register_partner", register_response.status_code))
partner_id = register_response.json()["partner_id"]
print(f"✓ Partner registered: {partner_id}")


# Test 2: Get partner details
print("\n=== Test 2: Get Partner Details ===")
get_partner_response = client.get(
    f"/v1/integrations/partners/{partner_id}",
    headers=ops_headers,
)
checks.append(("get_partner", get_partner_response.status_code))
print(f"✓ Partner status: {get_partner_response.json()['status']}")


# Test 3: List all partners
print("\n=== Test 3: List Partners ===")
list_partners_response = client.get(
    "/v1/integrations/partners?status=active&limit=50",
    headers=ops_headers,
)
checks.append(("list_partners", list_partners_response.status_code))
print(f"✓ Total partners: {list_partners_response.json()['total']}")


# Test 4: Update partner
print("\n=== Test 4: Update Partner ===")
update_partner_response = client.patch(
    f"/v1/integrations/partners/{partner_id}",
    headers=ops_headers,
    json={
        "status": "active",
        "assigned_clients": ["cli_001", "cli_002"],
    },
)
checks.append(("update_partner", update_partner_response.status_code))
print(f"✓ Partner updated: {update_partner_response.json()['partner_id']}")


# Test 5: Create API key
print("\n=== Test 5: Create API Key ===")
create_key_response = client.post(
    f"/v1/integrations/partners/{partner_id}/keys",
    headers=ops_headers,
    json={
        "name": "Production Key Q1 2026",
        "scopes": ["read:facilities", "read:recommendations"],
    },
)
checks.append(("create_api_key", create_key_response.status_code))
key_data = create_key_response.json()
key_id = key_data["key_id"]
api_secret = key_data["secret"]
print(f"✓ API key created: {key_id}")
print(f"✓ Secret (store securely): {api_secret[:20]}...")


# Test 6: List API keys
print("\n=== Test 6: List API Keys ===")
list_keys_response = client.get(
    f"/v1/integrations/partners/{partner_id}/keys?status=active",
    headers=ops_headers,
)
checks.append(("list_api_keys", list_keys_response.status_code))
print(f"✓ API keys count: {len(list_keys_response.json()['items'])}")


# Test 7: Create webhook
print("\n=== Test 7: Create Webhook ===")
create_webhook_response = client.post(
    f"/v1/integrations/partners/{partner_id}/webhooks",
    headers=ops_headers,
    json={
        "url": "https://yourapi.example.com/webhooks/energy-data",
        "description": "Real-time facility and recommendation updates",
        "events": [
            "ingestion.import_completed",
            "model.run_completed",
            "recommendation.created",
            "drift.detected",
        ],
        "max_retries": 5,
        "backoff_seconds": 60,
    },
)
checks.append(("create_webhook", create_webhook_response.status_code))
webhook_id = create_webhook_response.json()["webhook_id"]
print(f"✓ Webhook registered: {webhook_id}")


# Test 8: List webhooks
print("\n=== Test 8: List Webhooks ===")
list_webhooks_response = client.get(
    f"/v1/integrations/partners/{partner_id}/webhooks",
    headers=ops_headers,
)
checks.append(("list_webhooks", list_webhooks_response.status_code))
print(f"✓ Webhooks count: {len(list_webhooks_response.json()['items'])}")


# Test 9: Update webhook
print("\n=== Test 9: Update Webhook ===")
update_webhook_response = client.patch(
    f"/v1/integrations/partners/{partner_id}/webhooks/{webhook_id}",
    headers=ops_headers,
    json={
        "url": "https://api2.example.com/webhooks/energy",
        "events": ["recommendation.created", "recommendation.accepted", "drift.detected"],
        "status": "active",
    },
)
checks.append(("update_webhook", update_webhook_response.status_code))
print(f"✓ Webhook updated: {update_webhook_response.json()['webhook_id']}")


# Test 10: Assign partner to client (allocation)
print("\n=== Test 10: Create Allocation ===")
create_allocation_response = client.post(
    f"/v1/integrations/partners/{partner_id}/allocations",
    headers=ops_headers,
    json={
        "client_id": "cli_001",
        "scopes": ["read:facilities", "read:recommendations"],
        "read_only": True,
    },
)
checks.append(("create_allocation", create_allocation_response.status_code))
allocation_id = create_allocation_response.json()["allocation_id"]
print(f"✓ Allocation created: {allocation_id}")


# Test 11: List allocations
print("\n=== Test 11: List Allocations ===")
list_allocations_response = client.get(
    f"/v1/integrations/partners/{partner_id}/allocations",
    headers=ops_headers,
)
checks.append(("list_allocations", list_allocations_response.status_code))
print(f"✓ Allocations count: {len(list_allocations_response.json()['items'])}")


# Test 12: Update allocation
print("\n=== Test 12: Update Allocation ===")
update_allocation_response = client.patch(
    f"/v1/integrations/partners/{partner_id}/allocations/{allocation_id}",
    headers=ops_headers,
    json={
        "status": "active",
        "scopes": ["read:facilities", "read:recommendations", "read:savings"],
    },
)
checks.append(("update_allocation", update_allocation_response.status_code))
print(f"✓ Allocation updated: {update_allocation_response.json()['allocation_id']}")


# Test 13: Rotate API key
print("\n=== Test 13: Rotate API Key ===")
rotate_key_response = client.patch(
    f"/v1/integrations/partners/{partner_id}/keys/{key_id}",
    headers=ops_headers,
    json={"action": "rotate"},
)
checks.append(("rotate_api_key", rotate_key_response.status_code))
new_key_data = rotate_key_response.json()
print(f"✓ API key rotated: {new_key_data['key_id']}")
print(f"✓ New secret (store securely): {new_key_data['secret'][:20]}...")


# Test 14: Get partner usage and audit logs
print("\n=== Test 14: Get Partner Usage ===")
usage_response = client.get(
    f"/v1/integrations/partners/{partner_id}/usage",
    headers=ops_headers,
)
checks.append(("get_partner_usage", usage_response.status_code))
usage_data = usage_response.json()
print(f"✓ Total audit events: {usage_data['summary']['total_events']}")
print(f"✓ API keys: {usage_data['summary']['api_keys']}")
print(f"✓ Allocations: {usage_data['summary']['allocations']}")
print(f"✓ Webhooks: {usage_data['summary']['webhooks']}")


# Test 15: Revoke API key
print("\n=== Test 15: Revoke API Key ===")
revoke_key_response = client.patch(
    f"/v1/integrations/partners/{partner_id}/keys/{new_key_data['key_id']}",
    headers=ops_headers,
    json={"action": "revoke"},
)
checks.append(("revoke_api_key", revoke_key_response.status_code))
print(f"✓ API key revoked: {revoke_key_response.json()['status']}")


# ============================================================================
# Print Results
# ============================================================================

print("\n" + "=" * 70)
print("PARTNER INTEGRATION API TEST RESULTS")
print("=" * 70)
print(json.dumps(checks, indent=2))

summary = {
    "partner_id": partner_id,
    "webhook_id": webhook_id,
    "allocation_id": allocation_id,
    "rotated_key_id": new_key_data["key_id"],
    "total_checks": len(checks),
    "passed_checks": sum(1 for _, status in checks if status in [200, 201]),
}
print(json.dumps(summary, indent=2))
