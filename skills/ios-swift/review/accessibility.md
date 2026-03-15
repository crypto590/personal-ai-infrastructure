# iOS Accessibility Review

**Part of:** [ios-swift](../SKILL.md) > Review

**Trigger:** Before completing any iOS feature, PR review for iOS UI code, mentions of accessibility or VoiceOver, implementing custom controls, adding interactive elements, reviewing contrast or visibility, implementing Assistive Access support, checking system preference handling.

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

// BAD - Text-only plain button (especially prone to violation)
Button("Edit") { edit() }
    .buttonStyle(.plain)  // No default padding/chrome, tap target may be tiny

// GOOD - Plain button with explicit tap target
Button("Edit") { edit() }
    .buttonStyle(.plain)
    .frame(minWidth: 44, minHeight: 44)

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
- Plain-style buttons without explicit frame: [list]
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

### 9. VoiceOver Grouping

**Check:** Related elements grouped to avoid VoiceOver reading each child individually.

```swift
// BAD - VoiceOver reads icon and text as separate elements
HStack {
    Image(systemName: "clock")
    Text("5 min ago")
}

// GOOD - Combined into single VoiceOver element
HStack {
    Image(systemName: "clock")
    Text("5 min ago")
}
.accessibilityElement(children: .combine)

// GOOD - Custom label when .combine doesn't produce good output
HStack {
    Image(systemName: "star.fill")
    Image(systemName: "star.fill")
    Image(systemName: "star.fill")
    Image(systemName: "star")
    Image(systemName: "star")
}
.accessibilityElement(children: .ignore)
.accessibilityLabel("3 out of 5 stars")
```

**Report format:**
```
VOICEOVER GROUPING: [PASS/WARN]
- Composite views (icon + text rows, stat groups): [count]
- Properly grouped with .combine or .ignore: [count]
- Missing grouping: [list]
```

### 10. Accessibility Value Descriptions

**Check:** Sliders, steppers, and progress indicators provide meaningful `.accessibilityValue()`.

```swift
// BAD - VoiceOver reads raw number
Slider(value: $volume, in: 0...100)

// GOOD - meaningful description
Slider(value: $volume, in: 0...100)
    .accessibilityValue("\(Int(volume)) percent")

// GOOD - stepper with context
Stepper("Quantity: \(quantity)", value: $quantity, in: 1...10)
    .accessibilityValue("\(quantity) items")

// GOOD - progress with context
ProgressView(value: uploadProgress)
    .accessibilityValue("\(Int(uploadProgress * 100)) percent uploaded")
```

**Report format:**
```
ACCESSIBILITY VALUES: [PASS/WARN]
- Sliders/steppers/progress views: [count]
- With accessibilityValue: [count]
- Missing value descriptions: [list]
```

### 11. VoiceOver Sort Priority

**Check:** When visual reading order does not match logical reading order, use `.accessibilitySortPriority()`.

```swift
// Problem: header is visually at top but VoiceOver reads sidebar first
HStack {
    Sidebar()          // Read first by VoiceOver
    MainContent()      // Should be read first
}

// Fix: prioritize main content
HStack {
    Sidebar()
        .accessibilitySortPriority(0)
    MainContent()
        .accessibilitySortPriority(1)  // Higher = read first
}
```

**Report format:**
```
SORT PRIORITY: [PASS/WARN]
- Non-standard reading order layouts: [count]
- With sort priority set: [count]
- Potentially confusing VoiceOver order: [list]
```

### 12. Dismiss Action for Custom Overlays

**Check:** Custom sheets, popovers, and overlays provide `.accessibilityAction(.escape)` so VoiceOver users can dismiss them.

```swift
// BAD - custom overlay with no escape action
ZStack {
    content
    if showOverlay {
        CustomOverlay()  // No way for VoiceOver to dismiss
    }
}

// GOOD - escape action to dismiss
ZStack {
    content
    if showOverlay {
        CustomOverlay()
            .accessibilityAction(.escape) {
                showOverlay = false
            }
    }
}
```

**Report format:**
```
DISMISS ACTIONS: [PASS/WARN]
- Custom overlays/sheets: [count]
- With escape action: [count]
- Missing escape action: [list]
```

### 13. Live Regions for Dynamic Content

**Check:** Content that updates dynamically (timers, scores, live status) uses `.accessibilityAddTraits(.updatesFrequently)` so VoiceOver announces changes.

```swift
// BAD - score updates silently
Text("\(homeScore) - \(awayScore)")

// GOOD - VoiceOver announces updates
Text("\(homeScore) - \(awayScore)")
    .accessibilityAddTraits(.updatesFrequently)
    .accessibilityLabel("Score: \(homeTeam) \(homeScore), \(awayTeam) \(awayScore)")

// GOOD - countdown timer
Text(timerText)
    .accessibilityAddTraits(.updatesFrequently)
    .accessibilityLabel("Time remaining: \(timerText)")
```

**Report format:**
```
LIVE REGIONS: [PASS/WARN]
- Dynamic content (timers, scores, live indicators): [count]
- With updatesFrequently trait: [count]
- Missing live region markup: [list]
```

### 14. Magic Tap

**Check:** Media or primary-action screens implement `.accessibilityAction(.magicTap)` (two-finger double-tap) for the most important action.

```swift
// GOOD - play/pause in a media player
VideoPlayerView()
    .accessibilityAction(.magicTap) {
        isPlaying.toggle()
    }

// GOOD - start/stop in a workout tracker
WorkoutView()
    .accessibilityAction(.magicTap) {
        isTracking.toggle()
    }
```

**Report format:**
```
MAGIC TAP: [PASS/INFO]
- Media/primary-action screens: [count]
- With magicTap action: [count]
- Screens that would benefit: [list]
```

### 15. Custom Rotor Entries

**Check:** Complex lists with repeated structures (e.g., feed posts with headings, links, actions) expose custom rotor entries for efficient navigation.

```swift
// GOOD - custom rotor for navigating between post authors in a feed
ScrollView {
    LazyVStack {
        ForEach(posts) { post in
            PostRow(post: post)
                .accessibilityRotorEntry(id: post.id, in: .postAuthors)
        }
    }
}
.accessibilityRotor("Post Authors") { entries in
    // Rotor cycles through post authors
}
```

**Report format:**
```
CUSTOM ROTORS: [INFO]
- Complex list views: [count]
- With custom rotor entries: [count]
- Views that would benefit from rotors: [list]
```

### 16. Context Menu Parallel Paths

**Check:** Context menus (long-press) must NOT be the sole interaction path for actions. Users with motor impairments cannot reliably long-press. Always provide `.swipeActions` as a parallel path when using `.contextMenu`.

```swift
// BAD - Context menu is the only way to delete
ForEach(items) { item in
    ItemRow(item: item)
        .contextMenu {
            Button("Delete", role: .destructive) { delete(item) }
        }
}

// GOOD - Swipe actions as parallel path
ForEach(items) { item in
    ItemRow(item: item)
        .swipeActions(edge: .trailing) {
            Button("Delete", role: .destructive) { delete(item) }
        }
        .contextMenu {
            Button("Delete", role: .destructive) { delete(item) }
        }
}
```

**Report format:**
```
CONTEXT MENU PATHS: [PASS/WARN]
- Context menus: [count]
- With parallel swipe actions: [count]
- Context menu as sole path: [list - violations]
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

### VoiceOver Grouping
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

### Accessibility Values
[details]

### Sort Priority
[details]

### Dismiss Actions
[details]

### Live Regions
[details]

### Magic Tap
[details]

### Custom Rotors
[details]

### Context Menu Parallel Paths
[details]

### Testing Checklist
- [ ] Test with VoiceOver enabled
- [ ] Test with Reduce Transparency
- [ ] Test with Reduce Motion
- [ ] Test with Increase Contrast
- [ ] Verify all tap targets >= 44pt
- [ ] Test Assistive Access scene (iOS 26+)
- [ ] Verify VoiceOver grouping on composite views
- [ ] Check value descriptions on sliders/steppers
- [ ] Verify reading order matches logical order
- [ ] Test dismiss action on custom overlays
- [ ] Verify live regions announce updates
- [ ] Test Magic Tap on media/primary-action screens

### Recommendations
1. [ordered by severity]
2. ...
```

---

## Severity Levels

| Level | Criteria | Action |
|-------|----------|--------|
| Critical | Missing VoiceOver labels on buttons, tap targets < 44pt, custom overlay with no escape/dismiss action | Block PR |
| Warning | Missing Reduce Transparency fallback, no Assistive Access scene, context menu as sole interaction path, plain buttons without tap target frames, missing VoiceOver grouping on composite views, sliders/steppers without accessibilityValue, dynamic content without live region traits | Address before App Store |
| Info | Sort priority optimization, Magic Tap opportunities, custom rotor entries for complex lists | Optional improvement |

---

## Testing Commands

```bash
# Enable VoiceOver via Accessibility Shortcut
# Settings -> Accessibility -> Accessibility Shortcut -> VoiceOver

# Test with Accessibility Inspector
# Xcode -> Open Developer Tool -> Accessibility Inspector

# Preview with Assistive Access trait
#Preview(traits: .assistiveAccess) {
    SimplifiedView()
}
```

---

*Deeper accessibility patterns inspired by dadederk's iOS Accessibility Agent Skill.*
