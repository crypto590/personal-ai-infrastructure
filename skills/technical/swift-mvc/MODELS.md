# Models (Immutable Structs)

**Referenced from**: [SKILL.md](SKILL.md), [SERVICES.md](SERVICES.md)

**Related**:
- [SERVICES.md](SERVICES.md) - Services that return Models
- [CONTROLLERS.md](CONTROLLERS.md) - Controllers that use Models

---

## Overview

Models are immutable data structures with computed properties for business logic. They represent the core domain entities of your application.

**Key characteristics:**
- Always `struct`, never `class`
- Always `Codable` for API/persistence
- Always `Equatable` for comparisons
- No async operations
- No `@Published` or Observable
- Business logic in computed properties

---

## Basic Pattern

```swift
struct User: Codable, Equatable {
    let id: String
    let name: String
    let email: String
    let createdAt: Date

    var displayName: String {
        name.isEmpty ? email : name
    }

    var isNew: Bool {
        Date().timeIntervalSince(createdAt) < 86400  // 24 hours
    }
}
```

---

## Rules

### ✅ Always

**1. Use struct**
```swift
// ✅ GOOD
struct User: Codable, Equatable { ... }

// ❌ BAD
class User: Codable { ... }
```

**2. Conform to Codable**
```swift
struct User: Codable, Equatable {
    let id: String
    let name: String
    // Automatically synthesized Codable conformance
}
```

**3. Conform to Equatable**
```swift
struct User: Codable, Equatable {
    let id: String
    let name: String
    // Automatically synthesized Equatable conformance
}
```

**4. Use computed properties for logic**
```swift
struct Order: Codable, Equatable {
    let items: [Item]
    let taxRate: Double

    var subtotal: Double {
        items.reduce(0) { $0 + $1.price }
    }

    var tax: Double {
        subtotal * taxRate
    }

    var total: Double {
        subtotal + tax
    }
}
```

### ❌ Never

**1. Never use async operations**
```swift
// ❌ BAD
struct User {
    func loadProfile() async throws -> Profile { ... }
}

// ✅ GOOD - Put in Service
actor UserService {
    func loadProfile(userId: String) async throws -> Profile { ... }
}
```

**2. Never use @Published or Observable**
```swift
// ❌ BAD
@Observable
struct User {
    var name: String
}

// ✅ GOOD
struct User {
    let name: String
}
```

**3. Never store mutable state**
```swift
// ❌ BAD
struct User {
    var isLoading = false  // UI state!
}

// ✅ GOOD - Put in Controller
@Observable
@MainActor
final class UserController {
    private(set) var isLoading = false
}
```

---

## Patterns

### Nested Types

```swift
struct User: Codable, Equatable {
    let id: String
    let name: String
    let address: Address

    struct Address: Codable, Equatable {
        let street: String
        let city: String
        let state: String
        let zip: String

        var formatted: String {
            "\(street), \(city), \(state) \(zip)"
        }
    }
}
```

### Enums for State

```swift
struct Order: Codable, Equatable {
    let id: String
    let items: [Item]
    let status: Status

    enum Status: String, Codable {
        case pending
        case processing
        case shipped
        case delivered
        case cancelled

        var displayName: String {
            switch self {
            case .pending: return "Pending"
            case .processing: return "Processing"
            case .shipped: return "Shipped"
            case .delivered: return "Delivered"
            case .cancelled: return "Cancelled"
            }
        }

        var isActive: Bool {
            self != .cancelled && self != .delivered
        }
    }

    var canCancel: Bool {
        status == .pending || status == .processing
    }
}
```

### Optional Properties

```swift
struct User: Codable, Equatable {
    let id: String
    let name: String
    let bio: String?
    let avatarURL: URL?

    var hasBio: Bool {
        bio != nil && !bio!.isEmpty
    }

    var hasAvatar: Bool {
        avatarURL != nil
    }
}
```

### Collections

```swift
struct Team: Codable, Equatable {
    let id: String
    let name: String
    let members: [User]

    var memberCount: Int {
        members.count
    }

    var isEmpty: Bool {
        members.isEmpty
    }

    func isMember(_ userId: String) -> Bool {
        members.contains { $0.id == userId }
    }
}
```

---

## Computed Properties Best Practices

### Simple Derived Data

```swift
struct Product: Codable, Equatable {
    let price: Double
    let discountPercentage: Double

    var discountAmount: Double {
        price * (discountPercentage / 100)
    }

    var finalPrice: Double {
        price - discountAmount
    }
}
```

### Formatting

```swift
struct Event: Codable, Equatable {
    let date: Date
    let title: String

    var formattedDate: String {
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        return formatter.string(from: date)
    }

    var timeUntil: String {
        let interval = date.timeIntervalSinceNow
        if interval < 0 {
            return "Past"
        } else if interval < 3600 {
            return "In \(Int(interval / 60)) minutes"
        } else if interval < 86400 {
            return "In \(Int(interval / 3600)) hours"
        } else {
            return "In \(Int(interval / 86400)) days"
        }
    }
}
```

### Validation

```swift
struct SignUpForm: Codable, Equatable {
    let email: String
    let password: String
    let confirmPassword: String

    var isEmailValid: Bool {
        email.contains("@") && email.contains(".")
    }

    var isPasswordValid: Bool {
        password.count >= 8
    }

    var doPasswordsMatch: Bool {
        password == confirmPassword
    }

    var isValid: Bool {
        isEmailValid && isPasswordValid && doPasswordsMatch
    }
}
```

---

## Custom Codable

### Custom Keys

```swift
struct User: Codable, Equatable {
    let id: String
    let name: String
    let emailAddress: String

    enum CodingKeys: String, CodingKey {
        case id
        case name
        case emailAddress = "email"  // API uses "email", we use "emailAddress"
    }
}
```

### Date Decoding

```swift
struct Post: Codable, Equatable {
    let id: String
    let title: String
    let createdAt: Date

    init(id: String, title: String, createdAt: Date) {
        self.id = id
        self.title = title
        self.createdAt = createdAt
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = try container.decode(String.self, forKey: .id)
        title = try container.decode(String.self, forKey: .title)

        // Custom date decoding
        let timestamp = try container.decode(TimeInterval.self, forKey: .createdAt)
        createdAt = Date(timeIntervalSince1970: timestamp)
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(id, forKey: .id)
        try container.encode(title, forKey: .title)
        try container.encode(createdAt.timeIntervalSince1970, forKey: .createdAt)
    }
}
```

---

## Identifiable for SwiftUI

```swift
struct User: Codable, Equatable, Identifiable {
    let id: String
    let name: String
    let email: String
}

// Usage in SwiftUI
List(users) { user in
    Text(user.name)
}
```

---

## Example Models

### User

```swift
struct User: Codable, Equatable, Identifiable {
    let id: String
    let name: String
    let email: String
    let avatarURL: URL?
    let createdAt: Date

    var displayName: String {
        name.isEmpty ? email : name
    }

    var initials: String {
        let components = name.components(separatedBy: " ")
        let initials = components.compactMap { $0.first }.prefix(2)
        return String(initials).uppercased()
    }
}
```

### Post

```swift
struct Post: Codable, Equatable, Identifiable {
    let id: String
    let authorId: String
    let title: String
    let body: String
    let createdAt: Date
    let likes: Int

    var preview: String {
        String(body.prefix(100)) + (body.count > 100 ? "..." : "")
    }

    var formattedDate: String {
        let formatter = RelativeDateTimeFormatter()
        return formatter.localizedString(for: createdAt, relativeTo: Date())
    }
}
```

### API Response

```swift
struct APIResponse<T: Codable>: Codable {
    let data: T
    let meta: Meta

    struct Meta: Codable {
        let page: Int
        let totalPages: Int
        let totalItems: Int

        var hasMore: Bool {
            page < totalPages
        }
    }
}

// Usage
typealias UserListResponse = APIResponse<[User]>
```

---

## Related

- [SERVICES.md](SERVICES.md) - Services that return Models
- [CONTROLLERS.md](CONTROLLERS.md) - Controllers that use Models
- [EXAMPLES.md](EXAMPLES.md) - Real-world Model examples
