# SwiftData Core Rules

**Part of:** [ios-swift](../SKILL.md) > SwiftData

Adapted from [twostraws/SwiftData-Agent-Skill](https://github.com/twostraws/SwiftData-Agent-Skill) (Paul Hudson, MIT).

---

## Autosaving and Persistence

- SwiftData autosaves unpredictably. Always call `save()` explicitly when correctness matters.
- No need to check `modelContext.hasChanges` before saving — just call `save()` directly.

## ModelContext and Concurrency

- `ModelContext` and model instances must **never** cross actor boundaries.
- `ModelContainer` and `PersistentIdentifier` **are** `Sendable`.
- To transfer a model across actors: send its `PersistentIdentifier`, then re-fetch in the destination context.

## Relationships

- Place `@Relationship` on **one side only**. Using it on both sides causes circular references.
- SwiftData frequently gets inverse relationships wrong — always specify the exact inverse explicitly:
  ```swift
  @Relationship(inverse: \Child.parent) var children: [Child]
  ```
- Always set an explicit delete rule. Default is `.nullify`, which can leave orphaned objects or crash on non-optional properties:
  ```swift
  @Relationship(deleteRule: .cascade) var items: [Item]
  ```

## Identifiers

- Persistent identifiers are **temporary** before first save (start with lowercase "t").
- A model gets a new permanent ID after its first `save()`. Always save before relying on an ID.

## Property Restrictions

- Do **not** use the property name `description` in any `@Model` class — explicitly disallowed.
- Do **not** add property observers to `@Model` classes — they are silently ignored.
- `@Attribute(.externalStorage)` is a *suggestion*, not a requirement. Only applies to `Data` properties.

## @Transient

- `@Transient` properties are not persisted and **must** have a default value.
- They reset to the default on every fetch.
- If the value derives from stored properties, prefer a computed property instead.
- Use `@Transient` only for values expensive to produce.

## @Query

- `@Query` only works **inside SwiftUI views**. It will not operate correctly elsewhere.
- For count-only queries, use `ModelContext.fetchCount()` with a `FetchDescriptor`. Note: this does not live-update unless something else triggers a refresh.

## FetchDescriptor Optimization

- Set `relationshipKeyPathsForPrefetching` when you know certain relationships will be used — more efficient than lazy fetching.
- Set `propertiesToFetch` to load only needed properties (fetches all by default).

## Uniqueness Constraints

- Only one `#Unique` per model class. For multiple constraints, pass separate key path arrays:
  ```swift
  #Unique<User>([\.email], [\.username])
  ```

## Enums

- Enum properties stored in a model must conform to `Codable`.
- Enums with associated values **are** supported (despite what some tools claim).

## Migrations

- Always have a migration schema in place, even for lightweight migrations.
