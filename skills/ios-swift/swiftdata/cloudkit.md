# SwiftData with CloudKit

**Part of:** [ios-swift](../SKILL.md) > SwiftData

Adapted from [twostraws/SwiftData-Agent-Skill](https://github.com/twostraws/SwiftData-Agent-Skill) (Paul Hudson, MIT).

---

**These rules only apply if the project uses SwiftData with CloudKit.**

## Hard Constraints

- **Never** use `@Attribute(.unique)` or `#Unique` — not supported in CloudKit. When used, local data fails too.
- All model properties must have default values **or** be optional.
- All relationships must be optional.

## Supported Features

- Indexes are supported (with correct OS release).
- Subclasses are supported (with correct OS release).

## Design Principle

CloudKit is designed for **eventual consistency**. All SwiftData code with CloudKit must function correctly even if data has not yet synchronized.
