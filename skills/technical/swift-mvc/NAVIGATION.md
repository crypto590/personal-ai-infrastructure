# Navigation

**Referenced from**: [SKILL.md](SKILL.md), [CONTROLLERS.md](CONTROLLERS.md)

**Related**:
- [CONTROLLERS.md](CONTROLLERS.md) - Controllers own navigation intent
- [VIEWS.md](VIEWS.md) - Views implement navigation

---

## Overview

Controller owns navigation intent (enum), View owns mechanism (NavigationStack).

**Principle:**
- Controller declares WHAT to navigate to
- View implements HOW to navigate
- Separation of concerns

---

## Basic Navigation Pattern

```swift
// Controller declares destinations
@Observable
@MainActor
final class FeatureController {
    private(set) var navigationDestination: Destination?

    enum Destination: Hashable {
        case detail(id: String)
        case settings
    }

    func navigate(to destination: Destination) {
        navigationDestination = destination
    }

    func clearNavigation() {
        navigationDestination = nil
    }
}

// View implements navigation
struct FeatureView: View {
    @State private var controller = FeatureController()
    @State private var path = NavigationPath()

    var body: some View {
        NavigationStack(path: $path) {
            Content()
                .navigationDestination(for: FeatureController.Destination.self) { dest in
                    switch dest {
                    case .detail(let id): DetailView(id: id)
                    case .settings: SettingsView()
                    }
                }
                .onChange(of: controller.navigationDestination) { _, new in
                    if let destination = new {
                        path.append(destination)
                        controller.clearNavigation()
                    }
                }
        }
    }
}
```

---

## Navigation Rules

### ✅ Controller

- ✅ Owns navigation intent (enum)
- ✅ Provides navigation methods
- ✅ Clears navigation after triggering

### ✅ View

- ✅ Owns NavigationStack
- ✅ Owns NavigationPath
- ✅ Implements navigation destinations
- ✅ Listens to Controller navigation intent

### ❌ Never

- ❌ Controller never mutates NavigationPath
- ❌ Never store NavigationPath in Controller
- ❌ View never decides what to navigate to (delegates to Controller)

---

## Push Navigation

### Basic Push

```swift
@Observable
@MainActor
final class ListController {
    private(set) var navigationDestination: Destination?

    enum Destination: Hashable {
        case detail(Item)
    }

    func selectItem(_ item: Item) {
        navigationDestination = .detail(item)
    }

    func clearNavigation() {
        navigationDestination = nil
    }
}

struct ListView: View {
    @State private var controller = ListController()
    @State private var path = NavigationPath()

    var body: some View {
        NavigationStack(path: $path) {
            List(controller.items) { item in
                Button(item.name) {
                    controller.selectItem(item)
                }
            }
            .navigationDestination(for: ListController.Destination.self) { dest in
                switch dest {
                case .detail(let item):
                    DetailView(item: item)
                }
            }
            .onChange(of: controller.navigationDestination) { _, new in
                if let destination = new {
                    path.append(destination)
                    controller.clearNavigation()
                }
            }
        }
    }
}
```

### Multiple Destinations

```swift
enum Destination: Hashable {
    case userProfile(User)
    case postDetail(Post)
    case settings
    case about
}

// View
.navigationDestination(for: FeatureController.Destination.self) { dest in
    switch dest {
    case .userProfile(let user):
        UserProfileView(user: user)
    case .postDetail(let post):
        PostDetailView(post: post)
    case .settings:
        SettingsView()
    case .about:
        AboutView()
    }
}
```

---

## Modal Presentation

### Sheet

```swift
// Controller declares sheet
@Observable
@MainActor
final class FeatureController {
    private(set) var sheet: Sheet?

    enum Sheet: Identifiable {
        case edit(Item)
        case add
        case share(String)

        var id: String {
            switch self {
            case .edit(let item): return "edit-\(item.id)"
            case .add: return "add"
            case .share(let content): return "share-\(content)"
            }
        }
    }

    func showEdit(_ item: Item) {
        sheet = .edit(item)
    }

    func showAdd() {
        sheet = .add
    }

    func showShare(_ content: String) {
        sheet = .share(content)
    }

    func dismissSheet() {
        sheet = nil
    }
}

// View renders sheet
struct FeatureView: View {
    @State private var controller = FeatureController()

    var body: some View {
        Content()
            .sheet(item: $controller.sheet) { sheet in
                switch sheet {
                case .edit(let item):
                    EditView(item: item)
                case .add:
                    AddView()
                case .share(let content):
                    ShareSheet(content: content)
                }
            }
    }
}
```

### Full Screen Cover

```swift
@Observable
@MainActor
final class OnboardingController {
    private(set) var showingOnboarding = false

    func startOnboarding() {
        showingOnboarding = true
    }

    func completeOnboarding() {
        showingOnboarding = false
    }
}

struct AppView: View {
    @State private var controller = OnboardingController()

    var body: some View {
        MainContent()
            .fullScreenCover(isPresented: Binding(
                get: { controller.showingOnboarding },
                set: { if !$0 { controller.completeOnboarding() } }
            )) {
                OnboardingView()
            }
    }
}
```

---

## Programmatic Dismiss

### Sheet Dismissal

```swift
// Child view
struct EditView: View {
    @Environment(\.dismiss) var dismiss
    @State private var controller = EditController()

    var body: some View {
        Form {
            // ...
        }
        .toolbar {
            Button("Save") {
                Task {
                    await controller.save()
                    dismiss()
                }
            }
        }
    }
}
```

### Coordinated Dismissal

```swift
// Child controller signals completion
@Observable
@MainActor
final class EditController {
    private(set) var shouldDismiss = false

    func save() async {
        // ... save logic
        shouldDismiss = true
    }
}

// View handles dismiss
struct EditView: View {
    @Environment(\.dismiss) var dismiss
    @State private var controller = EditController()

    var body: some View {
        Form {
            // ...
        }
        .onChange(of: controller.shouldDismiss) { _, shouldDismiss in
            if shouldDismiss {
                dismiss()
            }
        }
    }
}
```

---

## Tab Navigation

```swift
@Observable
@MainActor
final class AppController {
    private(set) var selectedTab: Tab = .home

    enum Tab {
        case home
        case search
        case profile
    }

    func selectTab(_ tab: Tab) {
        selectedTab = tab
    }
}

struct AppView: View {
    @State private var controller = AppController()

    var body: some View {
        TabView(selection: Binding(
            get: { controller.selectedTab },
            set: { controller.selectTab($0) }
        )) {
            HomeView()
                .tabItem { Label("Home", systemImage: "house") }
                .tag(AppController.Tab.home)

            SearchView()
                .tabItem { Label("Search", systemImage: "magnifyingglass") }
                .tag(AppController.Tab.search)

            ProfileView()
                .tabItem { Label("Profile", systemImage: "person") }
                .tag(AppController.Tab.profile)
        }
    }
}
```

---

## Deep Linking

```swift
@Observable
@MainActor
final class AppController {
    private(set) var deepLink: DeepLink?

    enum DeepLink: Hashable {
        case post(id: String)
        case user(id: String)
        case settings
    }

    func handle(url: URL) {
        // Parse URL and set deepLink
        if url.pathComponents.contains("posts"),
           let id = url.pathComponents.last {
            deepLink = .post(id: id)
        }
    }

    func clearDeepLink() {
        deepLink = nil
    }
}

struct AppView: View {
    @State private var controller = AppController()
    @State private var path = NavigationPath()

    var body: some View {
        NavigationStack(path: $path) {
            HomeView()
                .navigationDestination(for: AppController.DeepLink.self) { link in
                    switch link {
                    case .post(let id):
                        PostView(id: id)
                    case .user(let id):
                        UserView(id: id)
                    case .settings:
                        SettingsView()
                    }
                }
        }
        .onOpenURL { url in
            controller.handle(url: url)
        }
        .onChange(of: controller.deepLink) { _, new in
            if let deepLink = new {
                path.append(deepLink)
                controller.clearDeepLink()
            }
        }
    }
}
```

---

## Navigation with Data Passing

### Passing Data to Destination

```swift
enum Destination: Hashable {
    case edit(item: Item)
}

.navigationDestination(for: Destination.self) { dest in
    switch dest {
    case .edit(let item):
        EditView(item: item)
    }
}
```

### Receiving Results from Destination

Use callbacks or shared state:

```swift
// Callback approach
struct ParentView: View {
    @State private var items: [Item] = []

    var body: some View {
        NavigationStack {
            List(items) { item in
                Text(item.name)
            }
            .navigationDestination(for: Destination.self) { dest in
                switch dest {
                case .add:
                    AddView { newItem in
                        items.append(newItem)
                    }
                }
            }
        }
    }
}

struct AddView: View {
    @Environment(\.dismiss) var dismiss
    let onSave: (Item) -> Void

    var body: some View {
        Form {
            // ...
            Button("Save") {
                onSave(newItem)
                dismiss()
            }
        }
    }
}
```

---

## Related

- [CONTROLLERS.md](CONTROLLERS.md) - Controllers manage navigation intent
- [VIEWS.md](VIEWS.md) - Views implement navigation
- [ADVANCED_PATTERNS.md](ADVANCED_PATTERNS.md) - Complex navigation patterns
- [EXAMPLES.md](EXAMPLES.md) - Real-world navigation examples
