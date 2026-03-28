---
name: staging-api-deployment
description: All APIs are merged into a single users-api service when deployed to staging/production
type: project
---

All Athlead APIs (users-api, recruiting-api, email-api, livestream-api, athletics-api, notifications-api) are consolidated into a single deployed service (users-api) in staging and production. The separate ports (8000-8005) only apply in local development. Don't flag routing issues when staging requests hit users-api for non-users routes — that's expected.

**Why:** Deployment consolidation — fewer containers to manage.
**How to apply:** When debugging staging/production API issues, don't assume the wrong service is being hit based on the hostname. Focus on whether the route is registered and the code is deployed.
