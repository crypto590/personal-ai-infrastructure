---
name: play-store-distribution
description: Step-by-step checklist for distributing an Android app through Google Play
type: workflow
platform: Android
---

# Google Play Distribution Workflow

Covers the full pipeline from pre-flight checks through production rollout, including all testing tracks.

---

## Prerequisites (One-Time Setup)

### Google Play Developer Account

- [ ] Active Google Play Developer account ($25 one-time fee)
- [ ] Developer profile complete (name, address, contact email)
- [ ] App created in Google Play Console: All apps → Create app
- [ ] App category, content rating questionnaire completed
- [ ] Privacy policy URL provided

### Signing Configuration

Android requires release builds to be signed. The upload key signs builds for Play App Signing.

**Generate upload keystore (do this once, store securely):**

```bash
keytool -genkey -v \
  -keystore upload-keystore.jks \
  -keyalias upload \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000
```

**Store keystore securely:**
- NEVER commit `upload-keystore.jks` to version control
- Add to `.gitignore`: `*.jks`, `*.keystore`, `keystore.properties`
- Store in a password manager or secrets vault (1Password, AWS Secrets Manager)

**`keystore.properties` (gitignored):**
```properties
storeFile=../upload-keystore.jks
storePassword=your-store-password
keyAlias=upload
keyPassword=your-key-password
```

**`build.gradle.kts` signing config:**
```kotlin
android {
    signingConfigs {
        create("release") {
            val keystoreProps = Properties().apply {
                load(rootProject.file("keystore.properties").inputStream())
            }
            storeFile = file(keystoreProps["storeFile"] as String)
            storePassword = keystoreProps["storePassword"] as String
            keyAlias = keystoreProps["keyAlias"] as String
            keyPassword = keystoreProps["keyPassword"] as String
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
            signingConfig = signingConfigs.getByName("release")
        }
    }
}
```

### Play App Signing (Required for Play Store)

Google Play uses Play App Signing — Google re-signs your APK/AAB with the app signing key. Your upload key is just used to authenticate uploads.

- [ ] Enable in Play Console: App → Setup → App integrity → App signing

---

## 1. Pre-Flight Checks

### Lint and Static Analysis

```bash
cd /path/to/your/project

# Run all quality checks
./gradlew ktlintCheck
./gradlew detekt
./gradlew lint

# Run tests
./gradlew test

# All checks must pass before proceeding
```

### ProGuard / R8 Configuration Verification

```bash
# Build release to verify R8 doesn't strip required classes
./gradlew assembleRelease

# Common rules to verify are present in proguard-rules.pro:
```

```proguard
# Keep @Serializable classes (kotlinx.serialization + Navigation routes)
-keepattributes *Annotation*
-keep class kotlinx.serialization.** { *; }
-keepclassmembers class ** {
    @kotlinx.serialization.Serializable *;
}

# Keep Hilt-generated components
-keep class dagger.hilt.** { *; }
-keep @dagger.hilt.android.HiltAndroidApp class * { *; }

# Keep Room entities
-keep @androidx.room.Entity class * { *; }
-keep @androidx.room.Dao class * { *; }

# Keep Retrofit service interfaces
-keep interface * extends retrofit2.Call { *; }
-keepclassmembers class * {
    @retrofit2.http.* <methods>;
}

# Keep Ktor serialization
-keep class io.ktor.** { *; }

# Keep enum values (commonly stripped)
-keepclassmembers enum * { *; }
```

### Version Code and Version Name Management

Version code must be strictly increasing — Play Store rejects duplicate or lower version codes.

```kotlin
// build.gradle.kts
android {
    defaultConfig {
        versionCode = 42          // Integer, must increment each release
        versionName = "1.4.2"    // Human-readable (semver recommended)
    }
}
```

**Automate version code via CI:**
```bash
# Use the CI build number as version code (GitHub Actions example)
VERSION_CODE=${{ github.run_number }}
./gradlew assembleRelease -PversionCode=$VERSION_CODE
```

```kotlin
// build.gradle.kts — read from Gradle property
val versionCode = (project.findProperty("versionCode") as String?)?.toInt() ?: 1
```

### Data Safety Form

- [ ] Play Console → App content → Data safety
- [ ] Declare all data collected (location, device ID, personal info)
- [ ] Declare all third-party SDKs and their data use
- [ ] Firebase Analytics, Crashlytics, Ads SDKs all require disclosure
- [ ] Must be updated when new data collection is added

### Pre-Release Checklist

- [ ] All API endpoints point to production (not localhost or staging)
- [ ] All API keys are production keys (check for dev/staging keys)
- [ ] Logging disabled in release build (`BuildConfig.DEBUG` guards)
- [ ] Analytics/crash reporting enabled for production
- [ ] `minifyEnabled = true` and `shrinkResources = true` for release

---

## 2. Build

### AAB vs APK

**Always use AAB (Android App Bundle) for Play Store submissions.** AAB is required for new apps since August 2021.

- AAB: Google Play generates optimized APKs per device → smaller downloads
- APK: Only use for direct distribution or testing outside Play Store

### Build Release AAB

```bash
# Build signed AAB (uses signingConfig defined in build.gradle.kts)
./gradlew bundleRelease

# Output: app/build/outputs/bundle/release/app-release.aab
```

### Build Signed APK (for direct distribution only)

```bash
./gradlew assembleRelease

# Output: app/build/outputs/apk/release/app-release.apk
```

### Verify the Build

```bash
# Check the AAB is signed correctly
bundletool validate --bundle=app/build/outputs/bundle/release/app-release.aab

# Extract and inspect APKs locally (optional)
bundletool build-apks \
  --bundle=app-release.aab \
  --output=app.apks \
  --ks=upload-keystore.jks \
  --ks-key-alias=upload \
  --ks-pass=pass:your-password \
  --key-pass=pass:your-key-password

bundletool install-apks --apks=app.apks
```

---

## 3. Upload to Google Play

### Option A — Play Console Web UI (Recommended for First-Time)

1. Go to [play.google.com/console](https://play.google.com/console)
2. Select your app
3. Navigate to: Testing → Internal testing (or Production → Releases)
4. Click "Create new release"
5. Upload `app-release.aab`
6. Fill in release notes (what's new for users)
7. Click "Save" then "Review release"

### Option B — Gradle Play Publisher Plugin (Automated)

```kotlin
// build.gradle.kts
plugins {
    id("com.github.triplet.play") version "3.10.1"
}

play {
    serviceAccountCredentials.set(file("service-account.json"))
    track.set("internal")  // or "alpha", "beta", "production"
    releaseStatus.set(ReleaseStatus.COMPLETED)
    defaultToAppBundles.set(true)
}
```

```bash
# Upload to internal track
./gradlew publishReleaseBundle

# Upload to production
./gradlew publishReleaseBundle --track production

# Promote from internal to alpha
./gradlew promoteReleaseArtifact --from-track internal --promote-track alpha
```

**Service account setup:**
1. Play Console → Setup → API access → Link Google Cloud project
2. Google Cloud Console → IAM → Create Service Account
3. Grant "Release Manager" role in Play Console
4. Download JSON credentials → save as `service-account.json` (gitignored)

### Option C — bundletool CLI

```bash
# bundletool is the underlying tool Play uses
bundletool build-apks \
  --bundle=app-release.aab \
  --output=app.apks

# Direct upload requires Play Developer API — use Gradle plugin instead
```

---

## 4. Testing Tracks

### Internal Testing (Immediate Access)

- Up to 100 testers
- No review required — available within minutes of upload
- Must be added by email address in Play Console

**Setup:**
- [ ] Testing → Internal testing → Manage testers
- [ ] Add tester emails or Google Groups
- [ ] Testers install via the opt-in link

### Closed Testing — Alpha

- Up to 2,000 testers
- Requires **closed testing review** (usually fast, 1-2 hours)
- Can use email lists or Google Groups

**Setup:**
- [ ] Testing → Closed testing → Alpha → Create track
- [ ] Upload AAB and submit for review
- [ ] After approval: add testers and share opt-in link

### Open Testing — Beta

- Unlimited testers (public link)
- Requires **open testing review** (usually 1-3 days)
- Anyone with the link can join

**Setup:**
- [ ] Testing → Open testing → Create track
- [ ] Submit for open testing review
- [ ] After approval: enable and share the Play Store beta link

### Production Rollout (Staged)

Production releases support gradual rollout to reduce risk.

**Recommended staged rollout:**

| Stage | Percentage | Wait Time |
|---|---|---|
| Initial | 1% | 24-48 hours (monitor crash rate) |
| Stage 2 | 5% | 48 hours (monitor ANR rate) |
| Stage 3 | 20% | 72 hours (monitor ratings) |
| Stage 4 | 50% | 48 hours |
| Full | 100% | — |

**In Play Console:**
- Production → Releases → Create new release
- After upload: set rollout percentage (1%)
- Increase via: Production → Release → Manage rollout → Increase rollout

**Halt rollout if:**
- Crash rate increases > 0.5% vs previous release
- ANR rate increases > 0.3%
- Rating drops significantly in new reviews

---

## 5. Post-Deployment Monitoring

### Firebase Crashlytics

```kotlin
// build.gradle.kts
implementation("com.google.firebase:firebase-crashlytics-ktx")
implementation("com.google.firebase:firebase-analytics-ktx")

// In Application class:
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        FirebaseApp.initializeApp(this)
    }
}
```

Monitor after each release:
- Firebase Console → Crashlytics → crash-free users %
- Target: maintain > 99.5% crash-free session rate
- Alert: crash-free rate drops > 0.5% → halt rollout

### ANR Monitoring

ANRs (Application Not Responding) — blocked main thread for > 5 seconds.

- Play Console → Android vitals → ANR rate
- Target: < 0.47% (Play Console "bad behavior" threshold is 0.47%)
- Common causes: database queries on main thread, synchronous network calls

### Play Console Vitals

Monitor after every release:

- [ ] Android vitals → Crashes & ANRs — check crash rate trend
- [ ] Android vitals → Core vitals — startup time, render time
- [ ] Android vitals → App size — verify AAB optimization working
- [ ] Android vitals → Permissions — check permission denial rate

### User Reviews Monitoring

- [ ] Inbox → Reviews — read and respond to all 1-3 star reviews
- [ ] Set up review notifications in Play Console
- [ ] Tag reviews by theme (crash, feature request, UI confusion)

---

## 6. Common Issues

| Issue | Fix |
|---|---|
| "Version code already used" | Increment `versionCode` in `build.gradle.kts` |
| "APK is not signed" | Verify `signingConfig` set in `buildTypes.release` |
| "Upload key mismatch" | Use the same upload keystore registered with Play App Signing |
| "Invalid APK" when uploading AAB | AABs require `bundleRelease`, not `assembleRelease` |
| R8 strips navigation routes | Add `-keep @kotlinx.serialization.Serializable class * { *; }` to ProGuard |
| R8 strips Hilt | Add Hilt keep rules or use `@Keep` annotation |
| "App not optimized for large screens" | Add `<uses-permission android:name="android.permission.CAMERA"/>` to manifest if needed, implement adaptive layouts |
| Data safety form rejected | Ensure all Firebase/Ads SDK data practices are declared |
| Service account 401 error | Re-grant "Release Manager" role in Play Console → API access |

---

## Checklist Summary

```
Pre-flight
  [ ] ktlint + Detekt + Lint pass
  [ ] Unit tests pass
  [ ] Production API keys/endpoints configured
  [ ] ProGuard rules verified (serialization, Hilt, Room)
  [ ] versionCode incremented
  [ ] versionName updated
  [ ] Data safety form current

Build
  [ ] ./gradlew bundleRelease succeeds
  [ ] AAB signed with upload keystore
  [ ] bundletool validate passes

Upload
  [ ] AAB uploaded to Play Console
  [ ] Release notes written (what's new)
  [ ] Review release summary confirmed

Distribution
  [ ] Internal testing: immediate rollout to team
  [ ] Closed testing (alpha): submit for review if needed
  [ ] Production: start at 1% staged rollout

Post-Deployment (first 48 hours)
  [ ] Crashlytics crash-free rate >= 99.5%
  [ ] ANR rate stable
  [ ] Play Console vitals showing no regressions
  [ ] Increase rollout % or halt if issues found
```
