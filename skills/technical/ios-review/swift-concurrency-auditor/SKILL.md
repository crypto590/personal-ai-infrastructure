---
name: swift-concurrency-auditor
description: Audit Swift async/await patterns for Swift 6.2 compliance. Checks actor isolation, @concurrent usage, race conditions, Task cancellation, and Sendable conformance. NOT for UI layout review, accessibility audits, or architecture validation.
compatibility: "Requires macOS with Xcode 16+ and Swift 6.2+"
context: fork
metadata:
  author: coreyyoung
  version: 1.0.0
  category: technical
  tags: [swift, concurrency, async-await, actors, sendable, code-review]
---

# Swift Concurrency Auditor

**Category:** technical/ios-review

**Brief Description:** Code review agent that audits Swift concurrency patterns for correctness and Swift 6.2 compliance. Validates actor isolation, @concurrent attribute usage, data race safety, Task cancellation discipline, and Sendable conformance.

---

## When to Use This Skill

Trigger this skill when:
- Before PR review for Swift code with async/await
- After implementing services with actor isolation
- User mentions Task, async, await, actor, or concurrency
- Reviewing background processing code
- Checking for potential race conditions
- Migrating to Swift 6.2 strict concurrency
- Implementing MainActor-isolated controllers

---

## Audit Checklist

### 1. Actor Isolation

**Check:** Proper actor usage and isolation boundaries.

```swift
// GOOD - Service as actor
actor UserService: UserServiceProtocol {
    func fetchUser(id: String) async throws -> User {
        // Isolated state access
    }
}

// BAD - Class with shared mutable state
class UserService {  // VIOLATION - should be actor
    var cache: [String: User] = [:]  // Shared mutable state
    func fetchUser(id: String) async throws -> User { ... }
}
```

**Report format:**
```
ACTOR ISOLATION: [PASS/WARN/FAIL]
- Actors found: [count]
- Classes with mutable state: [count]
- Isolation violations: [list]
- Recommendation: [if applicable]
```

### 2. MainActor Controllers

**Check:** Controllers properly MainActor-isolated.

```swift
// REQUIRED pattern
@Observable
@MainActor
final class FeatureController {
    private(set) var state: State  // UI state on MainActor
}

// VIOLATION - missing MainActor
@Observable
class FeatureController {  // Missing @MainActor
    private(set) var state: State
}
```

**Report format:**
```
MAINACTOR CONTROLLERS: [PASS/FAIL]
- Controllers found: [count]
- Properly isolated: [count]
- Missing @MainActor: [list files:lines]
```

### 3. @concurrent Usage (Swift 6.2)

**Check:** Background work explicitly marked with @concurrent.

```swift
// GOOD - explicit background execution
@concurrent
func processLargeDataset(data: [Item]) async -> Summary {
    // Guaranteed background thread
}

// SUSPICIOUS - heavy work without @concurrent
func processLargeDataset(data: [Item]) async -> Summary {
    // May run on MainActor, blocking UI
}
```

**Report format:**
```
BACKGROUND EXECUTION: [PASS/WARN]
- @concurrent functions: [count]
- Potentially heavy operations without @concurrent: [list]
- Recommendation: [if applicable]
```

### 4. Task Cancellation Discipline

**Check:** Tasks properly tracked and cancelled.

```swift
// REQUIRED pattern
@Observable
@MainActor
final class Controller {
    private var loadTask: Task<Void, Never>?

    func load() async {
        loadTask?.cancel()  // Cancel previous
        loadTask = Task {
            // ... work ...
            if !Task.isCancelled {  // Check before state update
                self.data = result
            }
        }
        await loadTask?.value
    }

    deinit {
        loadTask?.cancel()  // Cleanup
    }
}

// VIOLATIONS to detect:
// - No task tracking variable
// - No cancellation of previous task
// - No Task.isCancelled check before state update
// - No deinit cleanup
```

**Report format:**
```
TASK CANCELLATION: [PASS/FAIL]
- Controllers with async operations: [count]
- Properly tracking tasks: [count]
- Missing cancellation checks: [list]
- Missing deinit cleanup: [list]
```

### 5. Sendable Conformance

**Check:** Types crossing concurrency boundaries are Sendable.

```swift
// GOOD - Sendable struct
struct User: Sendable {
    let id: String
    let name: String
}

// BAD - Non-Sendable class crossing boundary
class UserCache {  // Not Sendable
    var users: [User] = []
}

actor UserService {
    func getUsers() async -> UserCache {  // VIOLATION
        // Returning non-Sendable type from actor
    }
}
```

**Report format:**
```
SENDABLE CONFORMANCE: [PASS/WARN/FAIL]
- Types crossing boundaries: [count]
- Sendable types: [count]
- Non-Sendable violations: [list]
- Classes that should be structs: [list]
```

### 6. Data Race Detection

**Check:** No shared mutable state accessed from multiple contexts.

```swift
// VIOLATION patterns to detect:

// 1. Captured mutable variable
var counter = 0
Task {
    counter += 1  // Race condition
}

// 2. Non-isolated access
class SharedState {
    var value = 0  // Accessed from multiple threads
}

// 3. nonisolated access to actor state
actor DataStore {
    var data: [String] = []

    nonisolated func unsafeRead() -> [String] {
        data  // VIOLATION - nonisolated access to isolated state
    }
}
```

**Report format:**
```
DATA RACES: [PASS/WARN/FAIL]
- Potential races detected: [count]
- Captured mutable variables: [list]
- Unsafe nonisolated access: [list]
- Recommendation: [if applicable]
```

---

## Audit Output Format

```markdown
## Swift Concurrency Audit: [Feature/File Name]

### Summary
- Overall: [PASS/NEEDS WORK/FAIL]
- Issues found: [count]
- Critical (data races): [count]

### Actor Isolation
[details]

### MainActor Controllers
[details]

### Background Execution
[details]

### Task Cancellation
[details]

### Sendable Conformance
[details]

### Data Race Analysis
[details]

### Recommendations
1. [ordered by severity]
2. ...

### Migration Steps (if needed)
[Swift 6.2 migration guidance]
```

---

## Severity Levels

| Level | Criteria | Action |
|-------|----------|--------|
| Critical | Data races, missing MainActor on controllers | Block PR |
| Warning | Missing task cancellation, heavy work on MainActor | Address before shipping |
| Info | @concurrent opportunities, optimization suggestions | Optional improvement |

---

## Swift 6.2 Migration Checklist

When auditing for Swift 6.2 compatibility:

- [ ] Enable strict concurrency checking
- [ ] Add `@MainActor` to all controllers
- [ ] Mark heavy computation with `@concurrent`
- [ ] Verify all Task closures are Sendable
- [ ] Check isolated conformances on protocols
- [ ] Audit `nonisolated` usage

---

## Dependencies

**Required context:**
- `/Users/coreyyoung/Desktop/Projects/athlead/docs/swift-conventions.md`
- `/Users/coreyyoung/Desktop/Projects/athlead/docs/swift-best-practices.md`

**Related skills:**
- `swift-mvc` - Architecture patterns
- `swiftui-pattern-validator` - General SwiftUI patterns
