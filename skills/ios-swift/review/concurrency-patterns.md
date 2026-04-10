# Concurrency Deep Patterns

**Part of:** [ios-swift](../SKILL.md) > Review

Adapted from [twostraws/Swift-Concurrency-Agent-Skill](https://github.com/twostraws/Swift-Concurrency-Agent-Skill) (Paul Hudson, MIT).

Supplements `review/concurrency.md` checklist with grep targets, bug patterns, and Swift 6.2 features.

---

## Hotspot Grep Targets

When reviewing, scan for these patterns as priority inspection points:

| Pattern | Why It's Suspicious |
|---|---|
| `DispatchQueue.main.async` | Should be `@MainActor` or Swift concurrency |
| `DispatchQueue.global()` | Should be `@concurrent` or task groups |
| `Task.detached` | Rarely correct. Usually want `@concurrent` or task groups |
| `Task {` inside a loop | Needs task group for cancellation/error propagation |
| `withCheckedContinuation` | Must resume exactly once on every path |
| `withCheckedThrowingContinuation` | Must resume exactly once — audit early returns and thrown errors |
| `AsyncStream` (closure init) | Prefer `AsyncStream.makeStream(of:)` factory |
| `@unchecked Sendable` | Should be very rare. Verify actual thread safety |
| `MainActor.run {}` | May be unnecessary if already on `@MainActor` |
| `!` after `await` on actor state | Actor reentrancy — value may be nil after suspension |

**Note:** GCD is still acceptable in low-level libraries, framework interop, and performance-critical synchronous sections.

---

## Common Bug Patterns

### 1. Actor Reentrancy: Check-Then-Act

State checks become stale after suspension. Concurrent callers may mutate data during `await`.

```swift
// BUG: data[key] may have changed after await
actor Cache {
    var data: [String: Data] = [:]
    func load(_ key: String) async throws -> Data {
        if data[key] == nil {
            data[key] = try await download(key) // other caller can run here
        }
        return data[key]! // crash if another caller set it to nil
    }
}

// FIX: capture result locally, use in-flight tasks to deduplicate
actor Cache {
    var data: [String: Data] = [:]
    var inFlight: [String: Task<Data, Error>] = [:]

    func load(_ key: String) async throws -> Data {
        if let existing = data[key] { return existing }
        if let task = inFlight[key] { return try await task.value }

        let task = Task { try await download(key) }
        inFlight[key] = task
        defer { inFlight[key] = nil }

        let result = try await task.value
        data[key] = result
        return result
    }
}
```

### 2. Continuation Resumed Zero Times

Callback never fires → indefinite hang. Audit every code path. Add timeout if API can silently drop callbacks.

### 3. Continuation Resumed Twice

Multiple callbacks resume the same continuation → runtime trap. Guard with a `Bool` flag or use an actor to serialize.

### 4. Unstructured Tasks in a Loop

```swift
// BUG: no cancellation, no error collection, no completion tracking
for item in items { Task { await process(item) } }

// FIX: use task groups
try await withThrowingTaskGroup(of: Void.self) { group in
    for item in items {
        group.addTask { try await process(item) }
    }
}
```

### 5. Swallowed Errors in Task Closures

`Task { try await riskyWork() }` silently loses thrown errors. Always catch and surface:

```swift
Task {
    do {
        try await riskyWork()
    } catch is CancellationError {
        // Normal lifecycle — do nothing
    } catch {
        self.errorMessage = error.localizedDescription
    }
}
```

### 6. Blocking the Main Actor

CPU-intensive work on `@MainActor` freezes UI. Move to `@concurrent` function, or `Task.detached` as last resort.

### 7. Unbounded AsyncStream Buffer

High-throughput producers exhaust memory. Specify buffering policy:

```swift
let (stream, continuation) = AsyncStream.makeStream(
    of: SensorReading.self,
    bufferingPolicy: .bufferingNewest(100)
)
```

### 8. Ignoring CancellationError

Catch blocks treating cancellation as an error show alerts for normal lifecycle events. Always catch `CancellationError` separately.

### 9. @unchecked Sendable Hiding Races

Suppresses compiler errors while mutable properties remain unsynchronized. Restructure to value types, actor, or proper locking.

---

## AsyncStream Best Practices

### Factory Pattern

Always use `makeStream(of:)` — eliminates captured continuation in closures:

```swift
let (stream, continuation) = AsyncStream.makeStream(of: Event.self)
```

### Cleanup

```swift
let monitor = NetworkMonitor()
monitor.onEvent = { event in continuation.yield(event) }
monitor.onComplete = { continuation.finish() }
continuation.onTermination = { _ in monitor.stop() }
```

### Buffering Policies

| Policy | Behavior |
|---|---|
| `.unbounded` (default) | Keeps all items — risky with fast producers |
| `.bufferingNewest(n)` | Keeps most recent n, discards older |
| `.bufferingOldest(n)` | Keeps first n, discards newer |

---

## Actor Isolation Propagation

`@MainActor` **propagates to:**
- Subclasses of annotated classes
- Property wrapper stored values
- Protocol conformance (entire type inherits)
- Type extensions

`@MainActor` **does NOT propagate to:**
- Closures passed to non-isolated functions

### Debugging Isolation

Use `assertIsolated()` — halts debug builds if running outside expected actor. Compiles out for release.

---

## Swift 6.2 Concurrency Features

### Default Main Actor Isolation

Modules can opt into `@MainActor` isolation by default. All declarations behave as `@MainActor` unless explicitly opted out. Per-module setting — neighboring modules can differ.

**Common misconception:** Main Actor isolation does NOT block networking. Suspending I/O (`URLSession.shared.data(from:)`) still runs off the main thread.

### Isolated Conformances

Protocol conformances can specify actor isolation:

```swift
@MainActor
class User: @MainActor Equatable {
    static func ==(lhs: User, rhs: User) -> Bool {
        lhs.id == rhs.id
    }
}
```

Compiler rejects calls from wrong isolation domain.

### Nonisolated Async Functions Stay on Caller's Actor

`nonisolated` async functions now run on the caller's actor by default (previously auto-hopped). Use `@concurrent` to explicitly offload.

### @concurrent

Opt-in attribute to run code on the concurrent pool:

```swift
@concurrent
func analyzeReadings(_ readings: [Double]) async -> AnalysisResult { ... }
```

Best for CPU-heavy work: parsing, image processing, compression, large transforms. Not needed for ordinary async I/O.

### Task.immediate

Executes immediately if caller is already on target executor:

```swift
Task.immediate {
    // runs synchronously until first suspension point
    print("Immediate")
}
```

Still an unstructured task after the first suspension. Also available: `addImmediateTask()` for task groups.

### Isolated Deinit

Deinitializers can run on the class's actor:

```swift
@MainActor class Session {
    isolated deinit {
        user.isLoggedIn = false // safe: runs on main actor
    }
}
```

Without `isolated`, deinit runs outside the actor and cannot access isolated state.

### Task Naming

Debug aid for logs, tracing, and failure diagnosis:

```swift
let task = Task(name: "FetchUser") {
    print("Running: \(Task.name ?? "?")")
}

// In task groups
group.addTask(name: "Story-\(i)") { ... }
```

### Priority Escalation APIs

```swift
let task = Task(priority: .medium) {
    try await withTaskPriorityEscalationHandler {
        try await fetchData()
    } onPriorityEscalated: { old, new in
        print("Escalated to \(new)")
    }
}
task.escalatePriority(to: .high)
```

Usually automatic — manual escalation is advanced usage.

---

## Strict Concurrency Diagnostics

Common compiler errors when enabling strict concurrency, and how to fix them:

### "Sending 'x' risks causing data races"

Value crosses isolation boundaries while remaining accessible from the original context.

**Fix progression:**
1. Check if region-based isolation already resolves it (Swift 6.2)
2. Use `sending` parameters
3. Make the type conform to `Sendable`
4. Mark function `nonisolated(nonsending)` if appropriate
5. `@unchecked Sendable` as last resort (must verify thread safety)

### "Static property 'x' is not concurrency-safe"

Global or static variables lack isolation protection.

**Fix:** `@MainActor` annotation (most common). For immutable types, add `Sendable` conformance. For verified immutable state, `nonisolated(unsafe)`.

### "Capture of 'x' with non-sendable type in a @Sendable closure"

Closures crossing boundaries capture non-Sendable values.

**Fix:** Make the captured type `Sendable`, restructure to pass data as parameters, keep work on the caller's actor, or use `sending` parameters.

### "Conformance crosses into main actor-isolated code"

Protocol-type boundary mismatch.

**Fix:** Remove isolation from the type, or use `@MainActor` protocol conformance (Swift 6.2 isolated conformances).

### "Expression is 'async' but is not marked with 'await'"

Calls crossing isolation boundaries need `await` or must be wrapped in `Task {}`.

### "Main actor-isolated conformance cannot be used in nonisolated context"

Move usage onto the matching actor, or remove isolation from the conformance if protocol methods don't require actor protection.
