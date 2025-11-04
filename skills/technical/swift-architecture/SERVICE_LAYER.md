# Service Layer Architecture

Guidelines for building robust, reusable services in Swift applications.

## What Belongs in Services

Services encapsulate domain-specific operations that are:
- **Shared across features** - Multiple ViewModels need the same logic
- **Framework-level concerns** - Networking, persistence, authentication
- **Infrastructure** - External system integrations

## Common Service Types

### Authentication Service

Manages user authentication and session state:

```swift
@Observable
class AuthenticationService {
    // Published state
    var currentUser: User?
    var isAuthenticated: Bool { currentUser != nil }
    
    // Dependencies
    private let networkService: NetworkServiceProtocol
    private let storageService: SecureStorageServiceProtocol
    
    init(
        networkService: NetworkServiceProtocol,
        storageService: SecureStorageServiceProtocol
    ) {
        self.networkService = networkService
        self.storageService = storageService
    }
    
    func login(email: String, password: String) async throws {
        let response: LoginResponse = try await networkService.post(
            "/auth/login",
            body: ["email": email, "password": password]
        )
        
        currentUser = response.user
        try await storageService.save(response.token, forKey: "auth_token")
    }
    
    func logout() async {
        currentUser = nil
        try? await storageService.delete(forKey: "auth_token")
    }
    
    func restoreSession() async throws {
        guard let token = try await storageService.retrieve(forKey: "auth_token") else {
            return
        }
        
        currentUser = try await networkService.get("/auth/me", token: token)
    }
}
```

### Network Service

Handles all HTTP communication:

```swift
protocol NetworkServiceProtocol {
    func get<T: Decodable>(_ endpoint: String, token: String?) async throws -> T
    func post<T: Decodable>(_ endpoint: String, body: [String: Any], token: String?) async throws -> T
    func put<T: Decodable>(_ endpoint: String, body: [String: Any], token: String?) async throws -> T
    func delete(_ endpoint: String, token: String?) async throws
}

class NetworkService: NetworkServiceProtocol {
    private let baseURL: URL
    private let session: URLSession
    
    init(baseURL: URL, session: URLSession = .shared) {
        self.baseURL = baseURL
        self.session = session
    }
    
    func get<T: Decodable>(_ endpoint: String, token: String? = nil) async throws -> T {
        let url = baseURL.appendingPathComponent(endpoint)
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        
        if let token {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw NetworkError.invalidResponse
        }
        
        guard (200...299).contains(httpResponse.statusCode) else {
            throw NetworkError.httpError(statusCode: httpResponse.statusCode)
        }
        
        return try JSONDecoder().decode(T.self, from: data)
    }
    
    func post<T: Decodable>(_ endpoint: String, body: [String: Any], token: String? = nil) async throws -> T {
        let url = baseURL.appendingPathComponent(endpoint)
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        if let token {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        
        request.httpBody = try JSONSerialization.data(withJSONObject: body)
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw NetworkError.invalidResponse
        }
        
        guard (200...299).contains(httpResponse.statusCode) else {
            throw NetworkError.httpError(statusCode: httpResponse.statusCode)
        }
        
        return try JSONDecoder().decode(T.self, from: data)
    }
    
    // Implement put and delete similarly
}

enum NetworkError: LocalizedError {
    case invalidResponse
    case httpError(statusCode: Int)
    case decodingError
    
    var errorDescription: String? {
        switch self {
        case .invalidResponse:
            return "Invalid server response"
        case .httpError(let code):
            return "Server error: \(code)"
        case .decodingError:
            return "Failed to decode response"
        }
    }
}
```

### Persistence Service

Manages local data storage:

```swift
protocol PersistenceServiceProtocol {
    func save<T: Codable>(_ object: T, withKey key: String) throws
    func retrieve<T: Codable>(withKey key: String) throws -> T?
    func delete(withKey key: String) throws
}

class UserDefaultsPersistenceService: PersistenceServiceProtocol {
    private let userDefaults: UserDefaults
    
    init(userDefaults: UserDefaults = .standard) {
        self.userDefaults = userDefaults
    }
    
    func save<T: Codable>(_ object: T, withKey key: String) throws {
        let data = try JSONEncoder().encode(object)
        userDefaults.set(data, forKey: key)
    }
    
    func retrieve<T: Codable>(withKey key: String) throws -> T? {
        guard let data = userDefaults.data(forKey: key) else {
            return nil
        }
        return try JSONDecoder().decode(T.self, from: data)
    }
    
    func delete(withKey key: String) throws {
        userDefaults.removeObject(forKey: key)
    }
}
```

### Location Service

Manages GPS and location:

```swift
@Observable
class LocationService: NSObject, CLLocationManagerDelegate {
    var currentLocation: CLLocation?
    var authorizationStatus: CLAuthorizationStatus = .notDetermined
    
    private let locationManager = CLLocationManager()
    
    override init() {
        super.init()
        locationManager.delegate = self
    }
    
    func requestPermission() {
        locationManager.requestWhenInUseAuthorization()
    }
    
    func startTracking() {
        locationManager.startUpdatingLocation()
    }
    
    func stopTracking() {
        locationManager.stopUpdatingLocation()
    }
    
    // CLLocationManagerDelegate methods
    func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        currentLocation = locations.last
    }
    
    func locationManagerDidChangeAuthorization(_ manager: CLLocationManager) {
        authorizationStatus = manager.authorizationStatus
    }
}
```

## Dependency Injection

Services should receive their dependencies, not create them:

### Service Factory

```swift
class ServiceFactory {
    // Shared services
    let networkService: NetworkServiceProtocol
    let persistenceService: PersistenceServiceProtocol
    let authenticationService: AuthenticationService
    
    init() {
        // Create base services
        let baseURL = URL(string: "https://api.example.com")!
        self.networkService = NetworkService(baseURL: baseURL)
        self.persistenceService = UserDefaultsPersistenceService()
        
        // Create dependent services
        self.authenticationService = AuthenticationService(
            networkService: networkService,
            storageService: SecureStorageService(persistence: persistenceService)
        )
    }
    
    // Factory methods for feature-specific services
    func makeUserProfileService() -> UserProfileService {
        UserProfileService(
            networkService: networkService,
            authService: authenticationService
        )
    }
    
    func makePostService() -> PostService {
        PostService(
            networkService: networkService,
            authService: authenticationService
        )
    }
}
```

### Using in SwiftUI App

```swift
@main
struct MyApp: App {
    let serviceFactory = ServiceFactory()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(serviceFactory.authenticationService)
        }
    }
}

// In Views:
struct ProfileView: View {
    @Environment(AuthenticationService.self) private var authService
    @State private var viewModel: ProfileViewModel
    
    init() {
        // Use environment in .task or onAppear, not init
    }
    
    var body: some View {
        // ...
    }
    .task {
        viewModel = ProfileViewModel(authService: authService)
        await viewModel.loadProfile()
    }
}
```

## Protocol-Based Design

Define protocols for services to enable testing and flexibility:

```swift
// Protocol
protocol UserServiceProtocol {
    func fetchUser(id: String) async throws -> User
    func updateUser(_ user: User) async throws
}

// Production implementation
class UserService: UserServiceProtocol {
    private let networkService: NetworkServiceProtocol
    
    init(networkService: NetworkServiceProtocol) {
        self.networkService = networkService
    }
    
    func fetchUser(id: String) async throws -> User {
        try await networkService.get("/users/\(id)")
    }
    
    func updateUser(_ user: User) async throws {
        let _: User = try await networkService.put("/users/\(user.id)", body: user.toDictionary())
    }
}

// Mock implementation for testing
class MockUserService: UserServiceProtocol {
    var mockUser: User?
    var shouldThrowError = false
    
    func fetchUser(id: String) async throws -> User {
        if shouldThrowError {
            throw NetworkError.httpError(statusCode: 404)
        }
        guard let user = mockUser else {
            throw NetworkError.httpError(statusCode: 404)
        }
        return user
    }
    
    func updateUser(_ user: User) async throws {
        if shouldThrowError {
            throw NetworkError.httpError(statusCode: 500)
        }
        mockUser = user
    }
}
```

## Error Handling in Services

Services should throw specific, meaningful errors:

```swift
enum DataServiceError: LocalizedError {
    case notFound
    case unauthorized
    case serverError(message: String)
    case networkUnavailable
    
    var errorDescription: String? {
        switch self {
        case .notFound:
            return "The requested data was not found"
        case .unauthorized:
            return "You don't have permission to access this resource"
        case .serverError(let message):
            return "Server error: \(message)"
        case .networkUnavailable:
            return "No internet connection"
        }
    }
}

class DataService {
    func fetchData() async throws -> [Item] {
        do {
            return try await networkService.get("/data")
        } catch let error as NetworkError {
            switch error {
            case .httpError(404):
                throw DataServiceError.notFound
            case .httpError(401), .httpError(403):
                throw DataServiceError.unauthorized
            case .httpError(let code) where code >= 500:
                throw DataServiceError.serverError(message: "Status \(code)")
            default:
                throw DataServiceError.networkUnavailable
            }
        }
    }
}
```

## Caching Strategies

### In-Memory Cache

```swift
@Observable
class CachedDataService {
    private var cache: [String: [Item]] = [:]
    private var cacheTimestamps: [String: Date] = [:]
    private let cacheLifetime: TimeInterval = 300  // 5 minutes
    
    private let networkService: NetworkServiceProtocol
    
    init(networkService: NetworkServiceProtocol) {
        self.networkService = networkService
    }
    
    func fetchData(forKey key: String, forceRefresh: Bool = false) async throws -> [Item] {
        // Check cache validity
        if !forceRefresh,
           let cachedData = cache[key],
           let timestamp = cacheTimestamps[key],
           Date().timeIntervalSince(timestamp) < cacheLifetime {
            return cachedData
        }
        
        // Fetch fresh data
        let data: [Item] = try await networkService.get("/data/\(key)")
        
        // Update cache
        cache[key] = data
        cacheTimestamps[key] = Date()
        
        return data
    }
    
    func clearCache() {
        cache.removeAll()
        cacheTimestamps.removeAll()
    }
}
```

## Testing Services

### Unit Testing with Mocks

```swift
func testUserServiceFetch() async throws {
    // Arrange
    let mockNetwork = MockNetworkService()
    mockNetwork.mockResponse = User(id: "123", name: "Test User")
    
    let userService = UserService(networkService: mockNetwork)
    
    // Act
    let user = try await userService.fetchUser(id: "123")
    
    // Assert
    XCTAssertEqual(user.id, "123")
    XCTAssertEqual(user.name, "Test User")
    XCTAssertEqual(mockNetwork.lastRequestedEndpoint, "/users/123")
}

func testUserServiceErrorHandling() async {
    // Arrange
    let mockNetwork = MockNetworkService()
    mockNetwork.shouldFail = true
    
    let userService = UserService(networkService: mockNetwork)
    
    // Act & Assert
    do {
        _ = try await userService.fetchUser(id: "123")
        XCTFail("Should have thrown an error")
    } catch {
        XCTAssertTrue(error is NetworkError)
    }
}
```

## Service Composition

Services can depend on other services:

```swift
class PostService {
    private let networkService: NetworkServiceProtocol
    private let authService: AuthenticationService
    private let cacheService: CacheServiceProtocol
    
    init(
        networkService: NetworkServiceProtocol,
        authService: AuthenticationService,
        cacheService: CacheServiceProtocol
    ) {
        self.networkService = networkService
        self.authService = authService
        self.cacheService = cacheService
    }
    
    func fetchPosts() async throws -> [Post] {
        // Check auth
        guard authService.isAuthenticated else {
            throw PostServiceError.notAuthenticated
        }
        
        // Check cache
        if let cached: [Post] = try? cacheService.retrieve(forKey: "posts") {
            return cached
        }
        
        // Fetch from network
        let posts: [Post] = try await networkService.get("/posts")
        
        // Update cache
        try? cacheService.save(posts, forKey: "posts")
        
        return posts
    }
}
```

## Best Practices Summary

1. **Single Responsibility** - Each service handles one domain
2. **Protocol-based** - Define interfaces for all services
3. **Dependency Injection** - Services receive dependencies, don't create them
4. **Testable** - Mock dependencies for unit tests
5. **Error Handling** - Throw meaningful, specific errors
6. **Async/Await** - Use modern concurrency patterns
7. **Observable for State** - Use @Observable when services hold shared state
8. **Caching Strategy** - Implement when appropriate for performance
9. **Logging** - Log important operations for debugging
10. **Documentation** - Document public APIs and error conditions
