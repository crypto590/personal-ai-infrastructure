# Android Code Quality Checks

**Part of:** [kotlin-android](../SKILL.md) > Quality

**Trigger:** Before commits or PRs for Android code, running `/android-check`, validating build integrity, running unit tests, checking code coverage, fixing ktlint or Detekt violations, verifying Compose stability.

---

## Arguments

- `--test` - Run unit tests after lint/build
- `--coverage` - Run tests with JaCoCo coverage report
- `--fix` - Auto-fix ktlint violations where possible
- `--compose` - Run Compose compiler metrics (stability report)
- `[path]` - Android project path (defaults to detecting project in current repo)

---

## Workflow

### 1. Detect Android Project

Look for Android project in this order:
1. Explicit path argument
2. `apps/[project-name]/` relative to git root containing `build.gradle.kts`
3. Current directory if it contains `settings.gradle.kts`

### 2. Check Tool Configurations

If configuration files don't exist:
1. Show the user the template (see below)
2. Ask if they want to create them
3. Create if confirmed

### 3. Run Checks (in order)

| Check | Command | When |
|---|---|---|
| **ktlint** | `./gradlew ktlintCheck` or `./gradlew ktlintFormat` | Always |
| **Detekt** | `./gradlew detekt` | Always |
| **Android Lint** | `./gradlew lint` | Always |
| **Build** | `./gradlew assembleDebug` | Always |
| **Unit Tests** | `./gradlew test` | `--test` or `--coverage` |
| **Coverage** | `./gradlew jacocoTestReport` | `--coverage` |
| **Compose Metrics** | `./gradlew assembleRelease -PcomposeCompilerReports=true` | `--compose` |

### 4. Report Results

```
## Android Check Results

| Check          | Status     | Details                        |
|----------------|------------|--------------------------------|
| ktlint         | pass/fail  | X warnings, Y errors           |
| Detekt         | pass/fail  | X issues (complexity/naming)   |
| Android Lint   | pass/fail  | X warnings, Y errors           |
| Build          | pass/fail  | [errors if any]                |
| Tests          | pass/fail/skipped | X passed, Y failed      |
| Coverage       | pass/skipped | XX.X% / skipped              |
| Compose Stable | pass/skipped | X% stable composables        |

**Ready for commit**: Yes/No
```

### 5. If Issues Found

- List ktlint errors with `file:line` references
- Offer to format with `--fix` if not already used
- For build errors, show the relevant Gradle output
- For Lint errors, include rule ID and description

---

## ktlint Configuration Template

`.editorconfig` in project root:

```editorconfig
[*.{kt,kts}]
ij_kotlin_imports_layout = *,^
ktlint_standard_no-wildcard-imports = disabled
ktlint_standard_filename = disabled
ktlint_code_style = intellij_idea
indent_size = 4
max_line_length = 120

# Disable rules that conflict with Compose patterns
ktlint_standard_trailing-comma-on-call-site = disabled
ktlint_standard_trailing-comma-on-declaration-site = disabled
ktlint_compose_compositionlocal-allowlist = disabled
```

`build.gradle.kts` ktlint plugin setup:

```kotlin
plugins {
    id("org.jlleitschuh.gradle.ktlint") version "12.1.1"
}

ktlint {
    version.set("1.3.1")
    android.set(true)
    ignoreFailures.set(false)
    reporters {
        reporter(ReporterType.PLAIN)
        reporter(ReporterType.CHECKSTYLE)
    }
    filter {
        exclude("**/generated/**")
        exclude("**/build/**")
    }
}
```

---

## Detekt Configuration Template

`detekt.yml` in project root:

```yaml
# Detekt Configuration for Android Projects
build:
  maxIssues: 0
  excludeCorrectable: false

complexity:
  ComplexMethod:
    threshold: 15
  LongMethod:
    threshold: 60
  LongParameterList:
    threshold: 6
  TooManyFunctions:
    threshold: 15
  CyclomaticComplexMethod:
    threshold: 15

naming:
  FunctionNaming:
    active: true
    functionPattern: '([a-z][a-zA-Z0-9]*)|([A-Z][a-zA-Z0-9]*)' # Allow PascalCase for Composables
  TopLevelPropertyNaming:
    active: true
    constantPattern: '[A-Z][_A-Z0-9]*'

style:
  MagicNumber:
    active: true
    ignoreAnnotated: ['Preview', 'Composable']
    ignoreNumbers: ['-1', '0', '1', '2', '100']
  MaxLineLength:
    maxLineLength: 120
    excludeCommentStatements: true

coroutines:
  GlobalCoroutineUsage:
    active: true  # Flag GlobalScope usage
  RedundantSuspendModifier:
    active: true
  SuspendFunWithFlowReturnType:
    active: true

exceptions:
  SwallowedException:
    active: true
  TooGenericExceptionCaught:
    active: true

performance:
  SpreadOperator:
    active: true

formatting:
  active: false  # Let ktlint handle formatting

output-reports:
  active: true

exclude-patterns:
  - '**/*.kts'
  - '**/build/**'
  - '**/generated/**'
```

`build.gradle.kts` Detekt setup:

```kotlin
plugins {
    id("io.gitlab.arturbosch.detekt") version "1.23.6"
}

detekt {
    toolVersion = "1.23.6"
    config.setFrom("$rootDir/detekt.yml")
    buildUponDefaultConfig = true
    allRules = false
    autoCorrect = false
    parallel = true
}

dependencies {
    detektPlugins("io.gitlab.arturbosch.detekt:detekt-formatting:1.23.6")
    detektPlugins("com.twitter.compose.rules:detekt:0.0.26")  // Compose-specific rules
}
```

---

## Android Lint Key Rules

| Rule | Category | Severity |
|---|---|---|
| `ContentDescription` | Accessibility | Error |
| `TouchTargetSizeCheck` | Accessibility | Warning |
| `TextContrastCheck` | Accessibility | Warning |
| `HardcodedText` | Internationalization | Warning |
| `SetTextI18n` | Internationalization | Warning |
| `UseSparseArrays` | Performance | Warning |
| `DrawAllocation` | Performance | Warning |
| `WrongThread` | Correctness | Error |
| `Recycle` | Correctness | Error |
| `MissingPermission` | Correctness | Error |
| `NewApi` | Correctness | Error |
| `HardcodedDebugMode` | Security | Error |
| `AllowBackup` | Security | Warning |
| `ExportedActivity` | Security | Warning |

Custom lint configuration in `build.gradle.kts`:

```kotlin
android {
    lint {
        abortOnError = true
        checkReleaseBuilds = true
        warningsAsErrors = false
        xmlReport = true
        htmlReport = true
        disable += setOf("GradleDependency", "NewerVersionAvailable")
        error += setOf("ContentDescription")
    }
}
```

---

## JaCoCo Code Coverage Configuration

```kotlin
// build.gradle.kts
tasks.register<JacocoReport>("jacocoTestReport") {
    dependsOn("testDebugUnitTest")

    reports {
        xml.required.set(true)
        html.required.set(true)
    }

    val fileFilter = listOf(
        "**/R.class",
        "**/R\$*.class",
        "**/BuildConfig.*",
        "**/Manifest*.*",
        "**/*Test*.*",
        "**/*_Factory*",
        "**/*_MembersInjector*",
        "**/*Module_Provides*",
        "**/*Hilt_*",
        "**/*_Impl*"
    )

    sourceDirectories.setFrom(files("$projectDir/src/main/java"))
    classDirectories.setFrom(
        fileTree("$buildDir/tmp/kotlin-classes/debug") { exclude(fileFilter) }
    )
    executionData.setFrom(
        fileTree(buildDir) { include("jacoco/testDebugUnitTest.exec") }
    )
}
```

Coverage thresholds (recommended):
- Overall: 70% minimum
- ViewModel: 85% minimum
- Repository: 80% minimum
- UseCase: 90% minimum

---

## Compose Compiler Metrics

Enable stability reporting to identify unnecessary recompositions:

```kotlin
// build.gradle.kts
android {
    composeOptions {
        kotlinCompilerExtensionVersion = "1.5.14"
    }
}

// Enable metrics via Gradle property:
// ./gradlew assembleRelease -PcomposeCompilerReports=true -PcomposeCompilerMetrics=true

// Or in gradle.properties:
// composeCompilerReports=true
// composeCompilerMetrics=true
```

Output is written to `build/compose_metrics/`. Check:
- `*-composables.txt` - Stability of each composable's parameters
- `*-classes.txt` - Stability of data classes passed to composables
- `*-composables.csv` - Skippability report (skippable = good)

Fixing unstable composables:

```kotlin
// PROBLEM - List<> parameter is unstable (interface)
@Composable
fun UserList(users: List<User>) { /* recomposes unnecessarily */ }

// FIX 1 - Use ImmutableList from kotlinx.collections.immutable
@Composable
fun UserList(users: ImmutableList<User>) { /* stable */ }

// FIX 2 - Annotate data class with @Immutable
@Immutable
data class User(val id: String, val name: String)

// FIX 3 - Use @Stable for classes with predictable mutation
@Stable
class UserState(initialUsers: List<User>) {
    var users by mutableStateOf(initialUsers)
}
```

---

## Gradle Dependency Updates

```bash
# Check for outdated dependencies
./gradlew dependencyUpdates

# Using gradle-versions-plugin (add to build.gradle.kts):
plugins {
    id("com.github.ben-manes.versions") version "0.51.0"
}

# Generate dependency report
./gradlew dependencies > dependency-report.txt
```

---

## CI/CD Integration (GitHub Actions)

```yaml
# .github/workflows/android-ci.yml
name: Android CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  check:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: gradle

      - name: Grant execute permission for gradlew
        run: chmod +x gradlew

      - name: Run ktlint
        run: ./gradlew ktlintCheck

      - name: Run Detekt
        run: ./gradlew detekt

      - name: Run Android Lint
        run: ./gradlew lint

      - name: Build debug APK
        run: ./gradlew assembleDebug

      - name: Run unit tests
        run: ./gradlew test

      - name: Generate coverage report
        run: ./gradlew jacocoTestReport

      - name: Upload lint results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: lint-results
          path: app/build/reports/lint-results-debug.html

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-results
          path: app/build/reports/tests/

      - name: Upload coverage report
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: app/build/reports/jacoco/

      - name: Comment PR with results
        uses: gradle/actions/setup-gradle@v3
```

---

## Examples

```bash
# Quick lint + build check
/android-check

# Full check with tests
/android-check --test

# Fix ktlint violations automatically
/android-check --fix

# Tests with coverage
/android-check --coverage

# Check Compose stability
/android-check --compose

# Specific project path
/android-check ~/Projects/my-android-app
```
