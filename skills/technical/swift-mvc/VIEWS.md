# Views (SwiftUI)

**Referenced from**: [SKILL.md](SKILL.md), [CONTROLLERS.md](CONTROLLERS.md)

**Related**:
- [CONTROLLERS.md](CONTROLLERS.md) - Controllers that Views use
- [NAVIGATION.md](NAVIGATION.md) - Navigation patterns
- [LIQUID_GLASS.md](LIQUID_GLASS.md) - iOS 26+ design system

---

## Overview

Views render UI and delegate actions to Controllers. They observe Controller state and never mutate it directly.

**Key characteristics:**
- Create Controller with `@State private var`
- Delegate all actions to Controller methods
- Never call Services directly
- Never mutate Controller properties (read-only via `private(set)`)
- No business logic in Views

---

## Basic Pattern

```swift
struct UserView: View {
    @State private var controller = UserController()

    var body: some View {
        Group {
            if controller.isLoading {
                ProgressView()
            } else if let user = controller.user {
                VStack {
                    Text(user.displayName)
                    Text(user.email)
                }
            } else {
                Text("No user")
            }
        }
        .task {
            await controller.loadUser(id: "123")
        }
    }
}
```

---

## Rules

### ✅ DO

**1. Create Controller with @State**
```swift
struct FeatureView: View {
    @State private var controller = FeatureController()
    // ...
}
```

**2. Delegate actions to Controller**
```swift
Button("Load") {
    Task {
        await controller.loadData()
    }
}
```

**3. Read Controller state**
```swift
if controller.isLoading {
    ProgressView()
}
```

**4. Use .task for initial loading**
```swift
.task {
    await controller.load()
}
```

### ❌ DON'T

**1. Never mutate Controller properties**
```swift
// ❌ BAD - Can't compile (private(set))
controller.user = newUser

// ✅ GOOD - Delegate to Controller
controller.updateUser(newUser)
```

**2. Never call Services directly**
```swift
// ❌ BAD
@State private var service = UserService()

Button("Load") {
    Task {
        user = try await service.fetchUser(id: "123")
    }
}

// ✅ GOOD
@State private var controller = UserController()

Button("Load") {
    Task {
        await controller.loadUser(id: "123")
    }
}
```

**3. Never put business logic in Views**
```swift
// ❌ BAD
var isValid: Bool {
    email.contains("@") && password.count >= 8
}

// ✅ GOOD - Put in Controller
// Controller has: private(set) var isValid: Bool
```

---

## Common Patterns

### Loading States

```swift
struct DataView: View {
    @State private var controller = DataController()

    var body: some View {
        Group {
            if controller.isLoading {
                ProgressView("Loading...")
            } else if let error = controller.errorMessage {
                ErrorView(message: error) {
                    Task { await controller.retry() }
                }
            } else if controller.data.isEmpty {
                EmptyStateView()
            } else {
                DataList(items: controller.data)
            }
        }
        .task {
            await controller.load()
        }
    }
}
```

### Forms

```swift
struct SignUpView: View {
    @State private var controller = SignUpController()
    @State private var email = ""
    @State private var password = ""

    var body: some View {
        Form {
            TextField("Email", text: $email)
                .textContentType(.emailAddress)
                .autocapitalization(.none)
                .onChange(of: email) { _, newValue in
                    controller.updateEmail(newValue)
                }

            SecureField("Password", text: $password)
                .textContentType(.newPassword)
                .onChange(of: password) { _, newValue in
                    controller.updatePassword(newValue)
                }

            Button("Sign Up") {
                Task {
                    await controller.signUp()
                }
            }
            .disabled(!controller.isValid || controller.isLoading)
        }
        .alert("Error", isPresented: .constant(controller.errorMessage != nil)) {
            Button("OK") { controller.clearError() }
        } message: {
            Text(controller.errorMessage ?? "")
        }
    }
}
```

### Lists

```swift
struct PostListView: View {
    @State private var controller = PostListController()

    var body: some View {
        List(controller.posts) { post in
            PostRow(post: post)
                .onTapGesture {
                    controller.selectPost(post)
                }
        }
        .refreshable {
            await controller.refresh()
        }
        .task {
            await controller.load()
        }
    }
}
```

### Search

```swift
struct SearchView: View {
    @State private var controller = SearchController()

    var body: some View {
        VStack {
            SearchField(text: Binding(
                get: { controller.query },
                set: { controller.updateQuery($0) }
            ))

            if controller.isSearching {
                ProgressView()
            } else if controller.results.isEmpty {
                Text("No results")
            } else {
                List(controller.results) { result in
                    ResultRow(result: result)
                }
            }
        }
    }
}

struct SearchField: View {
    @Binding var text: String

    var body: some View {
        TextField("Search", text: $text)
            .textFieldStyle(.roundedBorder)
            .padding()
    }
}
```

---

## View Composition

### Extract Subviews

```swift
// Parent view
struct ProfileView: View {
    @State private var controller = ProfileController()

    var body: some View {
        ScrollView {
            if let user = controller.user {
                ProfileHeader(user: user)
                ProfileBio(bio: user.bio)
                ProfileStats(posts: controller.posts)
            }
        }
        .task {
            await controller.load()
        }
    }
}

// Subviews receive data, not controllers
struct ProfileHeader: View {
    let user: User

    var body: some View {
        VStack {
            AsyncImage(url: user.avatarURL)
            Text(user.displayName)
        }
    }
}

struct ProfileBio: View {
    let bio: String?

    var body: some View {
        if let bio {
            Text(bio)
                .padding()
        }
    }
}
```

**Pattern:**
- Parent view owns Controller
- Child views receive data
- Keeps views reusable

---

## Passing Controllers to Child Views

Sometimes child views need to trigger Controller actions:

```swift
struct ParentView: View {
    @State private var controller = ParentController()

    var body: some View {
        VStack {
            ChildView(controller: controller)
        }
    }
}

struct ChildView: View {
    let controller: ParentController

    var body: some View {
        Button("Action") {
            Task {
                await controller.performAction()
            }
        }
    }
}
```

**When to use:**
- Child needs to trigger Controller actions
- Child shouldn't own its own Controller
- Parent coordinates overall state

**Alternative: Closures**
```swift
struct ChildView: View {
    let onAction: () async -> Void

    var body: some View {
        Button("Action") {
            Task { await onAction() }
        }
    }
}

// Usage
ChildView {
    await controller.performAction()
}
```

---

## Task Management

### .task Modifier

```swift
.task {
    await controller.load()
}
```

**Automatically:**
- Starts when view appears
- Cancels when view disappears
- Perfect for Controller methods

### Manual Task

```swift
@State private var loadTask: Task<Void, Never>?

.onAppear {
    loadTask = Task {
        await controller.load()
    }
}
.onDisappear {
    loadTask?.cancel()
}
```

**Use when:**
- Need manual control over task lifetime
- Multiple concurrent tasks
- Complex task coordination

**Recommendation:** Prefer `.task` modifier.

---

## Environment

### Reading Environment

```swift
struct FeatureView: View {
    @Environment(\.dismiss) var dismiss
    @State private var controller = FeatureController()

    var body: some View {
        Button("Save") {
            Task {
                await controller.save()
                dismiss()
            }
        }
    }
}
```

**Views can use @Environment.**
**Controllers should NOT use @Environment** (except for shared controllers).

### Shared Controllers

```swift
struct ParentView: View {
    @State private var appController = AppController.shared

    var body: some View {
        ChildView()
            .environment(\.appController, appController)
    }
}

struct ChildView: View {
    @Environment(\.appController) var appController

    var body: some View {
        Text(appController.currentUser?.name ?? "Guest")
    }
}
```

See [ADVANCED_PATTERNS.md](ADVANCED_PATTERNS.md#shared-controllers) for shared controller patterns.

---

## Related

- [CONTROLLERS.md](CONTROLLERS.md) - Controllers that Views use
- [NAVIGATION.md](NAVIGATION.md) - Navigation patterns
- [LIQUID_GLASS.md](LIQUID_GLASS.md) - iOS 26+ design system
- [EXAMPLES.md](EXAMPLES.md) - Real-world View examples
