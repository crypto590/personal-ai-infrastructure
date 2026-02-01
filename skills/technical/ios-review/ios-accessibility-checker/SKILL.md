---
name: ios-accessibility-checker
description: Verify Assistive Access, VoiceOver, contrast compliance, and accessibility settings in iOS code. Checks tap targets, labels, reduce transparency/motion handling.
---

# iOS Accessibility Checker

**Category:** technical/ios-review

**Brief Description:** Code review agent that audits iOS implementations for accessibility compliance. Validates VoiceOver support, Assistive Access scenes, contrast ratios, minimum tap targets, accessibility labels, and system preference handling (Reduce Transparency, Reduce Motion, Increase Contrast).

---

## When to Use This Skill

Trigger this skill when:
- Before completing any iOS feature
- PR review for iOS UI code
- User mentions accessibility or VoiceOver
- Implementing custom controls
- Adding interactive elements
- Reviewing contrast or visibility
- Implementing Assistive Access support
- Checking system preference handling

---

## Audit Checklist

### 1. VoiceOver Support

**Check:** All interactive elements properly labeled.

```swift
// GOOD - Explicit label
Button(action: { }) {
    Image(systemName: "plus")
}
.accessibilityLabel("Add new item")

// BAD - No label for image-only button
Button(action: { }) {
    Image(systemName: "plus")  // VoiceOver: "button"
}

// GOOD - Combined label for complex view
HStack {
    Image(systemName: "star.fill")
    Text("4.5")
}
.accessibilityElement(children: .combine)
.accessibilityLabel("Rating 4.5 stars")
```

**Report format:**
```
VOICEOVER: [PASS/WARN/FAIL]
- Interactive elements: [count]
- With accessibility labels: [count]
- Image-only buttons without labels: [list]
- Complex views needing combination: [list]
```

### 2. Minimum Tap Targets

**Check:** All interactive elements meet 44x44pt minimum.

```swift
// GOOD - Meets minimum
Button("Tap") { }
    .frame(minWidth: 44, minHeight: 44)

// BAD - Too small
Button("X") { }
    .frame(width: 24, height: 24)  // VIOLATION

// Pattern for small visual elements
Image(systemName: "info.circle")
    .frame(width: 20, height: 20)  // Visual size
    .contentShape(Rectangle())
    .frame(width: 44, height: 44)  // Tap target
```

**Report format:**
```
TAP TARGETS: [PASS/FAIL]
- Interactive elements: [count]
- Below 44pt minimum: [list with sizes]
- Recommendation: Use contentShape for larger hit area
```

### 3. Reduce Transparency Handling

**Check:** Glass and translucent effects have solid fallbacks.

```swift
// REQUIRED pattern
@Environment(\.accessibilityReduceTransparency) var reduceTransparency

var body: some View {
    content
        .background {
            if reduceTransparency {
                Color(.systemBackground)  // Solid fallback
            } else {
                // Glass or translucent effect
            }
        }
}

// For glass effects specifically
.glassEffect(in: .rect(cornerRadius: 12), isEnabled: !reduceTransparency)
```

**Report format:**
```
REDUCE TRANSPARENCY: [PASS/FAIL]
- Translucent/glass effects: [count]
- With fallback handling: [count]
- Missing fallbacks: [list files:lines]
```

### 4. Reduce Motion Handling

**Check:** Animations respect motion preferences.

```swift
// REQUIRED pattern
@Environment(\.accessibilityReduceMotion) var reduceMotion

withAnimation(reduceMotion ? nil : .spring(duration: 0.3)) {
    isExpanded.toggle()
}

// For complex animations
.animation(reduceMotion ? nil : .default, value: state)
```

**Report format:**
```
REDUCE MOTION: [PASS/WARN]
- Animated transitions: [count]
- Respecting preference: [count]
- Animations ignoring preference: [list]
```

### 5. Increase Contrast Handling

**Check:** High contrast mode provides enhanced visibility.

```swift
// REQUIRED pattern
@Environment(\.accessibilityContrast) var contrast

var body: some View {
    Text("Label")
        .foregroundStyle(contrast == .high ? .primary : .secondary)

    // Or use system-adaptive colors
    Text("Label")
        .foregroundStyle(.primary)  // GOOD - automatically adapts
}
```

**Report format:**
```
INCREASE CONTRAST: [PASS/WARN]
- Text elements: [count]
- Using system colors: [count]
- Custom colors that may need adjustment: [list]
```

### 6. Contrast Ratios

**Check:** Text meets WCAG AA standards.

| Element Type | Minimum Ratio | Standard |
|--------------|---------------|----------|
| Body text | 4.5:1 | WCAG AA |
| Large text (18pt+) | 3:1 | WCAG AA |
| UI components | 3:1 | WCAG 2.1 |

```swift
// GOOD - High contrast
Text("Important")
    .foregroundStyle(.primary)  // System handles contrast

// SUSPICIOUS - Custom color
Text("Warning")
    .foregroundColor(Color(hex: "#999999"))  // Check contrast!
```

**Report format:**
```
CONTRAST RATIOS: [PASS/WARN/FAIL]
- Text with system colors: [count]
- Text with custom colors: [count]
- Potential contrast issues: [list with color values]
```

### 7. Assistive Access Scene (iOS 26+)

**Check:** App provides simplified interface for Assistive Access mode.

```swift
// REQUIRED for iOS 26+
@main
struct App: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }

        // Simplified scene for Assistive Access
        AssistiveAccess {
            SimplifiedContentView()
        }
    }
}
```

**Report format:**
```
ASSISTIVE ACCESS: [PASS/WARN/N/A]
- AssistiveAccess scene present: [yes/no]
- Simplified views provided: [yes/no]
- Navigation icons set: [yes/no]
```

### 8. Accessibility Actions

**Check:** Complex gestures have accessible alternatives.

```swift
// GOOD - Accessible alternative for swipe
Row()
    .swipeActions {
        Button("Delete") { delete() }
    }
    .accessibilityAction(named: "Delete") {
        delete()  // Available via VoiceOver actions menu
    }

// GOOD - Custom action for drag gesture
DraggableView()
    .accessibilityAction(named: "Move up") { moveUp() }
    .accessibilityAction(named: "Move down") { moveDown() }
```

**Report format:**
```
ACCESSIBLE ACTIONS: [PASS/WARN]
- Custom gestures: [count]
- With accessible alternatives: [count]
- Missing alternatives: [list]
```

---

## Audit Output Format

```markdown
## iOS Accessibility Audit: [Feature/File Name]

### Summary
- Overall: [PASS/NEEDS WORK/FAIL]
- Issues found: [count]
- Critical (blocks users): [count]

### VoiceOver Support
[details]

### Tap Targets
[details]

### System Preferences
- Reduce Transparency: [status]
- Reduce Motion: [status]
- Increase Contrast: [status]

### Contrast Ratios
[details]

### Assistive Access
[details]

### Accessibility Actions
[details]

### Testing Checklist
- [ ] Test with VoiceOver enabled
- [ ] Test with Reduce Transparency
- [ ] Test with Reduce Motion
- [ ] Test with Increase Contrast
- [ ] Verify all tap targets ≥ 44pt
- [ ] Test Assistive Access scene (iOS 26+)

### Recommendations
1. [ordered by severity]
2. ...
```

---

## Severity Levels

| Level | Criteria | Action |
|-------|----------|--------|
| Critical | Missing VoiceOver labels on buttons, tap targets < 44pt | Block PR |
| Warning | Missing Reduce Transparency fallback, no Assistive Access scene | Address before App Store |
| Info | Optimization opportunities, enhanced experience suggestions | Optional improvement |

---

## Testing Commands

```bash
# Enable VoiceOver via Accessibility Shortcut
# Settings → Accessibility → Accessibility Shortcut → VoiceOver

# Test with Accessibility Inspector
# Xcode → Open Developer Tool → Accessibility Inspector

# Preview with Assistive Access trait
#Preview(traits: .assistiveAccess) {
    SimplifiedView()
}
```

---

## Dependencies

**Required context:**
- `/Users/coreyyoung/Desktop/Projects/athlead/docs/design-conventions.md` - Contrast matrix
- `/Users/coreyyoung/Desktop/Projects/athlead/docs/liquid-glass-conventions.md` - Glass accessibility
- `/Users/coreyyoung/Desktop/Projects/athlead/docs/swift-best-practices.md` - Assistive Access patterns

**Related skills:**
- `ios-liquid-glass-reviewer` - Glass-specific accessibility
- `swiftui-pattern-validator` - General SwiftUI patterns
