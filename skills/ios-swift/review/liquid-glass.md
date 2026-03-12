# Liquid Glass Review

**Part of:** [ios-swift](../SKILL.md) > Review

**Trigger:** User has implemented iOS UI components with glass effects, after completing a SwiftUI feature with `.glassEffect()`, before PR review for iOS UI code, reviewing navigation bars/toolbars/overlays, checking performance of glass-heavy screens, validating accessibility compliance for glass UI.

---

## Review Checklist

### 0. Surface Appropriateness (Most Critical)

**Rule:** Liquid Glass = chrome & navigation, NOT content.

**Check:** Is glass being applied to the correct surface type?

| Surface Type | Glass OK? | Examples |
|--------------|-----------|----------|
| Navigation bars | YES | TabView, NavigationStack bars |
| Tab bars | YES | System TabView |
| Toolbars | YES | Floating action buttons, control panels |
| Sidebars | YES | iPad sidebar navigation |
| HUD overlays | YES | Volume indicators, temporary status |
| Search bars | YES | Overlay search fields |
| **Content cards** | NO | Player cards, list items, data displays |
| **Reading areas** | NO | Long-form text, articles |
| **Dense data** | NO | Tables, grids, rosters |
| **Forms/inputs** | NO | Text fields, pickers |

```swift
// BAD - content card with glass
struct PlayerCard: View {
    var body: some View {
        VStack { /* player info */ }
            .glassEffect()  // VIOLATION - content surface
    }
}

// GOOD - content card with solid background
struct PlayerCard: View {
    var body: some View {
        VStack { /* player info */ }
            .background(Color.appCard)
            .clipShape(RoundedRectangle(cornerRadius: 12))
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .stroke(Color.appBorder, lineWidth: 1)
            )
    }
}

// GOOD - navigation/chrome with glass
struct FloatingToolbar: View {
    var body: some View {
        HStack { /* toolbar buttons */ }
            .glassEffect()  // OK - chrome/UI element
    }
}
```

**Report format:**
```
SURFACE APPROPRIATENESS: [PASS/FAIL]
- Glass on chrome/navigation: [count]
- Glass on content surfaces: [count]
- Violations:
  - [file:line] - [surface type] should use solid background
- Fix: Replace .glassEffect() with .background(Color.appCard) + border
```

---

### 1. Single Glass Layer Rule

**Check:** No glass effects stacked on top of each other.

```swift
// BAD - glass on glass
VStack {
    content
        .glassEffect()  // First glass layer
}
.glassEffect()  // Second glass layer - VIOLATION

// GOOD - single glass layer
VStack {
    content
        .background(Color.appCard)  // Solid background
}
.glassEffect()  // Only glass layer
```

**Report format:**
```
GLASS LAYERING: [PASS/FAIL]
- Location: [file:line]
- Issue: [description if fail]
- Fix: [recommendation if fail]
```

### 2. Contrast Compliance

**Check:** Text and icons on glass meet WCAG AA (4.5:1 for body, 3:1 for large text).

```swift
// Check foreground styles
Text("Label")
    .foregroundStyle(.primary)  // GOOD - system adaptive
    .glassEffect()

Text("Label")
    .foregroundColor(.gray)  // SUSPICIOUS - may fail contrast
    .glassEffect()
```

**Report format:**
```
CONTRAST: [PASS/WARN/FAIL]
- Foreground elements: [count]
- System styles used: [yes/no]
- Custom colors: [list any]
- Recommendation: [if applicable]
```

### 3. Performance Thresholds

**Check:** Glass effects within recommended limits.

| Screen Type | Max Glass Effects | Actual | Status |
|-------------|-------------------|--------|--------|
| Simple UI | 3-5 | ? | ? |
| Complex UI | 8-10 | ? | ? |
| Lists/Grids | 1-2 visible | ? | ? |

```swift
// Check for GlassEffectContainer usage
GlassEffectContainer(spacing: 40.0) {  // GOOD - grouped
    // Multiple glass effects
}

// Check for excessive individual glass effects
ForEach(items) { item in
    ItemView()
        .glassEffect()  // SUSPICIOUS in large lists
}
```

**Report format:**
```
PERFORMANCE: [PASS/WARN/FAIL]
- Total glass effects: [count]
- Container usage: [yes/no]
- List/grid glass: [count]
- Recommendation: [if applicable]
```

### 4. Accessibility Fallbacks

**Check:** Code handles Reduce Transparency setting.

```swift
// REQUIRED pattern
@Environment(\.accessibilityReduceTransparency) var reduceTransparency

if reduceTransparency {
    // Solid fallback
} else {
    // Glass effect
}
```

**Report format:**
```
ACCESSIBILITY: [PASS/FAIL]
- Reduce Transparency check: [present/missing]
- Fallback provided: [yes/no]
- Location: [file:line if missing]
```

### 5. API Usage

**Check:** Using native Liquid Glass APIs, not custom implementations.

```swift
// GOOD - native API
.glassEffect()
.buttonStyle(.glass)
.buttonStyle(.glassProminent)

// BAD - custom implementation
.background(.ultraThinMaterial)  // Legacy approach
.clipShape(RoundedRectangle(cornerRadius: 12))
.shadow(...)
```

**Report format:**
```
API USAGE: [PASS/WARN]
- Native glass APIs: [count]
- Legacy material usage: [count]
- Custom glass implementations: [count]
- Migration needed: [yes/no]
```

---

## Review Output Format

```markdown
## Liquid Glass Review: [Feature/File Name]

### Summary
- Overall: [PASS/NEEDS WORK/FAIL]
- Issues found: [count]
- Critical: [count]

### Surface Appropriateness
[details - most important check]

### Glass Layering
[details]

### Contrast Compliance
[details]

### Performance
[details]

### Accessibility
[details]

### API Usage
[details]

### Recommendations
1. [ordered by priority]
2. ...

### Code Fixes
[specific code changes if needed]
```

---

## Severity Levels

| Level | Criteria | Action |
|-------|----------|--------|
| Critical | Glass on content surfaces, glass on glass, missing accessibility | Block PR |
| Warning | Performance concerns, custom implementations | Address before shipping |
| Info | Style suggestions, optimization opportunities | Optional improvement |
