# SwiftUI Pattern Validation

**Part of:** [ios-swift](../SKILL.md) > Review

**Trigger:** After writing new SwiftUI features, before PR review for iOS code, asking "is my architecture correct?", reviewing Controllers/Services/Views, checking for proper layer separation, validating async/await patterns, implementing new features.

---

## Validation Checklist

### 1. Controller Class Structure

**Required pattern with strict ordering:**
```swift
@Observable
@MainActor
final class FeatureController {
    // MARK: - Published State
    private(set) var data: Model?
    private(set) var isLoading = false
    private(set) var errorMessage: String?

    // MARK: - Internal State
    private var hasLoadedInitialData = false

    // MARK: - Dependencies
    private let service: ServiceProtocol

    // MARK: - Tasks
    private var loadTask: Task<Void, Never>?

    // MARK: - Initialization
    init(service: ServiceProtocol = Service()) {
        self.service = service
    }

    // MARK: - Public Methods
    func load() async {
        loadTask?.cancel()
        loadTask = Task {
            isLoading = true
            defer { isLoading = false }

            do {
                data = try await service.fetch()
            } catch {
                if !Task.isCancelled {
                    errorMessage = error.localizedDescription
                }
            }
        }
        await loadTask?.value
    }

    // MARK: - Private Methods
    private func processData(_ raw: RawModel) -> Model {
        // Transform logic
    }

    // MARK: - Cleanup
    deinit {
        loadTask?.cancel()
    }
}
```

**Required property order within controllers:**

1. Published state (`private(set) var` -- properties the View reads)
2. Internal state (`private var` -- non-published tracking state)
3. Dependencies (`private let` -- services, injected values)
4. Tasks (`private var loadTask: Task<Void, Never>?`)
5. Initialization (`init`)
6. Public methods (`func` -- called by Views)
7. Private methods (`private func` -- internal helpers)
8. Cleanup (`deinit`)

**Validation points:**
| Check | Required | Status |
|-------|----------|--------|
| `@Observable` | Yes | ? |
| `@MainActor` | Yes | ? |
| `final class` | Yes | ? |
| `private(set)` on published state | Yes | ? |
| Protocol-based service dependency | Yes | ? |
| Task tracking variable | Yes | ? |
| `deinit` with cancel | Yes | ? |
| Published state before dependencies | Yes | ? |
| Dependencies before init | Yes | ? |
| init before public methods | Yes | ? |
| Public methods before private methods | Yes | ? |
| deinit last | Yes | ? |
| `// MARK:` section comments | Recommended | ? |

**MARK comment template (recommended):**
```swift
// MARK: - Published State
// MARK: - Internal State
// MARK: - Dependencies
// MARK: - Tasks
// MARK: - Initialization
// MARK: - Public Methods
// MARK: - Private Methods
// MARK: - Cleanup
```

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
- Property ordering: [correct/violations listed]
- MARK comments: [present/missing]
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

**Required pattern with strict ordering:**
```swift
struct User: Codable, Equatable {
    // MARK: - Properties
    let id: String
    let name: String
    let email: String
    let createdAt: Date

    // MARK: - Computed Properties
    var displayName: String {
        name.isEmpty ? email : name
    }

    // MARK: - Static Methods
    static func placeholder() -> User {
        User(id: "", name: "Loading...", email: "", createdAt: .now)
    }
}
```

**Required property order within models:**

1. Stored properties (`let` / `var`)
2. Computed properties (`var { get }`)
3. Static methods/properties
4. Custom `init` (if needed beyond memberwise)
5. Nested types (`enum`, `struct`)

**Validation points:**
| Check | Required | Status |
|-------|----------|--------|
| `struct` type | Yes | ? |
| `Equatable` | Yes | ? |
| No `@Published` | Yes | ? |
| No async code | Yes | ? |
| `Codable` justified | If present | ? |
| Stored properties first | Yes | ? |
| Computed after stored | Yes | ? |
| Static methods after instance | Yes | ? |
| `// MARK:` section comments | Recommended | ? |

**Report format:**
```
MODEL: [ModelName]
- Type: [struct/class - if class, violation]
- Equatable: [present/missing]
- @Published: [none/present - violation]
- Async code: [none/present - violation]
- Codable: [present - justified?/absent]
- Property ordering: [correct/violations listed]
- MARK comments: [present/missing]
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
- View -> Service calls: [none/count - violations]
- Service -> Controller access: [none/count - violations]
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

### 8. View Property Ordering

**Required order within any `View` struct:**

1. `@Environment` / `@EnvironmentObject` properties
2. `@State` / `@Binding` / `@FocusState` properties
3. Regular properties (`let` / `var`)
4. Computed properties
5. `init` (if needed)
6. `body`
7. Helper views (`@ViewBuilder private var`)
8. Helper functions (`private func`)

**Required pattern:**
```swift
struct FeatureView: View {
    // MARK: - Environment
    @Environment(\.dismiss) private var dismiss
    @Environment(UserSession.self) private var userSession

    // MARK: - State
    @State private var controller = FeatureController()
    @State private var isExpanded = false
    @Binding var selectedItem: Item?
    @FocusState private var isFocused: Bool

    // MARK: - Properties
    let title: String
    let items: [Item]

    // MARK: - Computed Properties
    private var filteredItems: [Item] {
        items.filter { $0.isActive }
    }

    // MARK: - Initialization
    init(title: String, items: [Item], selectedItem: Binding<Item?>) {
        self.title = title
        self.items = items
        self._selectedItem = selectedItem
    }

    // MARK: - Body
    var body: some View {
        List(filteredItems) { item in
            itemRow(item)
        }
    }

    // MARK: - Sections
    @ViewBuilder
    private var headerSection: some View {
        Text(title).font(.title)
    }

    // MARK: - Actions
    private func handleTap(_ item: Item) {
        selectedItem = item
    }
}
```

**Validation points:**
| Check | Required | Status |
|-------|----------|--------|
| `@Environment` properties first | Yes | ? |
| `@State`/`@Binding` before regular properties | Yes | ? |
| Regular properties before computed | Yes | ? |
| `init` before `body` | Yes | ? |
| `body` before helper views/functions | Yes | ? |
| `// MARK:` section comments | Recommended | ? |
| No enums/types mixed into property declarations | Yes | ? |

**Report format:**
```
VIEW ORDERING: [ViewName]
- @Environment first: [yes/no]
- @State/@Binding grouped: [yes/no]
- Properties before computed: [yes/no]
- init before body: [yes/no]
- body before helpers: [yes/no]
- MARK comments: [present/missing]
- Types mixed in: [none/count - violations]
- Overall: [PASS/FAIL]
```

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

### Controller Ordering
[details per controller]

### Services
[details per service]

### Views
[details per view]

### View Ordering
[details per view]

### Models
[details per model]

### Model Ordering
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
Feature needs...                  -> Create...
---------------------------------------------
Data structure with business logic -> Model (struct)
Async operation (API, database)   -> Service (actor + protocol)
UI state or service coordination  -> Controller (@Observable class)
Display UI or handle user input   -> View (SwiftUI)
```
