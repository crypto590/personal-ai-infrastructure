# Swift Concurrency Audit

**Part of:** [ios-swift](../SKILL.md) > Review

**Trigger:** Before PR review for Swift code with async/await, after implementing services with actor isolation, mentions of Task/async/await/actor/concurrency, reviewing background processing code, checking for potential race conditions, migrating to Swift 6.2 strict concurrency, implementing MainActor-isolated controllers.

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

### 7. `nonisolated(unsafe)` Usage

**Check:** Flag `nonisolated(unsafe)` as a code smell. It disables concurrency checking entirely and almost always indicates an architectural problem.

```swift
// BAD - silences the compiler instead of fixing the issue
nonisolated(unsafe) var sharedConfig: AppConfig = .default

// GOOD - use proper isolation
@MainActor var sharedConfig: AppConfig = .default

// GOOD - or make it Sendable
struct AppConfig: Sendable { ... }
```

**Report format:**
```
NONISOLATED(UNSAFE): [PASS/WARN/FAIL]
- Occurrences found: [count]
- Locations: [list files:lines]
- Recommendation: Replace with proper Sendable conformance or actor isolation
```

### 8. `@unchecked Sendable` Usage

**Check:** Flag `@unchecked Sendable` as a code smell. Prefer proper `Sendable` conformance (value types, actors, or immutable classes).

```swift
// BAD - bypasses compiler safety
final class TokenStore: @unchecked Sendable {
    private var token: String?  // Mutable state, no protection
}

// GOOD - use actor for mutable shared state
actor TokenStore {
    private var token: String?
    func setToken(_ t: String) { token = t }
    func getToken() -> String? { token }
}

// GOOD - immutable class is naturally Sendable
final class AppConstants: Sendable {
    let apiBaseURL: URL
    let appVersion: String
}
```

**Report format:**
```
UNCHECKED SENDABLE: [PASS/WARN/FAIL]
- Occurrences found: [count]
- Locations: [list files:lines]
- Has mutable state: [yes/no per occurrence]
- Recommendation: Convert to actor or make genuinely immutable
```

### 9. Task Group Discipline

**Check:** Prefer `withTaskGroup` / `withThrowingTaskGroup` over spawning multiple bare `Task { }` blocks.

```swift
// BAD - unstructured, no cancellation propagation
func loadDashboard() async {
    Task { await loadProfile() }
    Task { await loadFeed() }
    Task { await loadNotifications() }
    // No way to await all, no error propagation, no cancellation
}

// GOOD - structured concurrency
func loadDashboard() async throws {
    try await withThrowingTaskGroup(of: Void.self) { group in
        group.addTask { try await self.loadProfile() }
        group.addTask { try await self.loadFeed() }
        group.addTask { try await self.loadNotifications() }
        try await group.waitForAll()
    }
}
```

**Report format:**
```
TASK GROUPS: [PASS/WARN]
- Multiple bare Task spawns in same scope: [count]
- Using withTaskGroup: [count]
- Locations needing refactor: [list]
```

### 10. Actor Reentrancy

**Check:** Warn that actors are reentrant — state can change across `await` points within an actor method.

```swift
// DANGEROUS - state may change between await calls
actor CartService {
    var items: [Item] = []

    func addAndCheckout(item: Item) async throws {
        items.append(item)
        // After this await, another caller may have modified items!
        let receipt = try await paymentService.charge(items: items)
        items.removeAll()  // May remove items added by another caller
    }
}

// SAFE - capture state before suspension point
actor CartService {
    var items: [Item] = []

    func addAndCheckout(item: Item) async throws {
        items.append(item)
        let snapshot = items  // Capture before await
        let receipt = try await paymentService.charge(items: snapshot)
        items.removeAll()
    }
}
```

**Report format:**
```
ACTOR REENTRANCY: [PASS/WARN]
- Actor methods with multiple awaits: [count]
- State reads after suspension points: [list]
- Recommendation: Capture state before await, or restructure
```

### 11. Continuation Safety

**Check:** Every path through `withCheckedContinuation` / `withCheckedThrowingContinuation` must resume exactly once.

```swift
// BAD - may never resume (leaks the continuation)
func fetchLegacy() async -> Data {
    await withCheckedContinuation { continuation in
        legacyAPI.fetch { result in
            if case .success(let data) = result {
                continuation.resume(returning: data)
            }
            // Missing: .failure case never resumes!
        }
    }
}

// GOOD - every path resumes
func fetchLegacy() async throws -> Data {
    try await withCheckedThrowingContinuation { continuation in
        legacyAPI.fetch { result in
            switch result {
            case .success(let data):
                continuation.resume(returning: data)
            case .failure(let error):
                continuation.resume(throwing: error)
            }
        }
    }
}
```

**Report format:**
```
CONTINUATION SAFETY: [PASS/FAIL]
- Continuations found: [count]
- All paths resume: [yes/no per occurrence]
- Potential leaks: [list files:lines]
```

### 12. AsyncStream / AsyncSequence Cancellation

**Check:** `AsyncStream` and `AsyncSequence` consumers handle cancellation properly.

```swift
// BAD - no cancellation handling
func observeUpdates() -> AsyncStream<Update> {
    AsyncStream { continuation in
        let observer = NotificationCenter.default.addObserver(...) { notification in
            continuation.yield(Update(notification))
        }
        // Observer never removed on cancellation!
    }
}

// GOOD - cleanup on termination
func observeUpdates() -> AsyncStream<Update> {
    AsyncStream { continuation in
        let observer = NotificationCenter.default.addObserver(...) { notification in
            continuation.yield(Update(notification))
        }
        continuation.onTermination = { _ in
            NotificationCenter.default.removeObserver(observer)
        }
    }
}

// GOOD - check cancellation in async for loops
func processStream(_ stream: AsyncStream<Item>) async {
    for await item in stream {
        guard !Task.isCancelled else { break }
        await process(item)
    }
}
```

**Report format:**
```
ASYNC STREAM CANCELLATION: [PASS/WARN]
- AsyncStreams found: [count]
- With onTermination handler: [count]
- Missing cancellation cleanup: [list files:lines]
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

### Code Smells
- nonisolated(unsafe): [details]
- @unchecked Sendable: [details]

### Task Groups
[details]

### Actor Reentrancy
[details]

### Continuation Safety
[details]

### AsyncStream Cancellation
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
| Critical | Data races, missing MainActor on controllers, continuation leaks (never resumed) | Block PR |
| Warning | Missing task cancellation, heavy work on MainActor, `nonisolated(unsafe)`, `@unchecked Sendable` with mutable state, actor reentrancy hazards, bare Task spawns instead of task groups, missing AsyncStream `onTermination` | Address before shipping |
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
- [ ] Eliminate all `nonisolated(unsafe)` — replace with proper isolation
- [ ] Eliminate all `@unchecked Sendable` — convert to actors or immutable types
- [ ] Replace bare multi-Task spawns with `withTaskGroup`
- [ ] Audit actor methods for reentrancy hazards across `await` points
- [ ] Verify all continuations resume on every code path
- [ ] Add `onTermination` handlers to all `AsyncStream` producers

---

*Concurrency rules inspired by Swift Concurrency Pro community patterns and Apple's Swift 6.2 concurrency documentation.*
