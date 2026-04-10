# SwiftUI Tips and Modern Patterns

**Part of:** [ios-swift](../SKILL.md) > Review

Adapted from [twostraws/SwiftUI-Agent-Skill](https://github.com/twostraws/SwiftUI-Agent-Skill) (Paul Hudson, MIT).

Supplements `architecture/views.md` with optimization, deprecated API detection, and design compliance rules.

---

## Deprecated API Replacements

Flag these and suggest modern equivalents:

| Deprecated | Modern Replacement |
|---|---|
| `foregroundColor()` | `foregroundStyle()` |
| `cornerRadius()` | `clipShape(.rect(cornerRadius:))` |
| `tabItem()` | `Tab` API |
| `.navigationBarLeading/Trailing` | `.topBarLeading/Trailing` |
| Single-parameter `onChange()` | Two-parameter or no-parameter variant |
| `PreviewProvider` protocol | `#Preview` macro |
| `overlay(_:alignment:)` | `overlay(alignment:content:)` |
| `UIImpactFeedbackGenerator` etc. | `sensoryFeedback()` |
| `GeometryReader` (for sizing) | `containerRelativeFrame()`, `visualEffect()`, or `Layout` protocol |
| `ObservableObject` / `@Published` | `@Observable` class |
| `@StateObject` / `@ObservedObject` | `@State` / `@Bindable` / `@Environment` |
| `@EnvironmentObject` | `@Environment` with `@Observable` |

### @Entry Macro

Use `@Entry` for custom `EnvironmentValues`, `FocusValues`, `Transaction`, and `ContainerValues` keys instead of manually extending these types.

### iOS 26+

- Use native `WebView` (requires `import WebKit`) instead of wrapping `WKWebView`.
- `import Combine` now required explicitly if using `ObservableObject` (no longer auto-imported by SwiftUI).

---

## View Performance

### Conditional Views

Prefer ternary expressions over if/else branching to avoid `_ConditionalContent`:

```swift
// Preferred - single view identity
Text("Score")
    .foregroundStyle(isHighScore ? .green : .primary)

// Avoid - creates _ConditionalContent, resets view state
if isHighScore {
    Text("Score").foregroundStyle(.green)
} else {
    Text("Score").foregroundStyle(.primary)
}
```

### View Composition

- Break views into **dedicated View structs in separate files**, not computed properties or methods returning `some View`.
- One type per Swift file. Flag files with multiple type definitions.
- Avoid `AnyView`. Use `@ViewBuilder`, `Group`, or generics instead.

### Body Property

Assume `body` is called frequently. Move sorting, filtering, and transforms out of `body`:

```swift
// Preferred - derive outside body
@State private var sortedItems: [Item] = []

// Avoid - recomputes on every body evaluation
var body: some View {
    List(items.sorted { $0.name < $1.name }) { ... }
}
```

### Other Performance Rules

- Keep view initializers small — no non-trivial work.
- Avoid storing `DateFormatter` or similar formatters as properties — use `FormatStyle` APIs.
- Avoid expensive transforms in `List`/`ForEach` initializers (e.g., `items.filter { ... }`).
- Use `LazyVStack`/`LazyHStack` for large data sets in `ScrollView`.
- Prefer `task()` over `onAppear()` for async work.
- If a `ScrollView` has an opaque solid background, use `scrollContentBackground(.visible)`.
- Avoid storing escaping `@ViewBuilder` closures on views; store built view results instead.

---

## Design Compliance (HIG)

### Design Constants

Place standard fonts, sizes, colors, spacing, padding, corner radii, and animation timings into a shared enum:

```swift
enum Design {
    static let cornerRadius: CGFloat = 12
    static let standardPadding: CGFloat = 16
    static let animationDuration: Duration = .milliseconds(300)
}
```

### Layout Rules

- **Never** use `UIScreen.main.bounds`. Use `containerRelativeFrame()`, `visualEffect()`, or `GeometryReader`.
- Avoid fixed frames unless content fits neatly. Fixed frames break across device sizes and Dynamic Type.
- All interactive elements must be **44x44pt minimum** tap area.
- Avoid hard-coded padding/spacing values unless specifically requested.

### System Components

- Use `ContentUnavailableView` for empty/missing data (not custom empty states).
- With `searchable()`, use `ContentUnavailableView.search` (no manual text needed).
- Use `Label` over `HStack` when placing icons alongside text.
- Use system hierarchical styles (`.secondary`, `.tertiary`) instead of manual opacity.
- Wrap controls like `Slider` in `LabeledContent` within `Form`.
- `RoundedRectangle` defaults to `.continuous` — no need to specify.

### Typography

- Use `bold()` instead of `fontWeight(.bold)` — allows proper system weight selection.
- Use `fontWeight()` only for non-bold weights.
- Avoid `.caption2` (extremely small). Use `.caption` sparingly.
- Use SwiftUI `Color` or asset catalog colors, not `UIColor`.

---

## Animation

- Use `@Animatable` macro over manual `animatableData`. Mark non-animated properties with `@AnimatableIgnored`.
- **Never** use `animation()` without a value. Always provide a value to watch:
  ```swift
  .animation(.bouncy, value: score)
  ```
- Chain animations with `withAnimation` completion:
  ```swift
  withAnimation {
      scale = 2
  } completion: {
      withAnimation {
          scale = 1
      }
  }
  ```

---

## Data Flow

- `@Observable` classes must be `@MainActor` (unless project has Main Actor default isolation).
- `@State` must be `private` — only owned by the creating view.
- Avoid `Binding(get:set:)` in body code. Use bindings from `@State`/`@Binding` with `onChange()` for side effects.
- **Never** put `@AppStorage` inside an `@Observable` class (even with `@ObservationIgnored`) — it won't trigger view updates.
- Numeric `TextField`: bind to `Int`/`Double` with format:
  ```swift
  TextField("Score", value: $score, format: .number)
      .keyboardType(.numberPad)
  ```

---

## Navigation and Presentation

- Flag all use of deprecated `NavigationView` — use `NavigationStack` or `NavigationSplitView`.
- Prefer `navigationDestination(for:)` over `NavigationLink(destination:)`.
- **Never** mix `navigationDestination(for:)` and `NavigationLink(destination:)` in the same hierarchy — causes significant problems.
- `navigationDestination(for:)` must be registered once per data type — flag duplicates.
- Attach `confirmationDialog()` to the triggering UI element (enables correct Liquid Glass animations).
- Single-button "OK" alerts can omit the button entirely: `.alert("Title", isPresented: $showing) { }`.
- Prefer `sheet(item:)` over `sheet(isPresented:)` for optional data (safe unwrapping).
- When using `sheet(item:)` with a view that takes the item as its only init parameter, prefer: `sheet(item: $item, content: DetailView.init)`.

---

## View Patterns

- Extract button actions from body into separate methods.
- Prefer `TextField` with `axis: .vertical` over `TextEditor` (allows placeholder text). Use `lineLimit(5...)` for minimum height.
- Use `ImageRenderer` over `UIGraphicsImageRenderer`.
- `TabView(selection:)` should bind to an **enum**, not Int or String.
- Prefer `ForEach(items.enumerated(), id: \.element.id)` without converting to `Array`.
- Hide scroll indicators with `.scrollIndicators(.hidden)`.
- Button actions as parameter: `Button("Add", systemImage: "plus", action: addItem)`.
- Make structs conform to `Identifiable` rather than using `id: \.someProperty` in SwiftUI.

---

## Swift Style (Modern Idioms)

| Old Pattern | Modern Replacement |
|---|---|
| `replacingOccurrences(of:with:)` | `replacing("a", with: "b")` |
| `FileManager` directory lookups | `URL.documentsDirectory` |
| `String(format: "%.2f", value)` | `Text(value, format: .number.precision(.fractionLength(2)))` |
| `Circle()` | `.circle` (static member lookup) |
| `filter().count` | `count(where:)` |
| `Date()` | `Date.now` |
| `Task.sleep(nanoseconds:)` | `Task.sleep(for:)` |
| `if let value = value {` | `if let value {` |
| `CGFloat` | `Double` (except optionals/inout) |

### Expression Returns

Omit `return` for single-expression functions. Use `if`/`switch` as expressions:

```swift
var tileColor: Color {
    if isCorrect { .green } else { .red }
}
```

### String and Date

- Use `localizedStandardContains()` for user input filtering.
- Use `PersonNameComponents` with formatting for person names.
- Use `"y"` not `"yyyy"` for year format strings (API exchange exempt).
- Use `Date(myString, strategy: .iso8601)` for string-to-date conversion.

### Error Handling

Flag instances where errors from user actions are silently swallowed (only `print(error.localizedDescription)`).

---

## Code Hygiene

- No secrets/API keys in repositories.
- Never use `@AppStorage` for sensitive data — use Keychain.
- SwiftLint must produce zero warnings.
- For Localizable.xcstrings: use symbol keys, set `extractionState` to "manual", access via generated symbols like `Text(.helloWorld)`.
