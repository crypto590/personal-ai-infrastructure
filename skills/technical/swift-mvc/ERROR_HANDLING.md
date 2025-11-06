# Error Handling

**Referenced from**: [SKILL.md](SKILL.md), [CONTROLLERS.md](CONTROLLERS.md), [SERVICES.md](SERVICES.md)

**Related**:
- [CONTROLLERS.md](CONTROLLERS.md) - Controllers handle errors
- [SERVICES.md](SERVICES.md) - Services throw errors

---

## Overview

Controllers handle errors from Services and present them to users. Keep it simple and pragmatic.

**Philosophy:**
- Services throw specific errors
- Controllers catch and present errors
- Views display error UI
- Keep it simple unless complexity is needed

---

## Basic Pattern

```swift
@Observable
@MainActor
final class FeatureController {
    private(set) var errorMessage: String?
    private(set) var isLoading = false

    func performAction() async {
        isLoading = true
        errorMessage = nil  // Clear previous error
        defer { isLoading = false }

        do {
            try await service.doSomething()
        } catch {
            if !Task.isCancelled {
                errorMessage = error.localizedDescription
            }
        }
    }

    func clearError() {
        errorMessage = nil
    }
}

// View displays error
struct FeatureView: View {
    @State private var controller = FeatureController()

    var body: some View {
        Content()
            .alert("Error", isPresented: .constant(controller.errorMessage != nil)) {
                Button("OK") { controller.clearError() }
            } message: {
                Text(controller.errorMessage ?? "")
            }
    }
}
```

---

## Error Handling Rules

### ✅ Always

**1. Check Task.isCancelled**
```swift
catch {
    if !Task.isCancelled {
        errorMessage = error.localizedDescription
    }
}
```

**Why:** Prevents showing errors for cancelled tasks.

**2. Clear errors before retrying**
```swift
func performAction() async {
    errorMessage = nil  // Clear previous error
    // ... perform action
}
```

**3. Provide clear user-facing messages**
```swift
catch {
    if !Task.isCancelled {
        errorMessage = "Unable to load data. Please try again."
    }
}
```

### ❌ Don't

**1. Don't show technical errors to users**
```swift
// ❌ BAD
errorMessage = "URLSession error: -1009"

// ✅ GOOD
errorMessage = "No internet connection. Please check your network."
```

**2. Don't set error state after cancellation**
```swift
// ❌ BAD
catch {
    errorMessage = error.localizedDescription  // Even if cancelled!
}

// ✅ GOOD
catch {
    if !Task.isCancelled {
        errorMessage = error.localizedDescription
    }
}
```

---

## Custom Error Types

For better control over error messages, define app-specific errors:

```swift
enum AppError: LocalizedError {
    case networkUnavailable
    case authenticationRequired
    case invalidInput(String)
    case serverError(Int)

    var errorDescription: String? {
        switch self {
        case .networkUnavailable:
            return "No internet connection. Please try again."
        case .authenticationRequired:
            return "Please sign in to continue."
        case .invalidInput(let field):
            return "\(field) is invalid."
        case .serverError(let code):
            return "Server error (\(code)). Please try again later."
        }
    }
}
```

### Service Layer

```swift
actor NetworkService {
    func get<T: Decodable>(_ endpoint: String) async throws -> T {
        guard Reachability.isConnected else {
            throw AppError.networkUnavailable
        }

        let (data, response) = try await URLSession.shared.data(from: url)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw AppError.serverError(0)
        }

        if httpResponse.statusCode == 401 {
            throw AppError.authenticationRequired
        }

        if httpResponse.statusCode >= 500 {
            throw AppError.serverError(httpResponse.statusCode)
        }

        return try JSONDecoder().decode(T.self, from: data)
    }
}
```

### Controller Layer

```swift
@Observable
@MainActor
final class DataController {
    private(set) var errorMessage: String?

    func loadData() async {
        errorMessage = nil

        do {
            data = try await service.fetchData()
        } catch let appError as AppError {
            if !Task.isCancelled {
                errorMessage = appError.errorDescription
            }
        } catch {
            if !Task.isCancelled {
                errorMessage = "An unexpected error occurred."
            }
        }
    }
}
```

---

## Error State Patterns

### Single Error Message

```swift
@Observable
@MainActor
final class FeatureController {
    private(set) var errorMessage: String?

    func clearError() {
        errorMessage = nil
    }
}
```

**Use when:** Simple error display is sufficient.

### Error with Retry

```swift
@Observable
@MainActor
final class DataController {
    private(set) var error: Error?
    private(set) var canRetry = false

    func loadData() async {
        error = nil
        canRetry = false

        do {
            data = try await service.fetchData()
        } catch let networkError as NetworkError {
            if !Task.isCancelled {
                error = networkError
                canRetry = networkError.isRecoverable
            }
        }
    }

    func retry() async {
        await loadData()
    }
}

// View
.alert("Error", isPresented: .constant(controller.error != nil)) {
    Button("OK") { controller.clearError() }
    if controller.canRetry {
        Button("Retry") {
            Task { await controller.retry() }
        }
    }
}
```

### Multiple Error Types

```swift
@Observable
@MainActor
final class FormController {
    private(set) var validationErrors: [String: String] = [:]
    private(set) var submissionError: String?

    func validate() {
        validationErrors.removeAll()

        if !ValidationService.isValidEmail(email) {
            validationErrors["email"] = "Invalid email address"
        }

        if !ValidationService.isValidPassword(password) {
            validationErrors["password"] = "Password must be at least 8 characters"
        }
    }

    func submit() async {
        validate()
        guard validationErrors.isEmpty else { return }

        submissionError = nil

        do {
            try await service.submit(email: email, password: password)
        } catch {
            if !Task.isCancelled {
                submissionError = error.localizedDescription
            }
        }
    }
}

// View
TextField("Email", text: $email)
if let error = controller.validationErrors["email"] {
    Text(error).foregroundColor(.red)
}
```

---

## View Error Patterns

### Alert

```swift
.alert("Error", isPresented: .constant(controller.errorMessage != nil)) {
    Button("OK") { controller.clearError() }
} message: {
    Text(controller.errorMessage ?? "")
}
```

### Inline Error

```swift
if let error = controller.errorMessage {
    HStack {
        Image(systemName: "exclamationmark.triangle")
        Text(error)
    }
    .foregroundColor(.red)
    .padding()
}
```

### Error View

```swift
if let error = controller.errorMessage {
    ErrorView(message: error) {
        controller.clearError()
    } retry: {
        Task { await controller.retry() }
    }
}

struct ErrorView: View {
    let message: String
    let onDismiss: () -> Void
    let retry: () -> Void

    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: "exclamationmark.triangle")
                .font(.largeTitle)
                .foregroundColor(.red)

            Text(message)
                .multilineTextAlignment(.center)

            HStack {
                Button("Dismiss", action: onDismiss)
                Button("Retry", action: retry)
                    .buttonStyle(.borderedProminent)
            }
        }
        .padding()
    }
}
```

---

## Validation Errors

### Form Validation

```swift
@Observable
@MainActor
final class SignUpController {
    private(set) var email = ""
    private(set) var password = ""
    private(set) var confirmPassword = ""

    private(set) var emailError: String?
    private(set) var passwordError: String?
    private(set) var confirmPasswordError: String?

    private(set) var isValid = false

    func updateEmail(_ newEmail: String) {
        email = newEmail
        validateEmail()
        updateValidity()
    }

    func updatePassword(_ newPassword: String) {
        password = newPassword
        validatePassword()
        updateValidity()
    }

    func updateConfirmPassword(_ newPassword: String) {
        confirmPassword = newPassword
        validateConfirmPassword()
        updateValidity()
    }

    private func validateEmail() {
        if email.isEmpty {
            emailError = nil
        } else if !ValidationService.isValidEmail(email) {
            emailError = "Invalid email address"
        } else {
            emailError = nil
        }
    }

    private func validatePassword() {
        if password.isEmpty {
            passwordError = nil
        } else if !ValidationService.isValidPassword(password) {
            passwordError = "Password must be at least 8 characters"
        } else {
            passwordError = nil
        }
    }

    private func validateConfirmPassword() {
        if confirmPassword.isEmpty {
            confirmPasswordError = nil
        } else if password != confirmPassword {
            confirmPasswordError = "Passwords don't match"
        } else {
            confirmPasswordError = nil
        }
    }

    private func updateValidity() {
        isValid = emailError == nil &&
                  passwordError == nil &&
                  confirmPasswordError == nil &&
                  !email.isEmpty &&
                  !password.isEmpty &&
                  !confirmPassword.isEmpty
    }
}

// View
VStack {
    TextField("Email", text: Binding(
        get: { controller.email },
        set: { controller.updateEmail($0) }
    ))
    if let error = controller.emailError {
        Text(error).foregroundColor(.red)
    }
}
```

---

## Network Error Example

```swift
enum NetworkError: LocalizedError {
    case noConnection
    case timeout
    case unauthorized
    case serverError
    case invalidResponse

    var errorDescription: String? {
        switch self {
        case .noConnection:
            return "No internet connection"
        case .timeout:
            return "Request timed out"
        case .unauthorized:
            return "Please sign in to continue"
        case .serverError:
            return "Server error. Please try again later."
        case .invalidResponse:
            return "Invalid response from server"
        }
    }

    var isRecoverable: Bool {
        switch self {
        case .noConnection, .timeout, .serverError:
            return true
        case .unauthorized, .invalidResponse:
            return false
        }
    }
}
```

---

## Best Practices

### ✅ DO

1. **Use localizedDescription for simple cases**
```swift
errorMessage = error.localizedDescription
```

2. **Define custom errors when you need specific messaging**
```swift
enum AppError: LocalizedError { ... }
```

3. **Clear errors before retrying**
```swift
errorMessage = nil
await performAction()
```

4. **Validate early**
```swift
guard isValid else { return }
await submit()
```

### ❌ DON'T

1. **Don't over-engineer**
   - Basic String errors are fine for most cases
   - Add complexity only when needed

2. **Don't show technical details to users**
   - No stack traces
   - No error codes (unless meaningful)
   - User-friendly messages

3. **Don't skip cancellation checks**
```swift
// ❌ BAD
catch {
    errorMessage = error.localizedDescription
}

// ✅ GOOD
catch {
    if !Task.isCancelled {
        errorMessage = error.localizedDescription
    }
}
```

---

## Related

- [CONTROLLERS.md](CONTROLLERS.md) - Controller error handling
- [SERVICES.md](SERVICES.md) - Service error throwing
- [EXAMPLES.md](EXAMPLES.md) - Real-world error handling examples
