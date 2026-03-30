---
name: transit_sandbox
description: TransIT API 3.0 sandbox URLs, auth mechanism, test credentials, and developer portal reference
type: reference
---

TransIT API 3.0 (Global Payments / TSYS) sandbox setup completed.

**URLs:**
- UAT: `https://stagegw.transnox.com/servlets/Transnox_API_server`
- Production: `https://gateway.transit-pass.com/servlets/TransNox_API_Server`
- Developer Portal: `https://developerportal.transit-pass.com/developerportal/resources/dist/#/`
- Certification support: (888) 959-2017

**Auth mechanism:** deviceID + transactionKey in request body (NOT Bearer tokens)
- For JSON: set `user-agent: infonox` header
- For XML: set `Content-Type: text/xml` header

**Shared test credentials (may be locked, need own account):**
- MID: 888900000189, UserID: TA5776079, Password: Tsys@8889
- DeviceID: 76950000001101, DeveloperID: 1234567890

**How to apply:** The existing tp-transit client uses a WRONG API format (Bearer token auth, /transactions/authorize paths). It needs rewriting to match the actual TransIT API 3.0 format. Sandbox test harness is at `gateway/crates/tp-transit/tests/sandbox_harness.rs` and works independently of the old client.
