# SwiftData Class Inheritance

**Part of:** [ios-swift](../SKILL.md) > SwiftData

Adapted from [twostraws/SwiftData-Agent-Skill](https://github.com/twostraws/SwiftData-Agent-Skill) (Paul Hudson, MIT).

---

## Availability

iOS 26+ and coordinated releases. Not a common feature — only use if it provides clear benefit. Protocols are often simpler.

## Basic Pattern

Both parent and child classes must use `@Model`. Child classes must be marked `@available` for a 26 release, **even if iOS 26 is the minimum deployment target**:

```swift
@Model class Article {
    var type: String

    init(type: String) {
        self.type = type
    }
}

@available(iOS 26, *)
@Model class Tutorial: Article {
    var difficulty: Int

    init(difficulty: Int) {
        self.difficulty = difficulty
        super.init(type: "Tutorial")
    }
}

@available(iOS 26, *)
@Model class News: Article {
    var topic: String

    init(topic: String) {
        self.topic = topic
        super.init(type: "News")
    }
}
```

## Model Container Setup

List **both** parent and child classes when creating the container — SwiftData cannot infer the connection:

```swift
let schema = Schema([Article.self, Tutorial.self, News.self])
```

## Relationships with Subclasses

A relationship to a parent class may contain **any** subclass:

```swift
@Model class Magazine {
    @Relationship(deleteRule: .cascade) var articles: [Article]
    // articles may contain Article, Tutorial, or News instances
}
```

Avoid deep subclassing hierarchies — they complicate migrations.

## Querying Subclasses

Load only a specific subclass:
```swift
@Query private var tutorials: [Tutorial]
```

Load the parent class to get **all** children:
```swift
@Query private var articles: [Article]
```

Filter specific children with `is`:
```swift
@Query(filter: #Predicate<Article> {
    $0 is Tutorial || $0 is News
}) private var tutorialsAndNews: [Article]
```

Typecast in predicates to filter by child properties:
```swift
@Query(filter: #Predicate<Article> { article in
    if let tutorial = article as? Tutorial {
        tutorial.difficulty < 3
    } else if let news = article as? News {
        news.topic == "General"
    } else {
        false
    }
}) private var frontPageArticles: [Article]
```

The resulting array is typed as `[Article]` — use standard Swift typecasting to access child properties.
