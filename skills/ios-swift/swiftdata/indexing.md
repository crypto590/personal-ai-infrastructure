# SwiftData Indexing

**Part of:** [ios-swift](../SKILL.md) > SwiftData

Adapted from [twostraws/SwiftData-Agent-Skill](https://github.com/twostraws/SwiftData-Agent-Skill) (Paul Hudson, MIT).

---

## Availability

iOS 18+ and coordinated releases (macOS 15+, etc.).

## When to Use

- Indexes speed up queries but have a small write-time cost.
- **Good for:** frequently queried, rarely updated data.
- **Bad for:** write-heavy data like logging.

## Single Property Indexes

```swift
@Model class Article {
    #Index<Article>([\.type], [\.author])

    var type: String
    var author: String
    var publishDate: Date

    init(type: String, author: String, publishDate: Date) {
        self.type = type
        self.author = author
        self.publishDate = publishDate
    }
}
```

## Compound Indexes

Mix single properties and groups when they're commonly queried together:

```swift
#Index<Article>([\.type], [\.type, \.author])
```
