---
name: testflight-deployment
description: Step-by-step checklist for deploying the Athlead iOS app to TestFlight
type: workflow
app: athlead
platform: iOS
---

# TestFlight Deployment Workflow

Covers the full pipeline from pre-flight checks through tester distribution.
Project root: `apps/athlead-ios/`
Scheme: `athlead`
Project file: `apps/athlead-ios/athlead.xcodeproj`

---

## Prerequisites (one-time setup)

### Apple Developer Account
- [ ] Active Apple Developer Program membership ($99/year)
- [ ] App ID registered in Developer Portal matching bundle ID (e.g., `com.athlead.app`)
- [ ] App record created in App Store Connect (Apps → New App)

### Certificates & Signing
- [ ] **Apple Distribution certificate** in your keychain (not just Development)
  - Certificates, Identifiers & Profiles → Certificates → + → Apple Distribution
  - Download and double-click to install in Keychain Access
- [ ] **App Store provisioning profile** associated with the Distribution cert
  - Profiles → + → App Store Connect → select App ID → select certificate
  - Download and double-click to install
- [ ] Alternatively: enable **Automatically manage signing** in Xcode (simplest path)
  - Xcode → Project → Signing & Capabilities → check "Automatically manage signing"
  - Select your Team

### App Store Connect setup
- [ ] App record exists for `athlead` (bundle ID must match exactly)
- [ ] At least one version record created (e.g., 1.0.0)
- [ ] App Privacy questionnaire answered in App Store Connect (required before first upload)

---

## 1. Pre-flight Checks

### Lint and type check
```bash
cd /Users/coreyyoung/Desktop/Projects/athlead
bun run lint
bunx turbo check-types
```

### Environment config — confirm production values
Review `apps/athlead-ios/Config/Environment.xcconfig` and ensure:
- [ ] All `*_API_URL` values point to production endpoints (not localhost or staging)
- [ ] `CLERK_PUBLISHABLE_KEY` is the production key (starts with `pk_live_`)
- [ ] `GETSTREAM_API_KEY` is production
- [ ] `LIVEKIT_URL` is production (`wss://`)

### Privacy manifest
`apps/athlead-ios/athlead/PrivacyInfo.xcprivacy` — verify that any new API categories used since the last release are declared. Current manifest declares `NSPrivacyAccessedAPICategoryUserDefaults` (reason `CA92.1`). If new system APIs were added, add corresponding entries.

### Version and build number
- [ ] Marketing version (CFBundleShortVersionString) is correct (e.g., `1.0.0`)
- [ ] Build number (CFBundleVersion) is higher than the last uploaded build — App Store Connect rejects duplicate build numbers
  - In Xcode: target → General → Identity → Version / Build
  - Or in project.pbxproj / Info.plist directly

---

## 2. Archive

### Option A — Xcode GUI (recommended for first-time)

1. In Xcode, set the run destination to **Any iOS Device (arm64)** (not a simulator)
2. Product → Archive
3. Xcode Organizer opens automatically when archiving completes

### Option B — xcodebuild CLI

```bash
cd /Users/coreyyoung/Desktop/Projects/athlead/apps/athlead-ios

xcodebuild \
  -project athlead.xcodeproj \
  -scheme athlead \
  -sdk iphoneos \
  -configuration Release \
  -archivePath "$PWD/build/athlead.xcarchive" \
  archive
```

If using a workspace (e.g., CocoaPods), swap `-project` for `-workspace athlead.xcworkspace`. This project uses Swift Package Manager so `-project` is correct.

---

## 3. Export & Upload

### Option A — Xcode Organizer (simplest)

1. Window → Organizer → Archives tab → select the new archive
2. Distribute App → App Store Connect → Upload
3. Follow the wizard (leave defaults for bitcode/symbols)
4. Xcode uploads directly — no IPA file needed on disk

### Option B — xcodebuild CLI (direct upload)

Create `apps/athlead-ios/ExportOptions.plist` (not committed — add to `.gitignore`):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>method</key>
    <string>app-store</string>
    <key>destination</key>
    <string>upload</string>
    <key>teamID</key>
    <string>YOUR_TEAM_ID</string>
    <key>uploadBitcode</key>
    <false/>
    <key>uploadSymbols</key>
    <true/>
</dict>
</plist>
```

Then run:

```bash
xcodebuild \
  -exportArchive \
  -archivePath "$PWD/build/athlead.xcarchive" \
  -exportOptionsPlist ExportOptions.plist \
  -exportPath "$PWD/build/export"
```

With `destination: upload` in the plist, `xcodebuild` uploads directly to App Store Connect. No separate altool/Transporter step needed.

### Option C — altool (legacy, avoid for new workflows)

`xcrun altool --upload-app` is deprecated and has known breakages in Xcode 26+. Use Options A or B instead.

---

## 4. Processing Wait

After upload, App Store Connect processes the build. This typically takes **5–30 minutes** but can be longer. You will receive an email when processing completes. The build will then appear in App Store Connect → TestFlight → Builds.

---

## 5. TestFlight Configuration in App Store Connect

### Internal testers (no review required — fastest path)

- [ ] TestFlight tab → Internal Testing → select or create a group
- [ ] Add the build to the group
- [ ] Add team members (must have Account Holder / Admin / Developer / App Manager role)
- [ ] Testers receive an email invitation; they install the TestFlight app and accept

Internal testers get access immediately — no App Review required.

### External testers (up to 10,000 — requires review for first build)

- [ ] TestFlight tab → External Testing → create a group (e.g., "Beta Users")
- [ ] Add the build — this triggers **Beta App Review** (first build of each version)
  - Beta App Review typically takes **24–48 hours**
  - Only the first build per version requires review; subsequent builds of the same version may skip
- [ ] Provide Beta App Information:
  - Beta app description (what's new, what to test)
  - Feedback email address
  - Sign-in credentials if app requires auth (provide a test account)
- [ ] Invite testers:
  - By email (individual invites)
  - Or enable a **Public Link** (shareable URL, can set enrollment criteria by device/OS)

---

## 6. Tester Limits Reference

| Type | Max Testers | Review Required | Access Speed |
|------|-------------|-----------------|--------------|
| Internal | 100 | No | Immediate |
| External | 10,000 | Yes (first build per version) | 24–48h after review |

Each tester can install on up to 30 devices.

---

## 7. Common Issues

| Issue | Fix |
|-------|-----|
| "No accounts with iTunes Connect access" | Add your Apple ID in Xcode → Settings → Accounts |
| Duplicate build number | Increment CFBundleVersion — must be unique per App Store Connect app |
| Build stuck in "Processing" | Usually resolves within 1 hour; if not, re-upload with a new build number |
| Missing push notification entitlement | Ensure APS environment is set to `production` in release provisioning profile |
| Privacy manifest validation error | Add missing `NSPrivacyAccessedAPIType` entries to `PrivacyInfo.xcprivacy` |
| Signing identity not found | Install Apple Distribution cert from Developer Portal into Keychain Access |
| Export fails with "No profiles" | Download provisioning profile from Developer Portal, double-click to install |
| altool non-zero exit (-1) on Xcode 26 | Switch to `xcodebuild -exportArchive` with `destination: upload` (altool deprecated) |
| GetStream/LiveKit SDK symbols missing dSYM | Enable "Include app symbols" in export wizard or `uploadSymbols: true` in plist |

---

## 8. Incrementing Build Number (automation tip)

Before each archive, bump the build number automatically:

```bash
# In apps/athlead-ios/
CURRENT=$(agvtool what-version -terse)
agvtool new-version -all $((CURRENT + 1))
```

Or set it directly:

```bash
agvtool new-version -all 42
```

`agvtool` reads/writes `CFBundleVersion` across all targets.

---

## Checklist Summary

```
Pre-flight
  [ ] lint + type check pass
  [ ] Environment.xcconfig has production values
  [ ] PrivacyInfo.xcprivacy is current
  [ ] Version + build number bumped

Archive
  [ ] Destination = Any iOS Device (arm64)
  [ ] Configuration = Release
  [ ] Archive succeeds

Upload
  [ ] Via Xcode Organizer or xcodebuild exportArchive
  [ ] Processing email received

TestFlight
  [ ] Build appears in App Store Connect
  [ ] Added to Internal group (immediate) or External group (pending review)
  [ ] Beta description and feedback email set for external groups
```
