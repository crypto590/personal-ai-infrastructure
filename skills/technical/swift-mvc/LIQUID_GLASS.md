# Liquid Glass Design System (iOS 26+)

**Referenced from**: [SKILL.md](SKILL.md), [VIEWS.md](VIEWS.md)

**Related**:
- [VIEWS.md](VIEWS.md) - SwiftUI views that use Liquid Glass

---

## Overview

**Liquid Glass** is Apple's translucent material system that reflects and refracts surroundings while dynamically transforming to bring focus to content.

**Availability:** iOS 26+, iPadOS 26+, macOS Tahoe 26+, watchOS 26+, tvOS 26+

---

## Basic Usage

Apply Liquid Glass effects using the `glassEffect()` modifier:

```swift
// Default glass effect (Capsule shape)
Text("Hello, World!")
    .font(.title)
    .padding()
    .glassEffect()

// Custom shape
Text("Hello, World!")
    .font(.title)
    .padding()
    .glassEffect(in: .rect(cornerRadius: 16.0))

// Tinted and interactive
Text("Hello, World!")
    .font(.title)
    .padding()
    .glassEffect(.regular.tint(.orange).interactive())
```

---

## Glass Effect Variants

```swift
// Regular glass (default)
.glassEffect()

// Tinted glass (use sparingly for meaning, not just decoration)
.glassEffect(.regular.tint(.purple.opacity(0.12)))

// Interactive glass (responds to touch/pointer)
.glassEffect(.regular.interactive())

// Combined tint + interactive
.glassEffect(.regular.tint(.blue.opacity(0.1)).interactive())
```

---

## Custom Shapes

```swift
// Rounded rectangle
.glassEffect(in: .rect(cornerRadius: 12.0))

// Circle
.glassEffect(in: .circle)

// Custom shape
.glassEffect(in: RoundedRectangle(cornerRadius: 20, style: .continuous))
```

---

## Native Glass Button Styles

For buttons, use native glass button styles instead of custom implementations:

```swift
// Standard glass button
Button("Sign In") {
    // action
}
.buttonStyle(.glass)

// Prominent glass button (for primary actions)
Button("Get Started") {
    // action
}
.buttonStyle(.glassProminent)
```

---

## Multiple Glass Effects with Containers

Use `GlassEffectContainer` when applying glass effects to multiple views for optimal performance and shape blending:

```swift
GlassEffectContainer(spacing: 40.0) {
    HStack(spacing: 40.0) {
        Image(systemName: "scribble.variable")
            .frame(width: 80.0, height: 80.0)
            .font(.system(size: 36))
            .glassEffect()

        Image(systemName: "eraser.fill")
            .frame(width: 80.0, height: 80.0)
            .font(.system(size: 36))
            .glassEffect()
    }
}
```

**Container spacing** controls how glass effects blend together:
- Larger spacing = effects blend sooner during transitions
- When views are closer than spacing, effects merge at rest
- Creates fluid morphing animations as views move

---

## Unified Glass Effects

Combine multiple views into a single glass shape using `glassEffectUnion`:

```swift
@Namespace private var namespace
let symbolSet = ["cloud.bolt.rain.fill", "sun.rain.fill", "moon.stars.fill", "moon.fill"]

GlassEffectContainer(spacing: 20.0) {
    HStack(spacing: 20.0) {
        ForEach(symbolSet.indices, id: \.self) { item in
            Image(systemName: symbolSet[item])
                .frame(width: 80.0, height: 80.0)
                .font(.system(size: 36))
                .glassEffect()
                .glassEffectUnion(id: item < 2 ? "1" : "2", namespace: namespace)
        }
    }
}
```

---

## Morphing Transitions

Coordinate glass effect transitions using `glassEffectID` and `glassEffectTransition`:

```swift
@State private var isExpanded: Bool = false
@Namespace private var namespace

GlassEffectContainer(spacing: 40.0) {
    HStack(spacing: 40.0) {
        Image(systemName: "scribble.variable")
            .frame(width: 80.0, height: 80.0)
            .font(.system(size: 36))
            .glassEffect()
            .glassEffectID("pencil", in: namespace)

        if isExpanded {
            Image(systemName: "eraser.fill")
                .frame(width: 80.0, height: 80.0)
                .font(.system(size: 36))
                .glassEffect()
                .glassEffectID("eraser", in: namespace)
        }
    }
}

Button("Toggle") {
    withAnimation {
        isExpanded.toggle()
    }
}
.buttonStyle(.glass)
```

**Transition Types:**
- **matchedGeometry** (default): For effects within container spacing
- **materialize**: For effects farther apart than container spacing

---

## Liquid Glass Rules

### ✅ DO

- Use `.glassEffect()` for custom components requiring translucent backgrounds
- Use `.buttonStyle(.glass)` or `.buttonStyle(.glassProminent)` for buttons
- Use `GlassEffectContainer` when multiple glass effects are near each other
- Apply tints sparingly to convey meaning (e.g., primary actions, states)
- Use `.interactive()` for custom tappable components
- Apply `glassEffect()` after other appearance modifiers

### ❌ DON'T

- Don't create too many containers on screen (performance impact)
- Don't use tints for pure decoration
- Don't apply glass effects to too many views simultaneously
- Don't implement custom glass effects - use native API
- Don't add gesture handlers that interfere with `.interactive()`

---

## Migration from Custom Glass Effects

If you have custom glass implementations (e.g., using `.ultraThinMaterial`), migrate to native Liquid Glass:

**Before (Custom):**
```swift
.background(.ultraThinMaterial)
.clipShape(RoundedRectangle(cornerRadius: 12))
.shadow(color: .black.opacity(0.1), radius: 10)
```

**After (Native):**
```swift
.glassEffect(in: .rect(cornerRadius: 12))
```

**Benefits:**
- Native system performance optimizations
- Automatic adaptation to system theme
- Built-in interactive states
- Morphing and blending animations
- Future-proof as Apple refines the design language

---

## Performance Considerations

- Limit the number of glass effects on screen simultaneously
- Use `GlassEffectContainer` for clusters of glass views
- Profile with Instruments if experiencing performance issues
- Consider reducing complexity for lower-end devices

---

## Component Library Pattern

Create reusable glass components for consistency:

```swift
// Shared/Components/GlassCard.swift
struct GlassCard<Content: View>: View {
    let content: Content

    init(@ViewBuilder content: () -> Content) {
        self.content = content()
    }

    var body: some View {
        content
            .padding()
            .glassEffect(in: .rect(cornerRadius: 16))
    }
}

// Usage
GlassCard {
    VStack {
        Text("Title")
        Text("Description")
    }
}
```

---

## Integration with MVC

### In Views

```swift
struct DashboardView: View {
    @State private var controller = DashboardController()

    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                // Use glass for cards
                GlassCard {
                    VStack {
                        Text("Welcome, \(controller.userName)")
                        Text("\(controller.itemCount) items")
                    }
                }

                // Glass buttons for actions
                Button("Load More") {
                    Task { await controller.loadMore() }
                }
                .buttonStyle(.glassProminent)
            }
        }
    }
}
```

### Creating Reusable Components

```swift
// Component with controller integration
struct StatCard: View {
    let title: String
    let value: String
    let isLoading: Bool

    var body: some View {
        VStack {
            if isLoading {
                ProgressView()
            } else {
                Text(title)
                    .font(.headline)
                Text(value)
                    .font(.largeTitle)
            }
        }
        .frame(maxWidth: .infinity)
        .padding()
        .glassEffect(in: .rect(cornerRadius: 16))
    }
}

// Usage
StatCard(
    title: "Total Items",
    value: "\(controller.itemCount)",
    isLoading: controller.isLoading
)
```

---

## Further Reading

- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass) - Official Apple guide for iOS 26 design system

---

## Related

- [VIEWS.md](VIEWS.md) - SwiftUI views that use Liquid Glass
- [EXAMPLES.md](EXAMPLES.md) - Real-world Liquid Glass examples
