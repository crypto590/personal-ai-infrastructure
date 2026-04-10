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
