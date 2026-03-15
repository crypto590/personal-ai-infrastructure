# Android API Research

**Part of:** [kotlin-android](../SKILL.md) > Review

**Trigger:** Implementing a new Android feature, asking "what's the best way to do X on Android?", exploring unfamiliar Jetpack libraries, checking API level availability for target SDK, finding recommended patterns from Google, understanding deprecations and migrations, researching Google I/O announcements.

---

## Research Process

### 1. Identify the Domain

First, categorize the feature request:

| Domain | Libraries | Example Features |
|---|---|---|
| UI/UX | Compose, Material3, Accompanist | Animations, navigation, theming |
| Data/Persistence | Room, DataStore, Proto DataStore | Local database, preferences |
| Networking | Retrofit, Ktor, OkHttp | REST APIs, WebSockets |
| Async | Coroutines, Flow, WorkManager | Background tasks, scheduling |
| DI | Hilt, Koin | Dependency injection |
| Architecture | ViewModel, Navigation, Paging3 | App structure, lists |
| Media | Media3, CameraX | Audio, video, camera |
| Location | Google Maps SDK, Fused Location | Maps, geofencing |
| AI/ML | ML Kit, Gemini Nano (on-device) | Text recognition, smart replies |
| Security | Biometric, EncryptedSharedPrefs | Auth, secure storage |

### 2. Check Documentation Sources

#### Primary Sources (in order of authority)

1. **Android Developer Documentation**
   - URL: developer.android.com/docs
   - Comprehensive guides, API reference, codelabs
   - Includes migration guides and best practices

2. **Jetpack Release Notes**
   - URL: developer.android.com/jetpack/androidx/versions
   - Current stable/alpha/beta library versions
   - Breaking changes and migration notes

3. **Material Design 3 Documentation**
   - URL: m3.material.io
   - Component specifications, color system, typography
   - Compose Material3 implementation guidance

4. **Google I/O Sessions**
   - URL: io.google (annual conference)
   - Deep dives into new Jetpack features
   - Best practices from Google engineers

5. **Android Developers Blog**
   - URL: android-developers.googleblog.com
   - Announcements and migration guides

### 3. Verify API Level Availability

```kotlin
// Compile-time annotation for API-level-restricted code
@RequiresApi(Build.VERSION_CODES.TIRAMISU)  // API 33+
fun useNewApiFeature() {
    // Android 13+ only code
}

// Runtime availability check
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
    // Use API 33+ feature
} else {
    // Fallback for older versions
}

// Compose check for dynamic color (Android 12+)
val colorScheme = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
    val context = LocalContext.current
    if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
} else {
    if (darkTheme) DarkColorScheme else LightColorScheme
}
```

**Document availability:**
```
API: [name]
Introduced: API [level] / Android [version name]
Deprecated: API [level] (if applicable)
Replacement: [new API] (if deprecated)
AndroidX Compat: [yes/no - backport available]
```

### 4. Jetpack BOM Management

Use the Compose BOM for consistent library versions:

```kotlin
// build.gradle.kts
dependencies {
    val composeBom = platform("androidx.compose:compose-bom:2025.04.00")
    implementation(composeBom)
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.material3:material3")
    // No version needed — BOM manages it
}
```

Check current BOM: developer.android.com/jetpack/compose/bom/bom-mapping

### 5. Deprecated API Watchlist

Common old APIs that LLMs generate incorrectly. Flag during review and replace with modern equivalents.

| Deprecated | Modern Replacement | Notes |
|---|---|---|
| `LiveData` in ViewModel | `StateFlow` / `SharedFlow` | Kotlin-idiomatic |
| `ObservableField` | `StateFlow` | DataBinding replacement |
| `AsyncTask` | Coroutines | Removed in API 30 |
| `Handler` + `Looper` | Coroutines on `Dispatchers.Main` | More structured |
| `SharedPreferences` | `DataStore` (Proto or Preferences) | Thread-safe, coroutine-native |
| `Fragment.startActivityForResult` | `ActivityResultContracts` | Modern result handling |
| `onRequestPermissionsResult` | `ActivityResultContracts.RequestPermission` | Modern permissions |
| `ViewPager` | `ViewPager2` | RecyclerView-based, RTL support |
| `RecyclerView.Adapter` | Compose `LazyColumn`/`LazyRow` | In Compose projects |
| `Navigation.findNavController()` | `rememberNavController()` | In Compose |
| String navigation routes | `@Serializable` data classes | Navigation 2.8+ |
| `Glide` / `Picasso` | `Coil3` (Kotlin-native) | Compose-friendly |
| `RxJava` Observable | `Flow` | Kotlin-native, structured |
| `Gson` | `kotlinx.serialization` or `Moshi` | Kotlin-native |
| `Room` `@Query` with `List<>` return | `Flow<List<>>` | Reactive DB queries |
| `WorkManager` one-time `Worker` | `CoroutineWorker` | Coroutine-native |

---

## Research Output Format

```markdown
## Android API Research: [Topic]

### Query
[Original question/requirement]

### Recommended Approach
[High-level recommendation]

### Primary API
**Library:** [name + version]
**Min API Level:** [number] / Android [version name]
**Documentation:** [link]

### Implementation Pattern
[code example from official docs or Google samples]

### Alternative Approaches
1. [if applicable]
2. [if applicable]

### Caveats
- [API level limitations]
- [known issues]
- [deprecation warnings]

### Resources
- Documentation: [link]
- Google I/O Session: [link]
- Official Sample: [link]
- Now in Android: [link if applicable]

### Integration Notes
[How this fits with existing MVVM architecture]
```

---

## Common Research Scenarios

### New Jetpack Library Investigation

When encountering an unfamiliar Jetpack library:

1. Find library documentation on developer.android.com
2. Check current stable version in Jetpack release notes
3. Identify key types and extension functions
4. Find official sample (github.com/android/nowinandroid is a reference app)
5. Check for Compose-specific integration

### API Level Compatibility

When implementing a feature with API level requirements:

1. Identify the minimum API of the feature
2. Check if an AndroidX compat library provides backporting
3. If no compat: wrap in `Build.VERSION.SDK_INT` check
4. Add `@RequiresApi` annotation to functions requiring higher API
5. Ensure fallback behavior for older devices

### Migration Research

When moving from deprecated to new API:

1. Find deprecation notice in release notes
2. Identify replacement API
3. Compare functionality gaps
4. Document migration steps
5. Check Jetpack migration guides

---

## Documentation URLs

| Library | Documentation |
|---|---|
| Jetpack Compose | developer.android.com/compose |
| Material3 Compose | developer.android.com/jetpack/compose/designsystems/material3 |
| Navigation Compose | developer.android.com/jetpack/compose/navigation |
| Hilt | developer.android.com/training/dependency-injection/hilt-android |
| Room | developer.android.com/jetpack/androidx/releases/room |
| DataStore | developer.android.com/topic/libraries/architecture/datastore |
| ViewModel | developer.android.com/topic/libraries/architecture/viewmodel |
| Coroutines | kotlinlang.org/docs/coroutines-overview.html |
| Kotlin Flow | kotlinlang.org/docs/flow.html |
| WorkManager | developer.android.com/topic/libraries/architecture/workmanager |
| Paging3 | developer.android.com/topic/libraries/architecture/paging/v3-overview |
| Compose BOM | developer.android.com/jetpack/compose/bom |

## Reference App

**Now in Android:** github.com/android/nowinandroid

A production-quality reference app from Google demonstrating all modern Android patterns: MVVM, Hilt, Room, DataStore, Coroutines, Flow, Navigation Compose, Material3, Compose, and testing.
