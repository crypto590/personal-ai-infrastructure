# SOLID Principles

Comprehensive guide to applying SOLID principles in Swift applications.

**Referenced from**: [SKILL.md](SKILL.md), [ARCHITECTURE_LEVELS.md](ARCHITECTURE_LEVELS.md)

---

## Table of Contents

- [Overview](#overview)
- [Single Responsibility Principle (SRP)](#single-responsibility-principle-srp)
- [Open/Closed Principle (OCP)](#openclosed-principle-ocp)
- [Liskov Substitution Principle (LSP)](#liskov-substitution-principle-lsp)
- [Interface Segregation Principle (ISP)](#interface-segregation-principle-isp)
- [Dependency Inversion Principle (DIP)](#dependency-inversion-principle-dip)
- [Combining SOLID Principles](#combining-solid-principles)

---

## Overview

SOLID principles help you write maintainable, testable, and flexible code regardless of architecture pattern. They apply whether you're using simple views with @State or complex service layers.

**How they integrate with architecture**:
- **Level 1** (@State): SOLID applies within view logic
- **Level 2** (ViewModels): SOLID guides ViewModel design
- **Level 3** (Services): SOLID shapes service interfaces

**Related**: 
- See [ARCHITECTURE_LEVELS.md](ARCHITECTURE_LEVELS.md) for where these principles apply
- See [SERVICE_LAYER.md](SERVICE_LAYER.md#protocol-based-design) for protocol design
- See [VIEWMODEL_PATTERNS.md](VIEWMODEL_PATTERNS.md) for ViewModel best practices

---

## Single Responsibility Principle (SRP)

**Definition**: A class should have only one reason to change.

### Bad Example: Multiple Responsibilities

```swift
// Violates SRP - handles UI logic, networking, and persistence
class UserViewController {
    func loadUser() {
        // Networking logic
        let url = URL(string: "https://api.example.com/user")!
        URLSession.shared.dataTask(with: url) { data, response, error in
            // Parsing logic
            guard let data = data else { return }
            let user = try? JSONDecoder().decode(User.self, from: data)
            
            // Persistence logic
            UserDefaults.standard.set(data, forKey: "user")
            
            // UI logic
            DispatchQueue.main.async {
                self.updateUI(with: user)
            }
        }.resume()
    }
    
    func updateUI(with user: User?) {
        // Update views
    }
}
```

**Problems**:
- Changes to networking affect this class
- Changes to persistence affect this class
- Changes to UI affect this class
- Hard to test each concern independently

### Good Example: Separated Responsibilities

```swift
// NetworkService - handles only networking
class NetworkService {
    func fetchUser() async throws -> User {
        let url = URL(string: "https://api.example.com/user")!
        let (data, _) = try await URLSession.shared.data(from: url)
        return try JSONDecoder().decode(User.self, from: data)
    }
}

// PersistenceService - handles only storage
class PersistenceService {
    func save(_ user: User) throws {
        let data = try JSONEncoder().encode(user)
        UserDefaults.standard.set(data, forKey: "user")
    }
    
    func loadUser() throws -> User? {
        guard let data = UserDefaults.standard.data(forKey: "user") else { return nil }
        return try JSONDecoder().decode(User.self, from: data)
    }
}

// ViewModel - coordinates between services
@Observable
class UserViewModel {
    var user: User?
    
    private let networkService: NetworkService
    private let persistenceService: PersistenceService
    
    init(networkService: NetworkService, persistenceService: PersistenceService) {
        self.networkService = networkService
        self.persistenceService = persistenceService
    }
    
    func loadUser() async {
        do {
            user = try await networkService.fetchUser()
            try persistenceService.save(user!)
        } catch {
            // Handle error
        }
    }
}
```

**Benefits**:
- Each class has one reason to change
- Easy to test each piece independently
- Changes to networking don't affect persistence
- Can swap implementations easily

### Identifying SRP Violations

Ask: "How many reasons could this class change?"

```swift
// Bad - multiple reasons to change
class ReportGenerator {
    func generateReport() { /* Creates report */ }
    func saveToFile() { /* File operations */ }
    func sendByEmail() { /* Email operations */ }
    func formatAsHTML() { /* Formatting logic */ }
}

// Good - single responsibility
class ReportGenerator {
    func generateReport() -> Report { /* Creates report */ }
}

class ReportFileWriter {
    func save(_ report: Report, to path: String) { /* File operations */ }
}

class ReportEmailer {
    func send(_ report: Report, to email: String) { /* Email operations */ }
}

class ReportHTMLFormatter {
    func format(_ report: Report) -> String { /* Formatting logic */ }
}
```

**Related**: See [SERVICE_LAYER.md](SERVICE_LAYER.md#what-belongs-in-services) for service responsibilities.

---

## Open/Closed Principle (OCP)

**Definition**: Software entities should be open for extension but closed for modification.

### Bad Example: Modifying for New Behavior

```swift
enum PaymentMethod {
    case creditCard
    case paypal
    case applePay
}

class PaymentProcessor {
    func processPayment(amount: Decimal, method: PaymentMethod) throws {
        switch method {
        case .creditCard:
            // Credit card logic
            print("Processing credit card payment")
        case .paypal:
            // PayPal logic
            print("Processing PayPal payment")
        case .applePay:
            // Apple Pay logic - had to modify this class!
            print("Processing Apple Pay payment")
        }
    }
}
```

**Problem**: Adding a new payment method requires modifying existing code.

### Good Example: Extension Without Modification

```swift
protocol PaymentMethodProtocol {
    func process(amount: Decimal) async throws
}

class CreditCardPayment: PaymentMethodProtocol {
    func process(amount: Decimal) async throws {
        // Credit card logic
        print("Processing credit card payment: \(amount)")
    }
}

class PayPalPayment: PaymentMethodProtocol {
    func process(amount: Decimal) async throws {
        // PayPal logic
        print("Processing PayPal payment: \(amount)")
    }
}

// New payment method added without modifying existing code
class ApplePayPayment: PaymentMethodProtocol {
    func process(amount: Decimal) async throws {
        // Apple Pay logic
        print("Processing Apple Pay payment: \(amount)")
    }
}

class PaymentProcessor {
    func processPayment(amount: Decimal, method: PaymentMethodProtocol) async throws {
        try await method.process(amount: amount)
    }
}
```

**Benefits**:
- Add new payment methods without changing PaymentProcessor
- Each payment method is independently testable
- No risk of breaking existing payment methods

### Another Example: Validation Rules

```swift
// Bad - must modify for new rules
class FormValidator {
    func validate(_ form: Form) -> Bool {
        if form.email.isEmpty { return false }
        if !form.email.contains("@") { return false }
        if form.password.count < 8 { return false }
        // Adding new rule means modifying this class
        return true
    }
}

// Good - extend with new rules
protocol ValidationRule {
    func validate(_ value: String) -> Bool
}

class EmailRule: ValidationRule {
    func validate(_ value: String) -> Bool {
        value.contains("@")
    }
}

class PasswordLengthRule: ValidationRule {
    let minLength: Int
    
    init(minLength: Int = 8) {
        self.minLength = minLength
    }
    
    func validate(_ value: String) -> Bool {
        value.count >= minLength
    }
}

// New rule - no modification to existing code
class PasswordSpecialCharRule: ValidationRule {
    func validate(_ value: String) -> Bool {
        value.range(of: "[^a-zA-Z0-9]", options: .regularExpression) != nil
    }
}

class FormValidator {
    private let emailRules: [ValidationRule]
    private let passwordRules: [ValidationRule]
    
    init(emailRules: [ValidationRule], passwordRules: [ValidationRule]) {
        self.emailRules = emailRules
        self.passwordRules = passwordRules
    }
    
    func validateEmail(_ email: String) -> Bool {
        emailRules.allSatisfy { $0.validate(email) }
    }
    
    func validatePassword(_ password: String) -> Bool {
        passwordRules.allSatisfy { $0.validate(password) }
    }
}
```

**Related**: See [VIEWMODEL_PATTERNS.md](VIEWMODEL_PATTERNS.md#validation) for validation in ViewModels.

---

## Liskov Substitution Principle (LSP)

**Definition**: Subtypes must be substitutable for their base types without altering program correctness.

### Bad Example: Violating Expectations

```swift
class Rectangle {
    var width: Double
    var height: Double
    
    init(width: Double, height: Double) {
        self.width = width
        self.height = height
    }
    
    func area() -> Double {
        width * height
    }
}

// Violates LSP - changes behavior unexpectedly
class Square: Rectangle {
    override var width: Double {
        didSet { height = width }
    }
    
    override var height: Double {
        didSet { width = height }
    }
}

// This breaks with Square!
func testRectangle(_ rect: Rectangle) {
    rect.width = 5
    rect.height = 10
    assert(rect.area() == 50)  // Fails for Square!
}
```

**Problem**: Square changes behavior in unexpected ways when used as Rectangle.

### Good Example: Proper Abstraction

```swift
protocol Shape {
    func area() -> Double
}

struct Rectangle: Shape {
    let width: Double
    let height: Double
    
    func area() -> Double {
        width * height
    }
}

struct Square: Shape {
    let side: Double
    
    func area() -> Double {
        side * side
    }
}

// Works correctly for all shapes
func printArea(_ shape: Shape) {
    print("Area: \(shape.area())")
}
```

### Another Example: Data Sources

```swift
// Bad - subtypes behave differently
protocol DataSource {
    func fetchData() async throws -> [Item]
}

class APIDataSource: DataSource {
    func fetchData() async throws -> [Item] {
        // Fetches from network
        try await networkService.fetch()
    }
}

class CachedDataSource: DataSource {
    func fetchData() async throws -> [Item] {
        // Returns cached data OR throws if empty
        // Different behavior! Violates LSP
        if cache.isEmpty {
            throw DataError.noCache  // Unexpected!
        }
        return cache
    }
}

// Good - consistent behavior
protocol DataSource {
    func fetchData() async throws -> [Item]
}

class APIDataSource: DataSource {
    func fetchData() async throws -> [Item] {
        try await networkService.fetch()
    }
}

class CachedDataSource: DataSource {
    private let fallbackSource: DataSource
    
    init(fallbackSource: DataSource) {
        self.fallbackSource = fallbackSource
    }
    
    func fetchData() async throws -> [Item] {
        if !cache.isEmpty {
            return cache
        }
        // Consistent behavior - always tries to return data
        let items = try await fallbackSource.fetchData()
        cache = items
        return items
    }
}
```

---

## Interface Segregation Principle (ISP)

**Definition**: Clients should not be forced to depend on interfaces they don't use.

### Bad Example: Fat Interface

```swift
protocol Worker {
    func work()
    func eat()
    func sleep()
    func attendMeeting()
    func submitTimesheet()
}

// Robot forced to implement methods it doesn't need
class Robot: Worker {
    func work() { /* Robot works */ }
    
    func eat() { /* Robots don't eat! */ }
    func sleep() { /* Robots don't sleep! */ }
    func attendMeeting() { /* Robots don't attend meetings! */ }
    func submitTimesheet() { /* Robots don't submit timesheets! */ }
}
```

### Good Example: Segregated Interfaces

```swift
protocol Workable {
    func work()
}

protocol Eatable {
    func eat()
}

protocol Sleepable {
    func sleep()
}

protocol Meetable {
    func attendMeeting()
}

class Human: Workable, Eatable, Sleepable, Meetable {
    func work() { /* Human works */ }
    func eat() { /* Human eats */ }
    func sleep() { /* Human sleeps */ }
    func attendMeeting() { /* Human attends meeting */ }
}

class Robot: Workable {
    func work() { /* Robot works */ }
    // Only implements what it needs
}
```

### Practical Example: User Permissions

```swift
// Bad - user must implement all permissions
protocol User {
    func viewProfile()
    func editProfile()
    func deleteAccount()
    func manageUsers()
    func viewAnalytics()
}

// Admin user is fine, but...
class AdminUser: User {
    func viewProfile() { /* OK */ }
    func editProfile() { /* OK */ }
    func deleteAccount() { /* OK */ }
    func manageUsers() { /* OK */ }
    func viewAnalytics() { /* OK */ }
}

// Regular user forced to implement admin methods!
class RegularUser: User {
    func viewProfile() { /* OK */ }
    func editProfile() { /* OK */ }
    func deleteAccount() { /* OK */ }
    func manageUsers() { fatalError("Not allowed") }  // Shouldn't exist!
    func viewAnalytics() { fatalError("Not allowed") }  // Shouldn't exist!
}

// Good - segregated by capability
protocol ProfileViewable {
    func viewProfile()
}

protocol ProfileEditable {
    func editProfile()
}

protocol AccountDeletable {
    func deleteAccount()
}

protocol UserManageable {
    func manageUsers()
}

protocol AnalyticsViewable {
    func viewAnalytics()
}

class RegularUser: ProfileViewable, ProfileEditable, AccountDeletable {
    func viewProfile() { /* OK */ }
    func editProfile() { /* OK */ }
    func deleteAccount() { /* OK */ }
}

class AdminUser: ProfileViewable, ProfileEditable, AccountDeletable, UserManageable, AnalyticsViewable {
    func viewProfile() { /* OK */ }
    func editProfile() { /* OK */ }
    func deleteAccount() { /* OK */ }
    func manageUsers() { /* OK */ }
    func viewAnalytics() { /* OK */ }
}
```

**Related**: See [SERVICE_LAYER.md](SERVICE_LAYER.md#protocol-based-design) for service protocol design.

---

## Dependency Inversion Principle (DIP)

**Definition**: High-level modules should not depend on low-level modules. Both should depend on abstractions.

### Bad Example: Direct Dependencies

```swift
// Low-level module
class SQLiteDatabase {
    func save(_ user: User) {
        // SQLite-specific code
    }
    
    func fetch(id: String) -> User? {
        // SQLite-specific code
        return nil
    }
}

// High-level module depends on concrete low-level module
class UserRepository {
    private let database = SQLiteDatabase()  // Hardcoded dependency!
    
    func saveUser(_ user: User) {
        database.save(user)
    }
    
    func getUser(id: String) -> User? {
        database.fetch(id: id)
    }
}
```

**Problems**:
- Can't switch to a different database
- Hard to test (can't mock)
- Tightly coupled

### Good Example: Depend on Abstractions

```swift
// Abstraction
protocol DatabaseProtocol {
    func save(_ user: User)
    func fetch(id: String) -> User?
}

// Low-level implementations
class SQLiteDatabase: DatabaseProtocol {
    func save(_ user: User) {
        // SQLite-specific code
    }
    
    func fetch(id: String) -> User? {
        // SQLite-specific code
        return nil
    }
}

class RealmDatabase: DatabaseProtocol {
    func save(_ user: User) {
        // Realm-specific code
    }
    
    func fetch(id: String) -> User? {
        // Realm-specific code
        return nil
    }
}

// High-level module depends on abstraction
class UserRepository {
    private let database: DatabaseProtocol  // Depends on protocol!
    
    init(database: DatabaseProtocol) {
        self.database = database
    }
    
    func saveUser(_ user: User) {
        database.save(user)
    }
    
    func getUser(id: String) -> User? {
        database.fetch(id: id)
    }
}

// Easy to swap implementations
let repo1 = UserRepository(database: SQLiteDatabase())
let repo2 = UserRepository(database: RealmDatabase())

// Easy to test with mock
class MockDatabase: DatabaseProtocol {
    var savedUsers: [User] = []
    
    func save(_ user: User) {
        savedUsers.append(user)
    }
    
    func fetch(id: String) -> User? {
        savedUsers.first { $0.id == id }
    }
}

let testRepo = UserRepository(database: MockDatabase())
```

### Practical Example: Networking Layer

```swift
// Bad - depends on concrete URLSession
class APIClient {
    func fetchData() async throws -> Data {
        let url = URL(string: "https://api.example.com/data")!
        let (data, _) = try await URLSession.shared.data(from: url)  // Hardcoded!
        return data
    }
}

// Good - depends on abstraction
protocol NetworkSessionProtocol {
    func data(from url: URL) async throws -> (Data, URLResponse)
}

// Make URLSession conform to our protocol
extension URLSession: NetworkSessionProtocol {
    // Already has the method we need!
}

class APIClient {
    private let session: NetworkSessionProtocol
    
    init(session: NetworkSessionProtocol) {
        self.session = session
    }
    
    func fetchData() async throws -> Data {
        let url = URL(string: "https://api.example.com/data")!
        let (data, _) = try await session.data(from: url)
        return data
    }
}

// Production
let productionClient = APIClient(session: URLSession.shared)

// Testing
class MockNetworkSession: NetworkSessionProtocol {
    var mockData: Data?
    var mockError: Error?
    
    func data(from url: URL) async throws -> (Data, URLResponse) {
        if let error = mockError {
            throw error
        }
        let response = HTTPURLResponse(url: url, statusCode: 200, httpVersion: nil, headerFields: nil)!
        return (mockData ?? Data(), response)
    }
}

let testClient = APIClient(session: MockNetworkSession())
```

**Related**: 
- See [SERVICE_LAYER.md](SERVICE_LAYER.md#dependency-injection) for DI implementation
- See [ARCHITECTURE_LEVELS.md](ARCHITECTURE_LEVELS.md#anti-patterns) for DI anti-patterns

---

## Combining SOLID Principles

Real-world example showing all principles working together:

```swift
// ISP - Small, focused protocols
protocol DataFetchable {
    func fetch() async throws -> [Item]
}

protocol DataCacheable {
    func cache(_ items: [Item])
    func getCached() -> [Item]?
}

// DIP - Depend on abstractions
protocol NetworkServiceProtocol {
    func get<T: Decodable>(_ endpoint: String) async throws -> T
}

// SRP - Single responsibility classes
class APIDataSource: DataFetchable {
    private let networkService: NetworkServiceProtocol  // DIP
    
    init(networkService: NetworkServiceProtocol) {
        self.networkService = networkService
    }
    
    func fetch() async throws -> [Item] {
        try await networkService.get("/items")
    }
}

class CacheManager: DataCacheable {
    private var cache: [Item] = []
    
    func cache(_ items: [Item]) {
        cache = items
    }
    
    func getCached() -> [Item]? {
        cache.isEmpty ? nil : cache
    }
}

// OCP - Extendable without modification
class DataRepository: DataFetchable {
    private let source: DataFetchable       // DIP
    private let cache: DataCacheable        // DIP
    
    init(source: DataFetchable, cache: DataCacheable) {
        self.source = source
        self.cache = cache
    }
    
    func fetch() async throws -> [Item] {
        // Try cache first
        if let cached = cache.getCached() {
            return cached
        }
        
        // Fetch from source
        let items = try await source.fetch()
        cache.cache(items)
        return items
    }
}

// Usage - all dependencies injected
let networkService = NetworkService()
let apiSource = APIDataSource(networkService: networkService)
let cacheManager = CacheManager()
let repository = DataRepository(source: apiSource, cache: cacheManager)

// Testing - easy to mock
let mockSource = MockDataSource()
let mockCache = MockCache()
let testRepository = DataRepository(source: mockSource, cache: mockCache)
```

**This example demonstrates**:
- **SRP**: Each class has a single, clear responsibility
- **OCP**: Can add new data sources without modifying DataRepository
- **LSP**: All DataFetchable implementations behave consistently
- **ISP**: Small, focused protocols (DataFetchable, DataCacheable)
- **DIP**: All dependencies are on protocols, not concrete classes

**Related**: See [EXAMPLES.md](EXAMPLES.md) for more combined examples.

---

## Summary

Apply SOLID principles to write:

1. **SRP**: Classes with single, clear responsibilities
2. **OCP**: Extensible code that doesn't require modification
3. **LSP**: Consistent behavior in inheritance hierarchies
4. **ISP**: Small, focused protocols
5. **DIP**: Dependencies on abstractions, not concrete types

These principles work together to create flexible, testable, maintainable code in any architecture.

**Related Resources**:
- [SKILL.md](SKILL.md) - Main skill overview
- [ARCHITECTURE_LEVELS.md](ARCHITECTURE_LEVELS.md) - Where SOLID applies in architecture
- [VIEWMODEL_PATTERNS.md](VIEWMODEL_PATTERNS.md) - SOLID in ViewModels
- [SERVICE_LAYER.md](SERVICE_LAYER.md) - SOLID in Services
- [EXAMPLES.md](EXAMPLES.md) - Real-world applications
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Quick SOLID checks
