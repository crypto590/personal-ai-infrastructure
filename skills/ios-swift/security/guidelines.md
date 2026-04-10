# Security: Core Guidelines and Anti-Patterns

**Part of:** [ios-swift](../SKILL.md) > Security

Adapted from [ivan-magda/swift-security-skill](https://github.com/ivan-magda/swift-security-skill) (Ivan Magda, MIT).

Covers Keychain Services, biometric authentication, CryptoKit, Secure Enclave, credential storage, certificate trust, and OWASP compliance for iOS/macOS.

---

## Scope

**In scope:** Client-side Keychain, biometrics, CryptoKit, Secure Enclave, certificate trust, credential lifecycle.

**Out of scope:** ATS configuration, CloudKit security, server-side auth, jailbreak detection, third-party crypto libraries.

---

## 7 Non-Negotiable Rules

### 1. Never Ignore OSStatus

Every `SecItem*` call returns `OSStatus`. Always check it:

```swift
let status = SecItemAdd(query as CFDictionary, nil)
guard status == errSecSuccess else {
    throw KeychainError.unhandledError(status: status)
}
```

### 2. Never Use LAContext.evaluatePolicy() as Standalone Auth Gate

Biometric check alone is not authentication. Always bind biometrics to a Keychain item with access control:

```swift
let access = SecAccessControlCreateWithFlags(
    nil,
    kSecAttrAccessibleWhenPasscodeSetThisDeviceOnly,
    .biometryCurrentSet,
    nil
)

let query: [String: Any] = [
    kSecClass as String: kSecClassGenericPassword,
    kSecAttrService as String: "com.app.auth",
    kSecAttrAccount as String: "token",
    kSecAttrAccessControl as String: access!,
    kSecValueData as String: tokenData
]
```

### 3. Never Store Secrets in Unsafe Locations

**Forbidden:** UserDefaults, plist files, xcconfig files, NSCoding archives.

**Required:** Keychain Services (always).

### 4. Never Call SecItem* on @MainActor

Keychain operations can block. Always run off the main actor:

```swift
actor KeychainService {
    func store(key: String, data: Data) throws {
        // SecItemAdd runs on actor's executor, not main thread
    }
}
```

### 5. Always Set kSecAttrAccessible Explicitly

Never rely on the default. Choose the most restrictive option that works:

| Constant | When Available | Survives Backup |
|---|---|---|
| `kSecAttrAccessibleWhenPasscodeSetThisDeviceOnly` | Unlocked + passcode set | No |
| `kSecAttrAccessibleWhenUnlockedThisDeviceOnly` | Unlocked | No |
| `kSecAttrAccessibleWhenUnlocked` | Unlocked | Yes |
| `kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly` | After first unlock | No |
| `kSecAttrAccessibleAfterFirstUnlock` | After first unlock | Yes |

**Recommendation:** Use `WhenPasscodeSetThisDeviceOnly` for credentials, `AfterFirstUnlockThisDeviceOnly` for background-accessible tokens.

### 6. Always Use Add-or-Update Pattern

`SecItemAdd` fails if item exists. Always check and update:

```swift
func save(service: String, account: String, data: Data) throws {
    let query: [String: Any] = [
        kSecClass as String: kSecClassGenericPassword,
        kSecAttrService as String: service,
        kSecAttrAccount as String: account,
    ]

    let status = SecItemCopyMatching(query as CFDictionary, nil)

    switch status {
    case errSecSuccess:
        // Update existing
        let attributes: [String: Any] = [kSecValueData as String: data]
        let updateStatus = SecItemUpdate(query as CFDictionary, attributes as CFDictionary)
        guard updateStatus == errSecSuccess else {
            throw KeychainError.unhandledError(status: updateStatus)
        }
    case errSecItemNotFound:
        // Add new
        var addQuery = query
        addQuery[kSecValueData as String] = data
        let addStatus = SecItemAdd(addQuery as CFDictionary, nil)
        guard addStatus == errSecSuccess else {
            throw KeychainError.unhandledError(status: addStatus)
        }
    default:
        throw KeychainError.unhandledError(status: status)
    }
}
```

### 7. Always Target Data Protection Keychain on macOS

macOS has legacy file-based keychain. Always set this flag:

```swift
query[kSecUseDataProtectionKeychain as String] = true
```

---

## Top 10 AI-Generated Security Mistakes

These are the most common insecure patterns AI coding assistants produce:

| # | Anti-Pattern | Severity |
|---|---|---|
| 1 | Storing tokens/secrets in UserDefaults | CRITICAL |
| 2 | Hardcoded API keys in source | CRITICAL |
| 3 | `LAContext.evaluatePolicy()` as sole auth gate (bypassable with Frida/objection) | CRITICAL |
| 4 | Ignoring `SecItem*` return codes | HIGH |
| 5 | Wrong or missing data protection class (`kSecAttrAccessible`) | HIGH |
| 6 | Nonce reuse in AES-GCM (catastrophic — enables plaintext recovery) | CRITICAL |
| 7 | MD5/SHA-1 for security purposes (use SHA-256+) | HIGH |
| 8 | Logging sensitive data (`print(token)`, `os_log(password)`) | HIGH |
| 9 | Not clearing Keychain on first launch after reinstall | MEDIUM |
| 10 | Non-cryptographic RNG for security (`Int.random()` instead of `SecRandomCopyBytes`) | HIGH |

---

## Biometric Auth: The Boolean Gate Vulnerability

`LAContext.evaluatePolicy()` returns a Bool that lives in app memory. Attackers with Frida/objection can hook the callback and flip `false` → `true`, bypassing biometrics entirely.

**Secure pattern:** Store the actual secret in the Keychain with `SecAccessControl` + Secure Enclave. The OS enforces biometric verification at the hardware level — there's no Bool to bypass:

```swift
// 1. Create access control
let access = SecAccessControlCreateWithFlags(
    nil,
    kSecAttrAccessibleWhenPasscodeSetThisDeviceOnly,
    .biometryCurrentSet,  // Invalidates if biometrics change
    nil
)!

// 2. Store secret with biometric protection
let query: [String: Any] = [
    kSecClass as String: kSecClassGenericPassword,
    kSecAttrService as String: "com.app.auth",
    kSecAttrAccount as String: "session-token",
    kSecAttrAccessControl as String: access,
    kSecValueData as String: tokenData
]
SecItemAdd(query as CFDictionary, nil)

// 3. Retrieve — OS prompts biometric automatically
let searchQuery: [String: Any] = [
    kSecClass as String: kSecClassGenericPassword,
    kSecAttrService as String: "com.app.auth",
    kSecAttrAccount as String: "session-token",
    kSecReturnData as String: true
]
var result: AnyObject?
let status = SecItemCopyMatching(searchQuery as CFDictionary, &result)
// If user fails biometric, status != errSecSuccess — no Bool to bypass
```

**Biometric flag selection:**
- `.biometryCurrentSet` — Invalidates when biometrics change (most secure for credentials)
- `.biometryAny` — Survives biometric enrollment changes
- `.userPresence` — Accepts biometric OR passcode fallback

---

## Credential Lifecycle

### Logout — Clear Everything

```swift
actor CredentialManager {
    func clearAll() throws {
        let secClasses = [
            kSecClassGenericPassword,
            kSecClassInternetPassword,
            kSecClassCertificate,
            kSecClassKey
        ]
        for secClass in secClasses {
            let query: [String: Any] = [kSecClass as String: secClass]
            SecItemDelete(query as CFDictionary)
            // Ignore errSecItemNotFound — item may not exist
        }
    }
}
```

### Token Refresh — Atomic Rotation

Never delete old token before storing new one. Use update-in-place to avoid window where no token exists:

```swift
func rotateToken(service: String, newToken: Data) throws {
    let query: [String: Any] = [
        kSecClass as String: kSecClassGenericPassword,
        kSecAttrService as String: service
    ]
    let attributes: [String: Any] = [
        kSecValueData as String: newToken
    ]
    let status = SecItemUpdate(query as CFDictionary, attributes as CFDictionary)
    guard status == errSecSuccess else {
        throw KeychainError.unhandledError(status: status)
    }
}
```

### First Launch — Clear Stale Keychain

Keychain survives app reinstall. On first launch, clear stale credentials:

```swift
let hasLaunchedKey = "hasLaunchedBefore"
if !UserDefaults.standard.bool(forKey: hasLaunchedKey) {
    try? credentialManager.clearAll()
    UserDefaults.standard.set(true, forKey: hasLaunchedKey)
}
```

---

## CryptoKit Algorithm Selection

| Purpose | Algorithm | Notes |
|---|---|---|
| Hashing | SHA256 / SHA384 / SHA512 | SHA-2 family. SHA-3 available iOS 26+ |
| HMAC | HMAC\<SHA256\> | Message authentication |
| Symmetric encryption | AES.GCM | Default choice for encryption |
| Symmetric encryption (alt) | ChaChaPoly | Better for software-only (no AES hardware) |
| Signing | P256.Signing (ECDSA) | Curve25519 also available |
| Key agreement | P256.KeyAgreement (ECDH) | Derive shared secrets |
| Post-quantum | HPKE, ML-KEM, ML-DSA | iOS 26+, forward-looking |

---

## Anti-Pattern Quick Scan

| Pattern | Severity | What to Check |
|---|---|---|
| `UserDefaults` storing tokens/passwords | CRITICAL | Move to Keychain |
| Missing `OSStatus` check after `SecItem*` | CRITICAL | Add error handling |
| `LAContext.evaluatePolicy()` without Keychain binding | CRITICAL | Bind to access control |
| No `kSecAttrAccessible` set | HIGH | Add explicit accessibility |
| `SecItem*` on main thread / `@MainActor` | HIGH | Move to background actor |
| `kSecAttrAccessibleAlways` | HIGH | Use stricter constant |
| Force-unwrapping `SecAccessControlCreateWithFlags` | HIGH | Handle nil result |
| Hardcoded keys/secrets in source | CRITICAL | Use Keychain or env vars |
| Missing `kSecUseDataProtectionKeychain` on macOS | HIGH | Add flag |
| `@unchecked Sendable` on Keychain wrapper | MEDIUM | Use actor isolation |
| Missing delete rule for credential rotation | MEDIUM | Implement rotation pattern |
| No error enum for Keychain errors | MEDIUM | Create typed error enum |

---

## Review Checklist

1. Are secrets stored exclusively in Keychain (never UserDefaults/plist)?
2. Is `OSStatus` checked after every `SecItem*` call?
3. Is biometric auth bound to a Keychain item with `SecAccessControl`?
4. Is `kSecAttrAccessible` explicitly set with the most restrictive constant?
5. Are Keychain operations off the main actor?
6. Is the correct `kSecClass` used (GenericPassword, InternetPassword, etc.)?
7. Is CryptoKit used instead of legacy `CommonCrypto` / `Security` framework?
8. Are Secure Enclave keys used for high-value operations?
9. Is keychain sharing configured correctly (access groups)?
10. Is certificate trust evaluation implemented for pinning?
11. Is `kSecUseDataProtectionKeychain` set on macOS?

---

## Version Baseline

| API | Minimum iOS | Common AI Mistake |
|---|---|---|
| Keychain Services | iOS 2+ | Ignoring OSStatus returns |
| LocalAuthentication | iOS 8+ | Using evaluatePolicy() standalone |
| CryptoKit | iOS 13+ | Using CommonCrypto instead |
| Secure Enclave via CryptoKit | iOS 13+ | Assuming all devices support it |
| SecAccessControl biometry flags | iOS 11.3+ | Not handling fallback to passcode |
| `#Index` in SwiftData | iOS 18+ | N/A |
| Post-quantum (ML-KEM, ML-DSA) | iOS 26+ | Using before availability check |

---

## References

For detailed reference material, see the original skill:
- [keychain-fundamentals](https://github.com/ivan-magda/swift-security-skill) — Query structure, item classes, search behavior
- [biometric-authentication](https://github.com/ivan-magda/swift-security-skill) — LAContext, access control flags, fallback
- [cryptokit-symmetric / cryptokit-public-key](https://github.com/ivan-magda/swift-security-skill) — Algorithm selection, Secure Enclave keys
- [credential-storage-patterns](https://github.com/ivan-magda/swift-security-skill) — Token lifecycle, rotation, migration
- [common-anti-patterns](https://github.com/ivan-magda/swift-security-skill) — Full anti-pattern catalog with fixes
- [compliance-owasp-mapping](https://github.com/ivan-magda/swift-security-skill) — OWASP MASTG mapping
