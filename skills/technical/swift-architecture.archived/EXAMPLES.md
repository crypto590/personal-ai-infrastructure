# Architecture Examples

Real-world examples showing how features scale from Level 1 to Level 3.

## Example 1: User Profile Feature Evolution

### Starting Simple: Level 1

Initially, the profile screen just displays static user info:

```swift
struct ProfileView: View {
    @State private var showingSettings = false
    @State private var selectedTab = "Posts"
    
    var body: some View {
        VStack {
            Image(systemName: "person.circle.fill")
                .resizable()
                .frame(width: 100, height: 100)
            
            Text("John Doe")
                .font(.title)
            
            Picker("Tab", selection: $selectedTab) {
                Text("Posts").tag("Posts")
                Text("About").tag("About")
            }
            .pickerStyle(.segmented)
            
            Button("Settings") {
                showingSettings = true
            }
        }
        .sheet(isPresented: $showingSettings) {
            SettingsView()
        }
    }
}
```

**Characteristics**: Only UI state, no data loading, no API calls.

### Adding Complexity: Level 2

Now we need to fetch profile data from an API:

```swift
@Observable
class ProfileViewModel {
    var profile: UserProfile?
    var isLoading = false
    var errorMessage: String?
    
    private let authService: AuthenticationService
    
    init(authService: AuthenticationService) {
        self.authService = authService
    }
    
    func loadProfile() async {
        isLoading = true
        errorMessage = nil
        
        do {
            profile = try await authService.fetchUserProfile()
        } catch {
            errorMessage = "Failed to load profile: \(error.localizedDescription)"
        }
        
        isLoading = false
    }
    
    func updateProfile(name: String, bio: String) async {
        guard var profile = profile else { return }
        
        profile.name = name
        profile.bio = bio
        
        do {
            try await authService.updateProfile(profile)
            self.profile = profile
        } catch {
            errorMessage = "Failed to update profile"
        }
    }
}

struct ProfileView: View {
    @State private var viewModel: ProfileViewModel
    @State private var showingSettings = false
    
    init(authService: AuthenticationService) {
        self._viewModel = State(initialValue: ProfileViewModel(authService: authService))
    }
    
    var body: some View {
        Group {
            if viewModel.isLoading {
                ProgressView()
            } else if let profile = viewModel.profile {
                VStack {
                    AsyncImage(url: profile.avatarURL) { image in
                        image.resizable()
                    } placeholder: {
                        Image(systemName: "person.circle.fill")
                    }
                    .frame(width: 100, height: 100)
                    .clipShape(Circle())
                    
                    Text(profile.name)
                        .font(.title)
                    
                    Text(profile.bio)
                        .foregroundStyle(.secondary)
                    
                    Button("Settings") {
                        showingSettings = true
                    }
                }
            } else if let error = viewModel.errorMessage {
                VStack {
                    Text(error)
                    Button("Retry") {
                        Task { await viewModel.loadProfile() }
                    }
                }
            }
        }
        .task {
            await viewModel.loadProfile()
        }
        .sheet(isPresented: $showingSettings) {
            SettingsView()
        }
    }
}
```

**Characteristics**: API calls, error handling, loading states, business logic in ViewModel.

### Sharing Logic: Level 3

Multiple screens need auth state, so we extract it to a service:

```swift
@Observable
class AuthenticationService {
    var currentUser: User?
    var isAuthenticated: Bool { currentUser != nil }
    
    private let networkService: NetworkServiceProtocol
    private let persistenceService: PersistenceServiceProtocol
    
    init(
        networkService: NetworkServiceProtocol,
        persistenceService: PersistenceServiceProtocol
    ) {
        self.networkService = networkService
        self.persistenceService = persistenceService
    }
    
    func login(email: String, password: String) async throws {
        let response: LoginResponse = try await networkService.post(
            "/auth/login",
            body: ["email": email, "password": password]
        )
        
        currentUser = response.user
        try await persistenceService.save(response.token, forKey: "auth_token")
    }
    
    func logout() async {
        currentUser = nil
        try? await persistenceService.delete(forKey: "auth_token")
    }
    
    func fetchUserProfile() async throws -> UserProfile {
        guard isAuthenticated else {
            throw AuthError.notAuthenticated
        }
        
        return try await networkService.get("/profile")
    }
    
    func updateProfile(_ profile: UserProfile) async throws {
        guard isAuthenticated else {
            throw AuthError.notAuthenticated
        }
        
        try await networkService.put("/profile", body: profile.toDictionary())
    }
}

// ProfileViewModel now uses the shared service
@Observable
class ProfileViewModel {
    var profile: UserProfile?
    var isLoading = false
    var errorMessage: String?
    
    private let authService: AuthenticationService  // Shared service!
    
    init(authService: AuthenticationService) {
        self.authService = authService
    }
    
    func loadProfile() async {
        isLoading = true
        errorMessage = nil
        
        do {
            profile = try await authService.fetchUserProfile()
        } catch {
            errorMessage = "Failed to load profile: \(error.localizedDescription)"
        }
        
        isLoading = false
    }
}
```

**Benefits**: 
- Login screen also uses AuthenticationService
- Settings screen can access currentUser
- All auth logic in one place
- Consistent auth state across the app

## Example 2: Todo List Feature Evolution

### Level 1: Local State Only

```swift
struct TodoListView: View {
    @State private var todos = [
        Todo(title: "Buy milk", isComplete: false),
        Todo(title: "Walk dog", isComplete: true)
    ]
    @State private var newTodoTitle = ""
    
    var body: some View {
        List {
            ForEach(todos) { todo in
                HStack {
                    Image(systemName: todo.isComplete ? "checkmark.circle.fill" : "circle")
                    Text(todo.title)
                }
                .onTapGesture {
                    toggleTodo(todo)
                }
            }
            
            HStack {
                TextField("New todo", text: $newTodoTitle)
                Button("Add") {
                    addTodo()
                }
            }
        }
    }
    
    private func toggleTodo(_ todo: Todo) {
        if let index = todos.firstIndex(where: { $0.id == todo.id }) {
            todos[index].isComplete.toggle()
        }
    }
    
    private func addTodo() {
        guard !newTodoTitle.isEmpty else { return }
        todos.append(Todo(title: newTodoTitle, isComplete: false))
        newTodoTitle = ""
    }
}
```

**When to use**: Learning app, prototype, no data persistence needed.

### Level 2: Add Persistence

```swift
@Observable
class TodoViewModel {
    var todos: [Todo] = []
    var newTodoTitle = ""
    var errorMessage: String?
    
    private let persistenceService: PersistenceServiceProtocol
    
    init(persistenceService: PersistenceServiceProtocol) {
        self.persistenceService = persistenceService
    }
    
    func loadTodos() async {
        do {
            todos = try await persistenceService.load(forKey: "todos") ?? []
        } catch {
            errorMessage = "Failed to load todos"
        }
    }
    
    func addTodo() async {
        guard !newTodoTitle.isEmpty else { return }
        
        let newTodo = Todo(title: newTodoTitle, isComplete: false)
        todos.append(newTodo)
        newTodoTitle = ""
        
        await saveTodos()
    }
    
    func toggleTodo(_ todo: Todo) async {
        if let index = todos.firstIndex(where: { $0.id == todo.id }) {
            todos[index].isComplete.toggle()
            await saveTodos()
        }
    }
    
    private func saveTodos() async {
        do {
            try await persistenceService.save(todos, forKey: "todos")
        } catch {
            errorMessage = "Failed to save todos"
        }
    }
}
```

**When to graduate**: Need to save data, add validation, or sync with backend.

### Level 3: Sync with Backend

```swift
// Service for API operations
class TodoService {
    private let networkService: NetworkServiceProtocol
    
    init(networkService: NetworkServiceProtocol) {
        self.networkService = networkService
    }
    
    func fetchTodos() async throws -> [Todo] {
        try await networkService.get("/todos")
    }
    
    func createTodo(_ todo: Todo) async throws -> Todo {
        try await networkService.post("/todos", body: todo.toDictionary())
    }
    
    func updateTodo(_ todo: Todo) async throws {
        try await networkService.put("/todos/\(todo.id)", body: todo.toDictionary())
    }
    
    func deleteTodo(_ todo: Todo) async throws {
        try await networkService.delete("/todos/\(todo.id)")
    }
}

// ViewModel uses the service
@Observable
class TodoViewModel {
    var todos: [Todo] = []
    var isLoading = false
    var errorMessage: String?
    
    private let todoService: TodoService
    
    init(todoService: TodoService) {
        self.todoService = todoService
    }
    
    func loadTodos() async {
        isLoading = true
        errorMessage = nil
        
        do {
            todos = try await todoService.fetchTodos()
        } catch {
            errorMessage = "Failed to load todos"
        }
        
        isLoading = false
    }
    
    func addTodo(title: String) async {
        let newTodo = Todo(title: title, isComplete: false)
        
        // Optimistic update
        todos.append(newTodo)
        
        do {
            let savedTodo = try await todoService.createTodo(newTodo)
            // Update with server response
            if let index = todos.firstIndex(where: { $0.id == newTodo.id }) {
                todos[index] = savedTodo
            }
        } catch {
            // Rollback on failure
            todos.removeAll { $0.id == newTodo.id }
            errorMessage = "Failed to create todo"
        }
    }
}
```

**When to graduate**: Need backend sync, shared todo lists, or multi-device support.

## Example 3: Search Feature Evolution

### Level 1: Simple Filter

```swift
struct SearchView: View {
    @State private var searchText = ""
    
    let items = [
        "Apple", "Banana", "Cherry", "Date", "Elderberry"
    ]
    
    var filteredItems: [String] {
        if searchText.isEmpty {
            return items
        }
        return items.filter { $0.localizedCaseInsensitiveContains(searchText) }
    }
    
    var body: some View {
        List {
            ForEach(filteredItems, id: \.self) { item in
                Text(item)
            }
        }
        .searchable(text: $searchText)
    }
}
```

**When to use**: Filtering local data, no API needed.

### Level 2: API Search with Debouncing

```swift
@Observable
class SearchViewModel {
    var searchText = "" {
        didSet {
            // Cancel previous search
            searchTask?.cancel()
            
            // Debounce - wait 300ms before searching
            searchTask = Task {
                try? await Task.sleep(nanoseconds: 300_000_000)
                await performSearch()
            }
        }
    }
    
    var results: [SearchResult] = []
    var isLoading = false
    var errorMessage: String?
    
    private var searchTask: Task<Void, Never>?
    private let searchService: SearchService
    
    init(searchService: SearchService) {
        self.searchService = searchService
    }
    
    private func performSearch() async {
        guard !searchText.isEmpty else {
            results = []
            return
        }
        
        isLoading = true
        errorMessage = nil
        
        do {
            results = try await searchService.search(query: searchText)
        } catch {
            errorMessage = "Search failed"
            results = []
        }
        
        isLoading = false
    }
}

struct SearchView: View {
    @State private var viewModel: SearchViewModel
    
    var body: some View {
        List {
            if viewModel.isLoading {
                ProgressView()
            } else {
                ForEach(viewModel.results) { result in
                    Text(result.title)
                }
            }
        }
        .searchable(text: $viewModel.searchText)
    }
}
```

**When to graduate**: Need API search, debouncing, or complex search logic.

### Level 3: Shared Search Service with History

```swift
@Observable
class SearchService {
    var recentSearches: [String] = []
    
    private let networkService: NetworkServiceProtocol
    private let persistenceService: PersistenceServiceProtocol
    
    init(
        networkService: NetworkServiceProtocol,
        persistenceService: PersistenceServiceProtocol
    ) {
        self.networkService = networkService
        self.persistenceService = persistenceService
    }
    
    func search(query: String) async throws -> [SearchResult] {
        let results: [SearchResult] = try await networkService.get("/search?q=\(query)")
        
        // Save to recent searches
        if !recentSearches.contains(query) {
            recentSearches.insert(query, at: 0)
            if recentSearches.count > 10 {
                recentSearches.removeLast()
            }
            try? await persistenceService.save(recentSearches, forKey: "recent_searches")
        }
        
        return results
    }
    
    func loadRecentSearches() async {
        recentSearches = (try? await persistenceService.load(forKey: "recent_searches")) ?? []
    }
    
    func clearRecentSearches() async {
        recentSearches = []
        try? await persistenceService.delete(forKey: "recent_searches")
    }
}
```

**When to graduate**: Need search history across app, analytics, or search suggestions.

## Pattern Summary

| Feature Complexity | Architecture Level | Example |
|-------------------|-------------------|---------|
| Local UI state only | Level 1: @State | Settings toggles, tab selection |
| Single screen with logic | Level 2: ViewModel | Profile loading, form validation |
| Shared across features | Level 3: Service | Auth state, search history, network layer |

## Decision Process

Ask these questions:

1. **Does another screen need this logic?** → Yes = Level 3 Service
2. **Does this screen have API calls or complex logic?** → Yes = Level 2 ViewModel
3. **Is it just UI state?** → Yes = Level 1 @State

Start at Level 1 and refactor up as needs become clear.
