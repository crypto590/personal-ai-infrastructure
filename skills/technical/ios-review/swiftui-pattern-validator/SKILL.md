---
name: swiftui-pattern-validator
description: Validate MVC architecture compliance in SwiftUI code. Checks Controller patterns, service protocols, task cancellation, and proper layer separation per swift-conventions.md. NOT for concurrency audits (use swift-concurrency-auditor), accessibility (use ios-accessibility-checker), or Liquid Glass (use ios-liquid-glass-reviewer).
compatibility: "Requires macOS with Xcode and SwiftUI project"
context: fork
metadata:
  author: coreyyoung
  version: 1.0.0
  category: technical
  tags: [swiftui, mvc, architecture, pattern-validation, code-review]
---

# SwiftUI Pattern Validator

**Category:** technical/ios-review

**Brief Description:** Code review agent that validates SwiftUI implementations against the MVC architecture defined in swift-conventions.md. Checks Controller class patterns, Service protocols, task cancellation discipline, layer separation, and proper data flow.

---

## When to Use This Skill

Trigger this skill when:
- After writing new SwiftUI features
- Before PR review for iOS code
- User asks "is my architecture correct?"
- Reviewing Controllers, Services, or Views
- Checking for proper layer separation
- Validating async/await patterns
- Implementing new features in Athlead iOS

---

## Validation Checklist

### 1. Controller Class Structure

**Required pattern:**
```swift
@Observable
@MainActor
final class FeatureController {
    // MARK: - Properties
    private(set) var data: Model?
    private(set) var isLoading = false
    private(set) var errorMessage: String?

    // MARK: - Dependencies
    private let service: ServiceProtocol
    private var loadTask: Task<Void, Never>?

    // MARK: - Init
    init(service: ServiceProtocol = Service()) {
        self.service = service
    }

    // MARK: - Methods
    func load() async { ... }

    // MARK: - Cleanup
    deinit {
        loadTask?.cancel()
    }
}
```

**Validation points:**
| Check | Required | Status |
|-------|----------|--------|
| `@Observable` | Yes | ? |
| `@MainActor` | Yes | ? |
| `final class` | Yes | ? |
| `private(set)` on properties | Yes | ? |
| Protocol-based service | Yes | ? |
| Task tracking variable | Yes | ? |
| `deinit` with cancel | Yes | ? |

**Report format:**
```
CONTROLLER: [ClassName]
- @Observable: [present/missing]
- @MainActor: [present/missing]
- final: [present/missing]
- private(set) properties: [count/total]
- Service protocol: [present/missing]
- Task tracking: [present/missing]
- deinit cleanup: [present/missing]
- Overall: [PASS/FAIL]
```

### 2. Service Layer Compliance

**Required pattern:**
```swift
protocol FeatureServiceProtocol {
    func fetchData() async throws -> Model
}

actor FeatureService: FeatureServiceProtocol {
    func fetchData() async throws -> Model {
        // Implementation
    }
}
```

**Validation points:**
| Check | Required | Status |
|-------|----------|--------|
| Protocol defined | Yes | ? |
| `actor` type (for async) | Yes | ? |
| No `@MainActor` | Yes | ? |
| Returns structs | Yes | ? |
| No UI state | Yes | ? |

**Report format:**
```
SERVICE: [ServiceName]
- Protocol: [defined/missing]
- Type: [actor/struct/class]
- MainActor isolation: [none/present - violation]
- Return types: [all structs/includes classes]
- Overall: [PASS/FAIL]
```

### 3. View Delegation Pattern

**Required pattern:**
```swift
struct FeatureView: View {
    @State private var controller = FeatureController()

    var body: some View {
        Content()
            .task {
                await controller.load()
            }
    }
}
```

**Validation points:**
| Check | Required | Status |
|-------|----------|--------|
| `@State private var controller` | Yes | ? |
| No direct service calls | Yes | ? |
| No controller property mutation | Yes | ? |
| `.task` for async operations | Recommended | ? |

**Report format:**
```
VIEW: [ViewName]
- Controller as @State: [yes/no]
- Direct service calls: [none/count - violations]
- Controller property mutations: [none/count - violations]
- Async via .task: [yes/no]
- Overall: [PASS/FAIL]
```

### 4. Task Cancellation Discipline

**Required pattern:**
```swift
func load() async {
    loadTask?.cancel()  // Cancel previous

    loadTask = Task {
        isLoading = true
        defer { isLoading = false }

        do {
            data = try await service.fetch()
        } catch {
            if !Task.isCancelled {  // Check before error state
                errorMessage = error.localizedDescription
            }
        }
    }

    await loadTask?.value
}
```

**Validation points:**
| Check | Required | Status |
|-------|----------|--------|
| Previous task cancelled | Yes | ? |
| `Task.isCancelled` check | Yes | ? |
| `defer` for loading state | Recommended | ? |
| `await loadTask?.value` | Recommended | ? |

**Report format:**
```
TASK CANCELLATION: [MethodName]
- Previous cancellation: [present/missing]
- isCancelled check: [present/missing]
- defer for state: [present/missing]
- await completion: [present/missing]
- Overall: [PASS/FAIL]
```

### 5. Model Layer Compliance

**Required pattern:**
```swift
struct Model: Equatable {
    let id: String
    let name: String

    // Computed properties for business logic
    var displayName: String {
        name.isEmpty ? "Unknown" : name
    }
}

// Add Codable ONLY when needed:
// - Persisted to disk
// - Encoded/decoded for caching
// - Serialized within next sprint
```

**Validation points:**
| Check | Required | Status |
|-------|----------|--------|
| `struct` type | Yes | ? |
| `Equatable` | Yes | ? |
| No `@Published` | Yes | ? |
| No async code | Yes | ? |
| `Codable` justified | If present | ? |

**Report format:**
```
MODEL: [ModelName]
- Type: [struct/class - if class, violation]
- Equatable: [present/missing]
- @Published: [none/present - violation]
- Async code: [none/present - violation]
- Codable: [present - justified?/absent]
- Overall: [PASS/FAIL]
```

### 6. Layer Separation

**Check:** No cross-layer violations.

| From | To | Allowed |
|------|----|----|
| View | Controller | Yes |
| View | Service | No |
| View | Model | Read only |
| Controller | Service | Yes |
| Controller | Model | Yes |
| Service | Controller | No |
| Service | Model | Yes |
| Model | Any | No (pure data) |

**Report format:**
```
LAYER SEPARATION: [PASS/FAIL]
- View → Service calls: [none/count - violations]
- Service → Controller access: [none/count - violations]
- Model with dependencies: [none/count - violations]
```

### 7. Navigation Pattern

**Required pattern:**
```swift
// Controller owns intent
@Observable
@MainActor
final class FeatureController {
    private(set) var navigationDestination: Destination?

    enum Destination: Hashable {
        case detail(id: String)
        case settings
    }

    func navigate(to destination: Destination) {
        navigationDestination = destination
    }
}

// View owns mechanism
struct FeatureView: View {
    @State private var controller = FeatureController()
    @State private var path = NavigationPath()

    var body: some View {
        NavigationStack(path: $path) {
            Content()
                .onChange(of: controller.navigationDestination) { _, new in
                    if let destination = new {
                        path.append(destination)
                        controller.clearNavigation()
                    }
                }
        }
    }
}
```

**Validation points:**
| Check | Required | Status |
|-------|----------|--------|
| Controller owns Destination enum | Yes | ? |
| View owns NavigationPath | Yes | ? |
| Controller never mutates path | Yes | ? |

---

## Validation Output Format

```markdown
## SwiftUI Pattern Validation: [Feature Name]

### Summary
- Overall: [PASS/NEEDS WORK/FAIL]
- Issues found: [count]
- Critical: [count]

### Controllers
[details per controller]

### Services
[details per service]

### Views
[details per view]

### Models
[details per model]

### Layer Separation
[details]

### Navigation
[details]

### Critical Issues (must fix)
1. [list]

### Warnings (should fix)
1. [list]

### Recommendations
1. [list]
```

---

## Severity Levels

| Level | Criteria | Action |
|-------|----------|--------|
| Critical | Missing @MainActor on Controller, View calls Service, missing task cancellation | Block PR |
| Warning | Missing protocol on Service, class instead of struct for Model | Address before shipping |
| Info | Missing @State on Controller var, could use defer | Optional improvement |

---

## Quick Reference: What Goes Where

```
Feature needs...                  → Create...
─────────────────────────────────────────────
Data structure with business logic → Model (struct)
Async operation (API, database)   → Service (actor + protocol)
UI state or service coordination  → Controller (@Observable class)
Display UI or handle user input   → View (SwiftUI)
```

---

## Dependencies

**Required context:**
- `/Users/coreyyoung/Desktop/Projects/athlead/docs/swift-conventions.md` - Source of truth for patterns

**Related skills:**
- `swift-mvc` - Detailed architecture patterns
- `swift-concurrency-auditor` - Concurrency-specific validation
- `ios-liquid-glass-reviewer` - UI-specific validation
