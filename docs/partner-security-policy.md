# Partner Integration Security Policy

## Introduction

This document outlines the security requirements and best practices for third-party partners integrating with the Energy Allocation Platform. Partners must comply with these policies to maintain secure, auditable, and compliant integrations.

---

## 1. Authentication & Authorization

### 1.1 API Key Management

**Requirements:**
- All API requests must include a valid API key via `X-API-Key` header
- API keys are automatically issued with 90-day expiration
- Keys expire immediately upon revocation
- Partners must rotate keys every 90 days (enforced by expiration)
- No API key should ever be committed to version control

**Implementation:**
```bash
# DO: Store API key in environment variable
export EA_API_KEY="key_xxxxx:secret_yyyyy"

# DO: Include in request headers
curl -H "X-API-Key: $EA_API_KEY" https://api.energyallocation.com/v1/facilities

# DON'T: Hard-code in application
const apiKey = "key_xxxxx:secret_yyyyy";  // ❌ NEVER DO THIS
```

### 1.2 Scope-Based Access

Partners are granted specific scopes that define their access:

```
read:facilities         - View facility data
read:imports           - View import job status
read:models            - View model run results
read:recommendations   - View recommendations
read:drift             - View drift detection events
read:savings           - View realized savings
write:webhooks         - Create/manage webhooks
write:recommendations  - Accept/reject recommendations
admin:partner          - Full partner admin (rarely granted)
```

**Policy:**
- Request minimum necessary scopes for your use case
- Scopes are enforced at API request time
- Requests outside granted scopes are rejected with HTTP 403
- Scope violations are logged and audited

---

## 2. Data Security

### 2.1 Encryption in Transit

**Requirements:**
- All requests must use HTTPS (TLS 1.2+)
- HTTP requests are automatically rejected
- Certificate pinning recommended for machine-to-machine integrations
- All webhook endpoints must use HTTPS

**Verification:**
```bash
# Verify SSL/TLS
curl -v https://api.energyallocation.com/health

# Should return: < HTTP/2 200
```

### 2.2 Data at Rest

- All tenant data is encrypted at rest using AES-256
- Encryption keys are managed by AWS KMS
- Partners cannot access encryption keys
- Backups are encrypted with the same key material

### 2.3 Data Isolation

- Multi-tenant database ensures complete data isolation
- Row-level security (RLS) policies enforce tenant boundaries
- Partners can only access data from allocated clients
- Cross-client data queries are impossible by design

---

## 3. Webhook Security

### 3.1 Signature Verification

All webhook payloads are signed with HMAC-SHA256 using the partner's API key secret.

**Signature Algorithm:**
```
X-Signature: sha256={HMAC-SHA256(payload, api_key_secret)}
```

**Verification Python Code:**
```python
import hmac
import hashlib

def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify webhook signature."""
    # Extract algorithm and hash from signature header
    algo, hash_value = signature.split("=")
    
    if algo != "sha256":
        return False
    
    # Compute expected signature
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    # Use constant-time comparison
    return hmac.compare_digest(hash_value, expected)
```

**Verification Node.js Code:**
```javascript
import crypto from "crypto";

function verifySignature(payload, signature, secret) {
  const [algo, hash] = signature.split("=");
  
  if (algo !== "sha256") return false;
  
  const expected = crypto
    .createHmac("sha256", secret)
    .update(payload)
    .digest("hex");
  
  return crypto.timingSafeEqual(
    Buffer.from(hash),
    Buffer.from(expected)
  );
}
```

### 3.2 Replay Attack Prevention

Each webhook request includes a timestamp header. Partners must:

1. Verify the timestamp is recent (within 5 minutes)
2. Track received event IDs to prevent duplicate processing
3. Use idempotency keys for all write operations

```python
from datetime import datetime, timezone, timedelta

def is_valid_timestamp(timestamp_str: str, max_age_seconds: int = 300) -> bool:
    """Check if timestamp is recent enough."""
    event_time = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
    age = (datetime.now(timezone.utc) - event_time).total_seconds()
    return 0 <= age <= max_age_seconds
```

### 3.3 Webhook Retry Policy

- Webhooks are retried up to `max_retries` times (default: 3)
- Exponential backoff: 60s, 120s, 240s
- Partners can configure retry policy when creating webhooks
- Failed webhooks after all retries are logged in usage/audit

---

## 4. Request & Rate Limiting

### 4.1 Rate Limits by Tier

| Tier | Requests/Min | Requests/Day | Burst |
|------|--------------|--------------|-------|
| Starter | 60 | 10,000 | 100 |
| Growth | 300 | 100,000 | 500 |
| Enterprise | Unlimited | Unlimited | Unlimited |

**Headers:**
```
X-RateLimit-Limit: 300          # Your limit
X-RateLimit-Remaining: 287      # Remaining this minute
X-RateLimit-Reset: 1711294500   # Unix timestamp when limit resets
```

**Handling Rate Limits:**
```python
import time

def make_api_request(url, key, max_retries=3):
    for attempt in range(max_retries):
        response = requests.get(
            url,
            headers={"X-API-Key": key}
        )
        
        if response.status_code == 429:  # Rate limited
            reset_time = int(response.headers["X-RateLimit-Reset"])
            wait_seconds = reset_time - time.time()
            print(f"Rate limited. Waiting {wait_seconds}s...")
            time.sleep(max(1, wait_seconds))
            continue
        
        return response
    
    raise Exception("Failed after retries")
```

### 4.2 Idempotency

All write operations (`POST`, `PATCH`) should include an `Idempotency-Key` header:

```bash
curl -X POST https://api.energyallocation.com/v1/integrations/partners/ptn_xxx/keys \
  -H "Idempotency-Key: partner-key-creation-20260324" \
  -H "X-API-Key: key_xxx" \
  -H "Content-Type: application/json" \
  -d '{"name": "prod key"}'
```

**Benefits:**
- Prevents duplicate resource creation on network retries
- Safe to retry requests without creating duplicates
- Idempotency key must be a unique, stable identifier

---

## 5. Audit & Monitoring

### 5.1 Audit Logging

All partner actions are logged:

- Partner registration/updates
- API key creation/rotation/revocation
- Allocation creation/changes
- Webhook registration/updates
- Data access (read/write)
- Failed authentication attempts
- Rate limit violations

**Access Audit Logs:**
```bash
GET /v1/integrations/partners/{partner_id}/usage
Authorization: Bearer {INTERNAL_TOKEN}
```

### 5.2 Monitoring Best Practices

**For Partners:**
- Monitor webhook delivery success/failure rates
- Track API response times and error rates
- Set up alerts for authentication failures
- Monitor data freshness in your systems

**For Platform Operators:**
- Monitor partner API key usage patterns
- Alert on unusual access patterns
- Track per-partner quota consumption
- Monitor webhook delivery failures

---

## 6. Incident Response

### 6.1 Suspected Compromise

If you suspect an API key has been compromised:

1. **Immediately revoke the key:**
   ```bash
   PATCH /v1/integrations/partners/{partner_id}/keys/{key_id}
   Authorization: Bearer {INTERNAL_TOKEN}
   Content-Type: application/json
   
   {"action": "revoke"}
   ```

2. **Rotate to a new key:**
   ```bash
   PATCH /v1/integrations/partners/{partner_id}/keys/{key_id}
   Authorization: Bearer {INTERNAL_TOKEN}
   
   {"action": "rotate"}
   ```

3. **Review audit logs:**
   ```bash
   GET /v1/integrations/partners/{partner_id}/usage
   Authorization: Bearer {INTERNAL_TOKEN}
   ```

4. **Contact support:** incident-response@energyallocation.com

### 6.2 Reporting Security Issues

Report security vulnerabilities to: **security@energyallocation.com**

Do NOT publicly disclose security issues. We take security seriously and will:
- Acknowledge receipt within 24 hours
- Provide updates every 48 hours
- Credit your discovery if appropriate

---

## 7. Compliance & Legal

### 7.1 Data Processing Agreement

Partners must sign a Data Processing Agreement (DPA) before accessing production data.

**Key Terms:**
- Partners are Data Processors (customer is Data Controller)
- Partners must not transfer data outside the EU without agreement
- Partners must implement reasonable security measures
- Partners grant us audit rights

### 7.2 Data Retention

- Partners should not retain customer data longer than necessary
- Implement data deletion policies aligned with your service SLA
- Delete data immediately upon customer request or contract termination

### 7.3 Regulatory Compliance

Partners must comply with applicable regulations:
- **GDPR** (EU customers)
- **CCPA** (California customers)
- **HIPAA** (if applicable to your industry)
- **SOC 2** compliance for handling sensitive data

---

## 8. Development Best Practices

### 8.1 Secret Management

```python
# ✅ GOOD: Use environment variables
import os
api_key = os.getenv("EA_API_KEY")

# ✅ GOOD: Use secrets manager
from aws_secretsmanager_python import client
secret = client.get_secret_value(SecretId="ea-api-key")

# ❌ BAD: Hard-coded secrets
api_key = "key_xxxxx:secret_yyyyy"

# ❌ BAD: Committed to git
# .env file with secrets should be in .gitignore
```

### 8.2 Error Handling

```python
import requests

def call_api(endpoint, key):
    try:
        response = requests.get(
            endpoint,
            headers={"X-API-Key": key},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.Timeout:
        # Log and retry
        print(f"API timeout. Retrying...")
    
    except requests.exceptions.HTTPError as e:
        # Log error details, DON'T log full response (might contain secrets)
        print(f"API error: {e.response.status_code}")
        
        if e.response.status_code == 401:
            # Check if API key is still valid
            pass
        elif e.response.status_code == 403:
            # Check scope permissions
            pass
        elif e.response.status_code == 429:
            # Rate limited - implement backoff
            pass
```

### 8.3 Dependency Security

```bash
# Scan dependencies for vulnerabilities
pip install pip-audit
pip-audit

# Update dependencies regularly
pip install --upgrade pip

# Lock dependency versions in production
pip freeze > requirements.lock
```

---

## 9. Checklist for Integration Launch

- [ ] API keys stored securely (environment variables, secrets manager)
- [ ] HTTPS only - no HTTP requests
- [ ] Webhook signatures verified on every request
- [ ] Webhook timestamps validated (within 5 minutes)
- [ ] Idempotency keys included on all write operations
- [ ] Rate limiting handled with exponential backoff
- [ ] Audit logs reviewed for your partner account
- [ ] Error handling implemented (timeouts, retries, logging)
- [ ] Dependencies scanned for vulnerabilities
- [ ] DPA signed (production access)
- [ ] Security incident response plan documented
- [ ] Monitoring/alerts configured for your webhook endpoints

---

## 10. Support & Escalation

**Emergency Security Issues:**
- Email: security@energyallocation.com
- Phone: +1-555-0123 (24/7 security hotline)

**API Support:**
- Email: integration-support@energyallocation.com
- Docs: https://docs.energyallocation.com/integrations
- Status: https://status.energyallocation.com

**SLA for Support:**
- Starter: 24-hour response
- Growth: 4-hour response
- Enterprise: 1-hour response

---

**Last Updated:** March 2026
**Version:** 1.0.0
