# Services (Actors and Structs)

**Referenced from**: [SKILL.md](SKILL.md), [CONTROLLERS.md](CONTROLLERS.md)

**Related**:
- [CONTROLLERS.md](CONTROLLERS.md) - Controllers that use Services
- [MODELS.md](MODELS.md) - Models that Services return
- [TESTING.md](TESTING.md) - Testing with mock Services

---

## Overview

Services are the infrastructure layer. They handle async operations like network calls, database queries, and SDK interactions. Services are stateless (except for caching) and always protocol-based for testability.

**Key characteristics:**
- Use `actor` for async operations and shared state
- Use `struct` with static methods for pure functions
- Always define a protocol for testability
- No UI or business state (caching is acceptable)
- Return Models, never Controllers
- Never `@MainActor` (background execution only)
- Never `class` (prevents accidental shared mutable state)

---

## Actor vs Struct Decision Tree

```
Is the service performing async operations?
├─ YES → Is it managing shared mutable state?
│   ├─ YES → Use ACTOR
│   └─ NO → Use ACTOR (for consistent async patterns)
│
└─ NO → Is it a pure function or utility?
    └─ YES → Use STRUCT with static methods
```

### When to Use Actor

**Use actor when:**
- ✅ Making network calls
- ✅ Performing database operations
- ✅ Interacting with async SDKs
- ✅ Managing caches or shared state
- ✅ Any async operation that could cause race conditions

**Example:**
```swift
actor NetworkService {
    func fetchData() async throws -> Data
}

actor DatabaseService {
    func save(_ item: Item) async throws
}

actor CacheService {
    private var cache: [String: Data] = [:]

    func get(key: String) -> Data? {
        cache[key]
    }

    func set(key: String, value: Data) {
        cache[key] = value
    }
}
```

### When to Use Struct

**Use struct when:**
- ✅ Pure functions with no side effects
- ✅ Synchronous utilities
- ✅ Simple data transformations
- ✅ Validation logic

**Example:**
```swift
struct ValidationService {
    static func isValidEmail(_ email: String) -> Bool {
        email.contains("@") && email.contains(".")
    }

    static func isValidPassword(_ password: String) -> Bool {
        password.count >= 8
    }
}

struct FormattingService {
    static func formatCurrency(_ amount: Double) -> String {
        let formatter = NumberFormatter()
        formatter.numberStyle = .currency
        return formatter.string(from: NSNumber(value: amount)) ?? ""
    }
}
```

---

## Protocol-Based Design

### Basic Pattern

```swift
// 1. Define protocol
protocol UserServiceProtocol {
    func fetchUser(id: String) async throws -> User
    func updateUser(_ user: User) async throws
}

// 2. Implement with actor
actor UserService: UserServiceProtocol {
    func fetchUser(id: String) async throws -> User {
        try await APIClient.shared.get("/users/\(id)")
    }

    func updateUser(_ user: User) async throws {
        try await APIClient.shared.put("/users/\(user.id)", body: user)
    }
}
```

### Why Protocols?

**Testability:**
```swift
// Production: Real service
let controller = UserController(service: UserService())

// Testing: Mock service
let controller = UserController(service: MockUserService())
```

**Swappable implementations:**
```swift
protocol DataServiceProtocol {
    func save(_ item: Item) async throws
}

// Local implementation
actor LocalDataService: DataServiceProtocol { ... }

// Remote implementation
actor RemoteDataService: DataServiceProtocol { ... }

// Use either
let service: DataServiceProtocol = isOnline ? RemoteDataService() : LocalDataService()
```

---

## Actor Service Patterns

### Network Service

```swift
protocol NetworkServiceProtocol {
    func get<T: Decodable>(_ endpoint: String) async throws -> T
    func post<T: Encodable, R: Decodable>(_ endpoint: String, body: T) async throws -> R
}

actor NetworkService: NetworkServiceProtocol {
    private let baseURL: URL

    init(baseURL: URL) {
        self.baseURL = baseURL
    }

    func get<T: Decodable>(_ endpoint: String) async throws -> T {
        let url = baseURL.appendingPathComponent(endpoint)
        let (data, _) = try await URLSession.shared.data(from: url)
        return try JSONDecoder().decode(T.self, from: data)
    }

    func post<T: Encodable, R: Decodable>(_ endpoint: String, body: T) async throws -> R {
        let url = baseURL.appendingPathComponent(endpoint)
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.httpBody = try JSONEncoder().encode(body)
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let (data, _) = try await URLSession.shared.data(for: request)
        return try JSONDecoder().decode(R.self, from: data)
    }
}
```

### Database Service

```swift
protocol DatabaseServiceProtocol {
    func fetch<T: Decodable>(query: String) async throws -> [T]
    func save<T: Encodable>(_ item: T) async throws
    func delete(id: String) async throws
}

actor DatabaseService: DatabaseServiceProtocol {
    private let db: Database  // Your database instance

    init(db: Database) {
        self.db = db
    }

    func fetch<T: Decodable>(query: String) async throws -> [T] {
        let results = try await db.execute(query)
        return try results.map { try $0.decode(T.self) }
    }

    func save<T: Encodable>(_ item: T) async throws {
        let data = try JSONEncoder().encode(item)
        try await db.insert(data)
    }

    func delete(id: String) async throws {
        try await db.delete(where: "id = \(id)")
    }
}
```

### Cache Service

```swift
protocol CacheServiceProtocol {
    func get<T: Codable>(key: String) -> T?
    func set<T: Codable>(key: String, value: T)
    func remove(key: String)
    func clear()
}

actor CacheService: CacheServiceProtocol {
    private var cache: [String: Data] = [:]

    func get<T: Codable>(key: String) -> T? {
        guard let data = cache[key] else { return nil }
        return try? JSONDecoder().decode(T.self, from: data)
    }

    func set<T: Codable>(key: String, value: T) {
        guard let data = try? JSONEncoder().encode(value) else { return }
        cache[key] = data
    }

    func remove(key: String) {
        cache.removeValue(forKey: key)
    }

    func clear() {
        cache.removeAll()
    }
}
```

### Authentication Service

```swift
protocol AuthServiceProtocol {
    func signIn(email: String, password: String) async throws -> User
    func signOut() async throws
    func getCurrentUser() async -> User?
}

actor AuthService: AuthServiceProtocol {
    private var currentUser: User?

    func signIn(email: String, password: String) async throws -> User {
        // Call auth API
        let user = try await APIClient.shared.post("/auth/signin", body: [
            "email": email,
            "password": password
        ])

        currentUser = user
        return user
    }

    func signOut() async throws {
        try await APIClient.shared.post("/auth/signout")
        currentUser = nil
    }

    func getCurrentUser() async -> User? {
        currentUser
    }
}
```

---

## Struct Service Patterns

### Validation Service

```swift
protocol ValidationServiceProtocol {
    static func isValidEmail(_ email: String) -> Bool
    static func isValidPassword(_ password: String) -> Bool
    static func isValidURL(_ urlString: String) -> Bool
}

struct ValidationService: ValidationServiceProtocol {
    static func isValidEmail(_ email: String) -> Bool {
        let emailRegex = "[A-Z0-9a-z._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,64}"
        let emailPredicate = NSPredicate(format: "SELF MATCHES %@", emailRegex)
        return emailPredicate.evaluate(with: email)
    }

    static func isValidPassword(_ password: String) -> Bool {
        // At least 8 characters, one uppercase, one lowercase, one number
        password.count >= 8 &&
        password.contains(where: { $0.isUppercase }) &&
        password.contains(where: { $0.isLowercase }) &&
        password.contains(where: { $0.isNumber })
    }

    static func isValidURL(_ urlString: String) -> Bool {
        URL(string: urlString) != nil
    }
}
```

### Formatting Service

```swift
protocol FormattingServiceProtocol {
    static func formatCurrency(_ amount: Double, locale: Locale) -> String
    static func formatDate(_ date: Date, style: DateFormatter.Style) -> String
    static func formatPhone(_ phone: String) -> String
}

struct FormattingService: FormattingServiceProtocol {
    static func formatCurrency(_ amount: Double, locale: Locale = .current) -> String {
        let formatter = NumberFormatter()
        formatter.numberStyle = .currency
        formatter.locale = locale
        return formatter.string(from: NSNumber(value: amount)) ?? ""
    }

    static func formatDate(_ date: Date, style: DateFormatter.Style = .medium) -> String {
        let formatter = DateFormatter()
        formatter.dateStyle = style
        return formatter.string(from: date)
    }

    static func formatPhone(_ phone: String) -> String {
        let cleaned = phone.filter { $0.isNumber }
        guard cleaned.count == 10 else { return phone }

        let areaCode = cleaned.prefix(3)
        let middle = cleaned.dropFirst(3).prefix(3)
        let last = cleaned.suffix(4)

        return "(\(areaCode)) \(middle)-\(last)"
    }
}
```

### Calculation Service

```swift
protocol CalculationServiceProtocol {
    static func calculateTax(amount: Double, rate: Double) -> Double
    static func calculateDiscount(price: Double, percentage: Double) -> Double
}

struct CalculationService: CalculationServiceProtocol {
    static func calculateTax(amount: Double, rate: Double) -> Double {
        amount * rate
    }

    static func calculateDiscount(price: Double, percentage: Double) -> Double {
        price * (1 - percentage / 100)
    }
}
```

---

## Accessing Services from Controllers

### Single Service

```swift
@Observable
@MainActor
final class UserController {
    private(set) var user: User?

    private let service: UserServiceProtocol

    init(service: UserServiceProtocol = UserService()) {
        self.service = service
    }

    func loadUser(id: String) async {
        do {
            user = try await service.fetchUser(id: id)
        } catch {
            // Handle error
        }
    }
}
```

### Multiple Services

```swift
@Observable
@MainActor
final class ProfileController {
    private(set) var user: User?
    private(set) var posts: [Post] = []

    private let userService: UserServiceProtocol
    private let postService: PostServiceProtocol

    init(
        userService: UserServiceProtocol = UserService(),
        postService: PostServiceProtocol = PostService()
    ) {
        self.userService = userService
        self.postService = postService
    }

    func load(userId: String) async {
        async let user = userService.fetchUser(id: userId)
        async let posts = postService.fetchPosts(userId: userId)

        do {
            self.user = try await user
            self.posts = try await posts
        } catch {
            // Handle error
        }
    }
}
```

---

## Service Rules

### ✅ DO

**1. Always use protocols**
```swift
protocol ServiceProtocol { ... }
actor Service: ServiceProtocol { ... }
```

**2. Return Models, not primitives (when appropriate)**
```swift
// ✅ GOOD
func fetchUser(id: String) async throws -> User

// ❌ BAD (unless truly needed)
func fetchUserName(id: String) async throws -> String
```

**3. Use actors for async operations**
```swift
actor APIService {
    func fetch() async throws -> Data { ... }
}
```

**4. Use structs for pure functions**
```swift
struct ValidationService {
    static func validate(_ email: String) -> Bool { ... }
}
```

**5. Keep services focused**
```swift
// ✅ GOOD - Focused
actor UserService: UserServiceProtocol { ... }
actor PostService: PostServiceProtocol { ... }

// ❌ BAD - Too broad
actor APIService {
    func fetchUser() { ... }
    func fetchPosts() { ... }
    func fetchComments() { ... }
}
```

### ❌ DON'T

**1. Never use class for services**
```swift
// ❌ BAD
class UserService { ... }

// ✅ GOOD
actor UserService { ... }
```

**2. Never store UI state in services**
```swift
// ❌ BAD
actor UserService {
    var isLoading = false  // UI state belongs in Controller!
}

// ✅ GOOD
actor UserService {
    private var cache: [String: User] = [:]  // Caching is ok
}
```

**3. Never use @MainActor**
```swift
// ❌ BAD
@MainActor
actor UserService { ... }

// ✅ GOOD
actor UserService { ... }  // Background execution
```

**4. Never return or accept Controllers**
```swift
// ❌ BAD
func fetchData(controller: UserController) async throws

// ✅ GOOD
func fetchData(userId: String) async throws -> User
```

**5. Never import SwiftUI**
```swift
// ❌ BAD
import SwiftUI
actor UserService { ... }

// ✅ GOOD
import Foundation
actor UserService { ... }
```

---

## Service Composition

### Composing Services

Services can depend on other services:

```swift
protocol UserServiceProtocol {
    func fetchUser(id: String) async throws -> User
}

protocol CacheServiceProtocol {
    func get<T: Codable>(key: String) -> T?
    func set<T: Codable>(key: String, value: T)
}

actor UserService: UserServiceProtocol {
    private let api: NetworkServiceProtocol
    private let cache: CacheServiceProtocol

    init(
        api: NetworkServiceProtocol = NetworkService(),
        cache: CacheServiceProtocol = CacheService()
    ) {
        self.api = api
        self.cache = cache
    }

    func fetchUser(id: String) async throws -> User {
        // Check cache first
        if let cached: User = await cache.get(key: "user_\(id)") {
            return cached
        }

        // Fetch from API
        let user: User = try await api.get("/users/\(id)")

        // Cache result
        await cache.set(key: "user_\(id)", value: user)

        return user
    }
}
```

**Benefits:**
- Separation of concerns
- Each service is testable
- Reusable components

---

## Shared Services vs Instance Services

### Shared Service (Singleton)

```swift
actor NetworkService {
    static let shared = NetworkService()

    private init() {}  // Prevent external initialization

    func get<T: Decodable>(_ endpoint: String) async throws -> T {
        // Implementation
    }
}

// Usage
let data: User = try await NetworkService.shared.get("/users/123")
```

**When to use:**
- Service manages shared resources (network client, database connection)
- Only one instance should exist
- No configuration needed

### Instance Service

```swift
protocol UserServiceProtocol {
    func fetchUser(id: String) async throws -> User
}

actor UserService: UserServiceProtocol {
    private let baseURL: URL

    init(baseURL: URL) {
        self.baseURL = baseURL
    }

    func fetchUser(id: String) async throws -> User {
        // Implementation using baseURL
    }
}

// Usage in Controller
@Observable
@MainActor
final class UserController {
    init(service: UserServiceProtocol = UserService(baseURL: .production)) {
        self.service = service
    }
}
```

**When to use:**
- Service needs configuration
- Different instances for testing
- Better for dependency injection

**Recommendation**: Prefer instance services for better testability.

---

## Error Handling in Services

Services throw errors, Controllers handle them.

### Service Layer

```swift
enum NetworkError: LocalizedError {
    case invalidURL
    case noData
    case decodingFailed
    case httpError(statusCode: Int)

    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Invalid URL"
        case .noData:
            return "No data received"
        case .decodingFailed:
            return "Failed to decode response"
        case .httpError(let code):
            return "HTTP error: \(code)"
        }
    }
}

actor NetworkService {
    func get<T: Decodable>(_ endpoint: String) async throws -> T {
        guard let url = URL(string: endpoint) else {
            throw NetworkError.invalidURL
        }

        let (data, response) = try await URLSession.shared.data(from: url)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw NetworkError.noData
        }

        guard (200...299).contains(httpResponse.statusCode) else {
            throw NetworkError.httpError(statusCode: httpResponse.statusCode)
        }

        do {
            return try JSONDecoder().decode(T.self, from: data)
        } catch {
            throw NetworkError.decodingFailed
        }
    }
}
```

### Controller Layer

```swift
@Observable
@MainActor
final class UserController {
    private(set) var errorMessage: String?

    func loadUser(id: String) async {
        do {
            user = try await service.fetchUser(id: id)
        } catch {
            if !Task.isCancelled {
                errorMessage = error.localizedDescription
            }
        }
    }
}
```

**Separation:**
- Services: Define and throw specific errors
- Controllers: Catch and present errors to users

See [ERROR_HANDLING.md](ERROR_HANDLING.md) for complete error patterns.

---

## Testing Services

See [TESTING.md](TESTING.md) for complete testing patterns.

### Mock Services

```swift
actor MockUserService: UserServiceProtocol {
    var shouldFail = false
    var mockUser = User(id: "1", name: "Test", email: "test@test.com")

    func fetchUser(id: String) async throws -> User {
        if shouldFail {
            throw NetworkError.noData
        }
        return mockUser
    }
}

// Test
func testUserLoading() async {
    let mockService = MockUserService()
    let controller = UserController(service: mockService)

    await controller.loadUser(id: "1")

    XCTAssertEqual(controller.user?.name, "Test")
}
```

---

## Related

- [CONTROLLERS.md](CONTROLLERS.md) - Controllers that coordinate Services
- [MODELS.md](MODELS.md) - Models that Services return
- [TESTING.md](TESTING.md) - Testing with mock Services
- [ERROR_HANDLING.md](ERROR_HANDLING.md) - Error handling patterns
- [EXAMPLES.md](EXAMPLES.md) - Real-world Service examples
