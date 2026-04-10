# SwiftData Predicates

**Part of:** [ios-swift](../SKILL.md) > SwiftData

Adapted from [twostraws/SwiftData-Agent-Skill](https://github.com/twostraws/SwiftData-Agent-Skill) (Paul Hudson, MIT).

---

SwiftData predicates support only a subset of Swift. Some unsupported operations fail to compile; others compile but **crash at runtime**.

## String Matching

Always use `localizedStandardContains()` — never `lowercased().contains()`:

```swift
@Query(filter: #Predicate<Movie> {
    $0.name.localizedStandardContains("titanic")
}) private var movies: [Movie]
```

## hasPrefix / hasSuffix

`hasPrefix()` and `hasSuffix()` are **not supported**. Use `starts(with:)` instead:

```swift
@Query(filter: #Predicate<Website> {
    $0.type.starts(with: "https://apple.com")
}) private var appleLinks: [Website]
```

## Unsupported Operations (Compile Errors)

These common operations have no predicate equivalent:

- `String.hasSuffix()`
- `String.lowercased()`
- `Sequence.map()`
- `Sequence.reduce()`
- `Sequence.count(where:)`
- `Collection.first`
- Custom operators

## Dangerous Operations (Runtime Crashes)

These compile cleanly but fail or crash at runtime:

**`isEmpty` comparisons — use `!` prefix, not `== false`:**
```swift
// CORRECT
#Predicate<Movie> { !$0.cast.isEmpty }

// CRASHES AT RUNTIME
#Predicate<Movie> { $0.cast.isEmpty == false }
```

**Never use in predicates:**
- Computed properties
- `@Transient` properties
- Custom `Codable` struct data
- Regular expressions

All predicates must rely on data actually stored in the database as `@Model` classes.

```swift
// CRASHES AT RUNTIME - regex in predicate
@Query(filter: #Predicate<Movie> {
    $0.name.contains(/Titanic/)
}, sort: \Movie.name)
private var movies: [Movie]
```
