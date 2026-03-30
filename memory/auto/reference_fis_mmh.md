---
name: FIS MMH API reference
description: FIS Money Movement Hub integration details — UAT sandbox, auth, test harness, known sandbox issues
type: reference
---

FIS MMH Universal Payment Origination API integrated in `gateway/crates/tp-mmh/`.

**UAT Sandbox:** `https://api-gw-uat.fisglobal.com/api/money-movement-hub/universal-payments/v2`
**Portal:** FIS Developer Portal (app: test_mmh, environment: Sandbox)
**Auth:** OAuth2 Bearer JWT, 60-min TTL, generate from portal "Generate access token"
**Swagger spec:** `docs/D1-MMH-Universal-Payment-Origination (1).json`
**Integration doc:** `docs/FIS_MMH_INTEGRATION.md`
**Test harness:** `gateway/tests/mmh_sandbox_test.sh` with 21 fixtures in `gateway/tests/mmh_fixtures/`

**Sandbox headers:** `uuid` (v4), `organization-id` (example: D1B), `channel` (example: DIG-D1B-INT-BAT), `idempotency-key`

**Known sandbox issues (2026-03-28):**
- Credit-transfer 200 WireMock stub doesn't match — always returns canned 400 "uuid invalid"
- Debit-transfer CCD/PPD return 200 successfully
- Akamai WAF blocks payloads >~16KB (RTP/Supplementary-Data get 403)
- Rate limit: 50 req/min
