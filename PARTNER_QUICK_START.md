# Partner Integration Quick Reference

## Getting Started in 5 Minutes

### What You Need
1. **API Key** — Request from your account manager
2. **Client ID(s)** — List of clients you have access to
3. **HTTPS client** — curl, Postman, or your language's HTTP library

### Quick Example

```bash
# 1. List your facilities
curl -H "X-API-Key: key_abc123" \
  https://api.energyallocation.com/v1/clients/your_client_id/facilities

# 2. Get active recommendations
curl -H "X-API-Key: key_abc123" \
  https://api.energyallocation.com/v1/facilities/fac_001/recommendations?status=active

# 3. Accept a recommendation
curl -X POST -H "X-API-Key: key_abc123" \
  -H "Content-Type: application/json" \
  https://api.energyallocation.com/v1/facilities/fac_001/recommendations/rec_001/decision \
  -d '{"status": "accepted", "note": "Good recommendation"}'
```

---

## Available Data Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v1/clients/{client_id}/facilities` | GET | List facilities |
| `/v1/facilities/{facility_id}/connectors` | GET | List data connectors |
| `/v1/facilities/{facility_id}/appliances` | GET | List appliances |
| `/v1/facilities/{facility_id}/recommendations` | GET | Get recommendations |
| `/v1/facilities/{facility_id}/alerts` | GET | Get alerts |
| `/v1/facilities/{facility_id}/drift-events` | GET | Get drift events |
| `/v1/facilities/{facility_id}/retraining-jobs` | GET | Get retraining jobs |

---

## Common Integration Patterns

### Pattern 1: Monitor Recommendations
```python
import requests
import time

api_key = "key_xxxxx"
base = "https://api.energyallocation.com"

while True:
    # Get recommendations
    r = requests.get(
        f"{base}/v1/facilities/fac_001/recommendations?status=active",
        headers={"X-API-Key": api_key}
    )
    recs = r.json()["items"]
    
    # Accept high-confidence ones
    for rec in recs:
        if rec["confidence"] > 0.9:
            requests.post(
                f"{base}/v1/facilities/{rec['facility_id']}/recommendations/{rec['recommendation_id']}/decision",
                json={"status": "accepted"},
                headers={"X-API-Key": api_key}
            )
    
    time.sleep(3600)  # Check hourly
```

### Pattern 2: Set Up Webhooks
```python
requests.post(
    f"{base}/v1/integrations/partners/{partner_id}/webhooks",
    json={
        "url": "https://yourapi.example.com/webhooks/energy",
        "events": ["recommendation.created", "drift.detected"],
    },
    headers={"Authorization": f"Bearer {internal_token}"}
)
```

Then on your server, verify webhook signatures:
```python
import hmac, hashlib

def verify(body, sig, secret):
    expected = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(sig, expected)
```

### Pattern 3: Sync Savings Data
```python
r = requests.get(
    f"{base}/v1/facilities/fac_001/savings",
    headers={"X-API-Key": api_key}
)
savings = r.json()

# Sync to your database
for facility_id, data in savings.items():
    db.update_savings(facility_id, data)
```

---

## Error Handling

### Common Status Codes
| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Continue |
| 201 | Created | Check response |
| 400 | Bad request | Check JSON format |
| 401 | Unauthorized | Verify API key |
| 403 | Forbidden | Check scopes/allocation |
| 404 | Not found | Verify resource ID |
| 429 | Rate limited | Wait, then retry |
| 500 | Server error | Retry in 60s |

### Retry Strategy
```python
import time

def call_api(url, key, max_retries=3):
    for attempt in range(max_retries):
        r = requests.get(url, headers={"X-API-Key": key})
        
        if r.status_code == 429:  # Rate limited
            wait = int(r.headers["X-RateLimit-Reset"]) - time.time()
            time.sleep(max(1, wait))
            continue
        
        if r.status_code >= 500:  # Server error
            time.sleep(2 ** attempt)
            continue
        
        return r
    
    raise Exception("Failed after retries")
```

---

## Rate Limits

| Plan | Per Minute | Per Day |
|------|-----------|---------|
| Starter | 60 | 10,000 |
| Growth | 300 | 100,000 |
| Enterprise | Unlimited | Unlimited |

**Check remaining quota** in response headers:
```
X-RateLimit-Limit: 300
X-RateLimit-Remaining: 287
X-RateLimit-Reset: 1711294500
```

---

## API Key Rotation

Your API key expires every 90 days. To rotate:

```bash
# 1. Get your old key ID
# 2. Create new key (ask your account manager)
# 3. Update your application with new key
# 4. Test thoroughly
# 5. Old key auto-revokes after 90 days
```

---

## Webhook Events

Your webhook receives these events:

```json
{
  "event_id": "evt_123",
  "event_type": "recommendation.created",
  "timestamp": "2026-03-24T21:00:00Z",
  "data": {
    "recommendation_id": "rec_abc",
    "facility_id": "fac_xyz",
    "title": "...",
    "confidence": 0.92,
    "estimated_savings_eur": 1200
  }
}
```

**Events you can subscribe to:**
- `recommendation.created` — New recommendation available
- ` recommendation.accepted` — Recommendation accepted
- `recommendation.rejected` — Recommendation rejected
- `drift.detected` — Model data drift detected
- `connector.sync_failed` — Data connector failed
- `model.run_completed` — Model training finished
- `savings.realized_update` — Realized savings updated

---

## Troubleshooting

### 401 Unauthorized
- Verify API key in request header: `X-API-Key: key_xxxxx`
- Check if key has expired (90 day rotation required)
- Confirm you're using HTTPS (not HTTP)

### 403 Forbidden
- Verify you have access to this `client_id`
- Check API key scopes match your requested action
- Internal endpoints require JWT token, not API key

### 404 Not Found
- Verify `facility_id`, `client_id`, `recommendation_id` are correct
- Resource may have been deleted

### 429 Rate Limited
- Wait until `X-RateLimit-Reset` timestamp
- Implement exponential backoff
- Upgrade plan if consistently hitting limits

### 500 Server Error
- Likely temporary issue
- Retry with exponential backoff (1s, 2s, 4s, 8s)
- Contact support if persistent: support@energyallocation.com

---

## Support

| Channel | Latency | For |
|---------|---------|-----|
| Email: integration-support@energyallocation.com | 4-24h | General questions |
| Slack: #energy-alloc-partners | Real-time | Quick questions |
| Docs: docs.energyallocation.com | Instant | How-to guides |
| Issues: github.com/energyallocation/integration-issues | 24h | Bug reports |

---

## Example: Complete Integration (Python)

```python
#!/usr/bin/env python3
import os
import requests
import hmac
import hashlib
from datetime import datetime
from flask import Flask, request

API_KEY = os.getenv("EA_API_KEY")
WEBHOOK_SECRET = "your_partner_secret"
API_BASE = "https://api.energyallocation.com"
FACILITY_ID = "fac_001"

app = Flask(__name__)

# Pull data periodically
def sync_facilities():
    r = requests.get(
        f"{API_BASE}/v1/clients/cli_001/facilities",
        headers={"X-API-Key": API_KEY}
    )
    return r.json()["items"]

def get_recommendations(fac_id):
    r = requests.get(
        f"{API_BASE}/v1/facilities/{fac_id}/recommendations?status=active",
        headers={"X-API-Key": API_KEY}
    )
    return r.json()["items"]

# Receive webhook events
@app.route("/webhooks/energy", methods=["POST"])
def handle_webhook():
    # Verify signature
    sig = request.headers.get("X-Signature")
    expected = "sha256=" + hmac.new(
        WEBHOOK_SECRET.encode(),
        request.data,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(sig, expected):
        return {"error": "Invalid signature"}, 401
    
    event = request.json
    print(f"Got event: {event['event_type']}")
    
    # Process event
    if event['event_type'] == 'recommendation.created':
        print(f"New recommendation: {event['data']['title']}")
    
    return {"status": "ok"}, 200

if __name__ == "__main__":
    # Sync facilities every hour
    import threading
    import time
    
    def periodic_sync():
        while True:
            facilities = sync_facilities()
            for fac in facilities:
                recs = get_recommendations(fac['id'])
                print(f"Facility {fac['name']}: {len(recs)} active recommendations")
            time.sleep(3600)
    
    thread = threading.Thread(target=periodic_sync, daemon=True)
    thread.start()
    
    app.run(port=5000)
```

---

**Remember:**
- Always use HTTPS
- Store API keys securely (environment variables)
- Verify webhook signatures
- Implement retry logic with backoff
- Use idempotency keys on write operations

**More help:**
- Full API docs: https://api.energyallocation.com/docs
- Security guide: docs/partner-security-policy.md
- Questions: integration-support@energyallocation.com
