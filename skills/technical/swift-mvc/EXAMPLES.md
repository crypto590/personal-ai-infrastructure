# Real-World Examples

**Referenced from**: [SKILL.md](SKILL.md)

---

## Overview

Complete, real-world examples showing how all the pieces fit together.

---

## Example 1: User Profile Feature

### Model

```swift
struct User: Codable, Equatable, Identifiable {
    let id: String
    let name: String
    let email: String
    let bio: String?
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

### Service

```swift
protocol UserServiceProtocol {
    func fetchUser(id: String) async throws -> User
    func updateUser(_ user: User) async throws -> User
}

actor UserService: UserServiceProtocol {
    func fetchUser(id: String) async throws -> User {
        let url = URL(string: "https://api.example.com/users/\(id)")!
        let (data, _) = try await URLSession.shared.data(from: url)
        return try JSONDecoder().decode(User.self, from: data)
    }

    func updateUser(_ user: User) async throws -> User {
        let url = URL(string: "https://api.example.com/users/\(user.id)")!
        var request = URLRequest(url: url)
        request.httpMethod = "PUT"
        request.httpBody = try JSONEncoder().encode(user)
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let (data, _) = try await URLSession.shared.data(for: request)
        return try JSONDecoder().decode(User.self, from: data)
    }
}
```

### Controller

```swift
@Observable
@MainActor
final class UserProfileController {
    private(set) var user: User?
    private(set) var isLoading = false
    private(set) var errorMessage: String?

    private let service: UserServiceProtocol
    private var loadTask: Task<Void, Never>?

    init(service: UserServiceProtocol = UserService()) {
        self.service = service
    }

    func loadUser(id: String) async {
        loadTask?.cancel()

        loadTask = Task {
            isLoading = true
            errorMessage = nil
            defer { isLoading = false }

            do {
                user = try await service.fetchUser(id: id)
            } catch {
                if !Task.isCancelled {
                    errorMessage = error.localizedDescription
                }
            }
        }

        await loadTask?.value
    }

    func clearError() {
        errorMessage = nil
    }

    deinit {
        loadTask?.cancel()
    }
}
```

### View

```swift
struct UserProfileView: View {
    @State private var controller = UserProfileController()
    let userId: String

    var body: some View {
        Group {
            if controller.isLoading {
                ProgressView()
            } else if let user = controller.user {
                ScrollView {
                    VStack(spacing: 20) {
                        // Avatar
                        if let avatarURL = user.avatarURL {
                            AsyncImage(url: avatarURL) { image in
                                image.resizable()
                            } placeholder: {
                                ProgressView()
                            }
                            .frame(width: 100, height: 100)
                            .clipShape(Circle())
                        } else {
                            Circle()
                                .fill(Color.blue)
                                .frame(width: 100, height: 100)
                                .overlay(
                                    Text(user.initials)
                                        .foregroundColor(.white)
                                        .font(.largeTitle)
                                )
                        }

                        // Name and email
                        VStack {
                            Text(user.name)
                                .font(.title)
                            Text(user.email)
                                .foregroundColor(.secondary)
                        }

                        // Bio
                        if let bio = user.bio {
                            Text(bio)
                                .padding()
                        }
                    }
                }
            }
        }
        .task {
            await controller.loadUser(id: userId)
        }
        .alert("Error", isPresented: .constant(controller.errorMessage != nil)) {
            Button("OK") { controller.clearError() }
        } message: {
            Text(controller.errorMessage ?? "")
        }
    }
}
```

---

## Example 2: Sign In Form

### Model

```swift
struct Credentials: Codable {
    let email: String
    let password: String
}

struct AuthResponse: Codable {
    let user: User
    let token: String
}
```

### Service

```swift
protocol AuthServiceProtocol {
    func signIn(credentials: Credentials) async throws -> AuthResponse
}

actor AuthService: AuthServiceProtocol {
    func signIn(credentials: Credentials) async throws -> AuthResponse {
        let url = URL(string: "https://api.example.com/auth/signin")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.httpBody = try JSONEncoder().encode(credentials)
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let (data, _) = try await URLSession.shared.data(for: request)
        return try JSONDecoder().decode(AuthResponse.self, from: data)
    }
}
```

### Controller

```swift
@Observable
@MainActor
final class SignInController {
    private(set) var email = ""
    private(set) var password = ""
    private(set) var isLoading = false
    private(set) var errorMessage: String?
    private(set) var isSignedIn = false

    private(set) var emailError: String?
    private(set) var isValid = false

    private let service: AuthServiceProtocol
    private var signInTask: Task<Void, Never>?

    init(service: AuthServiceProtocol = AuthService()) {
        self.service = service
    }

    func updateEmail(_ newEmail: String) {
        email = newEmail
        validateEmail()
        updateValidity()
    }

    func updatePassword(_ newPassword: String) {
        password = newPassword
        updateValidity()
    }

    private func validateEmail() {
        if email.isEmpty {
            emailError = nil
        } else if !email.contains("@") || !email.contains(".") {
            emailError = "Invalid email address"
        } else {
            emailError = nil
        }
    }

    private func updateValidity() {
        isValid = emailError == nil &&
                  !email.isEmpty &&
                  !password.isEmpty &&
                  password.count >= 8
    }

    func signIn() async {
        guard isValid else { return }

        signInTask?.cancel()

        signInTask = Task {
            isLoading = true
            errorMessage = nil
            defer { isLoading = false }

            do {
                let credentials = Credentials(email: email, password: password)
                let response = try await service.signIn(credentials: credentials)
                isSignedIn = true
            } catch {
                if !Task.isCancelled {
                    errorMessage = error.localizedDescription
                }
            }
        }

        await signInTask?.value
    }

    func clearError() {
        errorMessage = nil
    }

    deinit {
        signInTask?.cancel()
    }
}
```

### View

```swift
struct SignInView: View {
    @State private var controller = SignInController()

    var body: some View {
        Form {
            Section {
                TextField("Email", text: Binding(
                    get: { controller.email },
                    set: { controller.updateEmail($0) }
                ))
                .textContentType(.emailAddress)
                .autocapitalization(.none)

                if let error = controller.emailError {
                    Text(error)
                        .foregroundColor(.red)
                        .font(.caption)
                }

                SecureField("Password", text: Binding(
                    get: { controller.password },
                    set: { controller.updatePassword($0) }
                ))
                .textContentType(.password)
            }

            Section {
                Button("Sign In") {
                    Task {
                        await controller.signIn()
                    }
                }
                .disabled(!controller.isValid || controller.isLoading)

                if controller.isLoading {
                    ProgressView()
                }
            }
        }
        .alert("Error", isPresented: .constant(controller.errorMessage != nil)) {
            Button("OK") { controller.clearError() }
        } message: {
            Text(controller.errorMessage ?? "")
        }
        .fullScreenCover(isPresented: .constant(controller.isSignedIn)) {
            MainAppView()
        }
    }
}
```

---

## Example 3: Post List with Pagination

### Model

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
}

struct PostPage: Codable {
    let posts: [Post]
    let currentPage: Int
    let totalPages: Int

    var hasMore: Bool {
        currentPage < totalPages
    }
}
```

### Service

```swift
protocol PostServiceProtocol {
    func fetchPosts(page: Int, limit: Int) async throws -> PostPage
}

actor PostService: PostServiceProtocol {
    func fetchPosts(page: Int, limit: Int = 20) async throws -> PostPage {
        let url = URL(string: "https://api.example.com/posts?page=\(page)&limit=\(limit)")!
        let (data, _) = try await URLSession.shared.data(from: url)
        return try JSONDecoder().decode(PostPage.self, from: data)
    }
}
```

### Controller

```swift
@Observable
@MainActor
final class PostListController {
    private(set) var posts: [Post] = []
    private(set) var isLoading = false
    private(set) var isLoadingMore = false
    private(set) var errorMessage: String?
    private(set) var hasMore = true

    private var currentPage = 0
    private let service: PostServiceProtocol
    private var loadTask: Task<Void, Never>?

    init(service: PostServiceProtocol = PostService()) {
        self.service = service
    }

    func loadPosts() async {
        loadTask?.cancel()

        loadTask = Task {
            isLoading = true
            errorMessage = nil
            currentPage = 0
            defer { isLoading = false }

            do {
                let page = try await service.fetchPosts(page: currentPage)
                posts = page.posts
                hasMore = page.hasMore
            } catch {
                if !Task.isCancelled {
                    errorMessage = error.localizedDescription
                }
            }
        }

        await loadTask?.value
    }

    func loadMore() async {
        guard !isLoadingMore && hasMore else { return }

        loadTask?.cancel()

        loadTask = Task {
            isLoadingMore = true
            defer { isLoadingMore = false }

            do {
                currentPage += 1
                let page = try await service.fetchPosts(page: currentPage)
                posts.append(contentsOf: page.posts)
                hasMore = page.hasMore
            } catch {
                if !Task.isCancelled {
                    currentPage -= 1
                    errorMessage = error.localizedDescription
                }
            }
        }

        await loadTask?.value
    }

    func clearError() {
        errorMessage = nil
    }

    deinit {
        loadTask?.cancel()
    }
}
```

### View

```swift
struct PostListView: View {
    @State private var controller = PostListController()

    var body: some View {
        List {
            ForEach(controller.posts) { post in
                PostRow(post: post)
                    .onAppear {
                        if post == controller.posts.last && controller.hasMore {
                            Task {
                                await controller.loadMore()
                            }
                        }
                    }
            }

            if controller.isLoadingMore {
                HStack {
                    Spacer()
                    ProgressView()
                    Spacer()
                }
            }
        }
        .task {
            await controller.loadPosts()
        }
        .refreshable {
            await controller.loadPosts()
        }
        .alert("Error", isPresented: .constant(controller.errorMessage != nil)) {
            Button("OK") { controller.clearError() }
        } message: {
            Text(controller.errorMessage ?? "")
        }
    }
}

struct PostRow: View {
    let post: Post

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(post.title)
                .font(.headline)
            Text(post.preview)
                .font(.subheadline)
                .foregroundColor(.secondary)
            HStack {
                Image(systemName: "heart.fill")
                Text("\(post.likes)")
                Spacer()
                Text(post.createdAt, style: .relative)
            }
            .font(.caption)
            .foregroundColor(.secondary)
        }
        .padding(.vertical, 4)
    }
}
```

---

## Example 4: Search with Debounce

### Model

```swift
struct SearchResult: Codable, Equatable, Identifiable {
    let id: String
    let title: String
    let description: String
}
```

### Service

```swift
protocol SearchServiceProtocol {
    func search(query: String) async throws -> [SearchResult]
}

actor SearchService: SearchServiceProtocol {
    func search(query: String) async throws -> [SearchResult] {
        let encodedQuery = query.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? ""
        let url = URL(string: "https://api.example.com/search?q=\(encodedQuery)")!
        let (data, _) = try await URLSession.shared.data(from: url)
        return try JSONDecoder().decode([SearchResult].self, from: data)
    }
}
```

### Controller

```swift
@Observable
@MainActor
final class SearchController {
    private(set) var query = ""
    private(set) var results: [SearchResult] = []
    private(set) var isSearching = false
    private(set) var errorMessage: String?

    private let service: SearchServiceProtocol
    private var searchTask: Task<Void, Never>?

    init(service: SearchServiceProtocol = SearchService()) {
        self.service = service
    }

    func updateQuery(_ newQuery: String) {
        query = newQuery
        performSearch()
    }

    private func performSearch() {
        searchTask?.cancel()

        guard !query.isEmpty else {
            results = []
            return
        }

        searchTask = Task {
            // Debounce: wait before searching
            try? await Task.sleep(for: .milliseconds(300))

            guard !Task.isCancelled else { return }

            isSearching = true
            errorMessage = nil
            defer { isSearching = false }

            do {
                results = try await service.search(query: query)
            } catch {
                if !Task.isCancelled {
                    errorMessage = error.localizedDescription
                }
            }
        }
    }

    func clearError() {
        errorMessage = nil
    }

    deinit {
        searchTask?.cancel()
    }
}
```

### View

```swift
struct SearchView: View {
    @State private var controller = SearchController()

    var body: some View {
        VStack {
            TextField("Search", text: Binding(
                get: { controller.query },
                set: { controller.updateQuery($0) }
            ))
            .textFieldStyle(.roundedBorder)
            .padding()

            if controller.isSearching {
                ProgressView()
            } else if controller.results.isEmpty && !controller.query.isEmpty {
                Text("No results")
                    .foregroundColor(.secondary)
            } else {
                List(controller.results) { result in
                    VStack(alignment: .leading) {
                        Text(result.title)
                            .font(.headline)
                        Text(result.description)
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }
                }
            }
        }
        .alert("Error", isPresented: .constant(controller.errorMessage != nil)) {
            Button("OK") { controller.clearError() }
        } message: {
            Text(controller.errorMessage ?? "")
        }
    }
}
```

---

## Related

- [SKILL.md](SKILL.md) - Main skill overview
- [CONTROLLERS.md](CONTROLLERS.md) - Controller patterns
- [SERVICES.md](SERVICES.md) - Service patterns
- [MODELS.md](MODELS.md) - Model patterns
- [VIEWS.md](VIEWS.md) - View patterns
