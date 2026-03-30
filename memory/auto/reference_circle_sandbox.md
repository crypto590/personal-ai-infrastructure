---
name: reference_circle_sandbox
description: Circle Programmable Wallets sandbox - API details, testnet chains, entity secret registration, faucet usage
type: reference
---

Circle Programmable Wallets sandbox is configured and tested (2026-03-27).

**API Details:**
- Base URL: `https://api.circle.com` (same for testnet and mainnet)
- Auth: Bearer token with API key format `TEST_API_KEY:id:secret`
- Entity secret: RSA-OAEP SHA-256 encryption with Circle's public key (NOT AES-GCM)
- Public key endpoint: `GET /v1/w3s/config/entity/publicKey` (returns PKCS8 PEM)
- Ciphertext must be exactly 684 base64 characters, fresh per request

**API Path Pattern:**
- POST (mutations): `/v1/w3s/developer/...` (walletSets, wallets, transactions/transfer)
- GET (reads): `/v1/w3s/...` (wallets, wallets/{id}/balances, transactions/{id})

**Testnet Chains:**
ETH-SEPOLIA, SOL-DEVNET, BASE-SEPOLIA, MATIC-AMOY, ARB-SEPOLIA, AVAX-FUJI

**Entity Secret Registration:**
Console → Wallets → DEV CONTROLLED → Configurator → Entity Secret

**Faucet:**
- Console faucet at console.circle.com/faucet (requires reCAPTCHA, 5 req/24h)
- API faucet `/v1/faucet/drips` requires mainnet upgrade (returns 403 on testnet-only accounts)

**USDC Token (ETH-SEPOLIA):**
- Address: `0x1c7d4b196cb0c7b01d743fbc6116a902379c7238`
- Token ID: `5797fbd6-3795-519d-84ca-ec4c5f80c3b1`

**Test Harness:** `gateway/tests/circle_sandbox_test.mjs`
**Registration Script:** `gateway/tests/circle_register_secret.mjs`
