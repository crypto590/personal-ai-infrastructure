# Android Accessibility Review

**Part of:** [kotlin-android](../SKILL.md) > Review

**Trigger:** Before completing any Android feature, PR review for Android UI code, mentions of accessibility or TalkBack, implementing custom controls, adding interactive elements, reviewing contrast or visibility, checking touch target sizes, implementing Switch Access support, checking system preference handling.

---

## Audit Checklist

### 1. TalkBack Support (Content Descriptions)

**Check:** All interactive elements properly labeled for TalkBack.

```kotlin
// GOOD - Explicit content description on icon button
IconButton(onClick = { addItem() }) {
    Icon(
        imageVector = Icons.Default.Add,
        contentDescription = "Add new item"
    )
}

// BAD - No content description for image-only button
IconButton(onClick = { addItem() }) {
    Icon(
        imageVector = Icons.Default.Add,
        contentDescription = null  // TalkBack: "button"
    )
}

// GOOD - Merged semantics for complex row
Row(
    modifier = Modifier.semantics(mergeDescendants = true) {}
) {
    Icon(Icons.Default.Star, contentDescription = null)
    Text("4.5")
    Text("(128 reviews)")
}
// TalkBack reads: "4.5 (128 reviews)"

// GOOD - Custom content description overrides merged children
Row(
    modifier = Modifier.semantics(mergeDescendants = true) {
        contentDescription = "Rating: 4.5 stars, 128 reviews"
    }
) {
    Icon(Icons.Default.Star, contentDescription = null)
    Text("4.5")
    Text("(128 reviews)")
}
```

**Report format:**
```
TALKBACK: [PASS/WARN/FAIL]
- Interactive elements: [count]
- With content descriptions: [count]
- Icon-only buttons without descriptions: [list]
- Complex views needing mergeDescendants: [list]
```

### 2. Minimum Touch Targets

**Check:** All interactive elements meet 48dp x 48dp minimum (Material Design requirement).

```kotlin
// GOOD - Meets minimum via default button sizing
Button(onClick = { }) {
    Text("Tap me")
}

// BAD - Too small
Box(
    modifier = Modifier
        .size(24.dp)
        .clickable { doSomething() }
)  // VIOLATION: 24dp < 48dp minimum

// GOOD - Small visual element with larger touch target
Icon(
    imageVector = Icons.Default.Info,
    contentDescription = "Information",
    modifier = Modifier
        .size(20.dp)                    // Visual size
        .clickable { showInfo() }
        .minimumInteractiveComponentSize() // Enforces 48dp touch target
)

// GOOD - Manual touch target expansion
Box(
    modifier = Modifier
        .size(24.dp)
        .clickable { doSomething() }
        .padding(12.dp)  // Expands touch target to 48dp
)
```

**Report format:**
```
TOUCH TARGETS: [PASS/FAIL]
- Interactive elements: [count]
- Below 48dp minimum: [list with sizes]
- Using minimumInteractiveComponentSize: [count]
- Recommendation: Use Modifier.minimumInteractiveComponentSize() for small elements
```

### 3. Color Contrast Ratios

**Check:** Text meets WCAG AA standards.

| Element Type | Minimum Ratio | Standard |
|---|---|---|
| Body text | 4.5:1 | WCAG AA |
| Large text (18sp+ or 14sp bold) | 3:1 | WCAG AA |
| UI components / icons | 3:1 | WCAG 2.1 |

```kotlin
// GOOD - Uses MaterialTheme color roles (system handles contrast)
Text(
    text = "Important",
    color = MaterialTheme.colorScheme.onSurface
)

// SUSPICIOUS - Hardcoded color
Text(
    text = "Warning",
    color = Color(0xFF999999)  // Check contrast ratio!
)

// GOOD - Semantic color roles for foreground/background pairing
Surface(color = MaterialTheme.colorScheme.primary) {
    Text(
        text = "Button label",
        color = MaterialTheme.colorScheme.onPrimary  // Guaranteed contrast
    )
}
```

**Report format:**
```
CONTRAST RATIOS: [PASS/WARN/FAIL]
- Text with MaterialTheme colors: [count]
- Text with hardcoded colors: [count]
- Potential contrast issues: [list with color values]
```

### 4. Semantics in Compose

**Check:** Custom semantic properties set for non-standard elements.

```kotlin
// GOOD - stateDescription for toggles
Switch(
    checked = isEnabled,
    onCheckedChange = { isEnabled = it },
    modifier = Modifier.semantics {
        stateDescription = if (isEnabled) "Enabled" else "Disabled"
    }
)

// GOOD - Custom role for non-button clickable
Box(
    modifier = Modifier
        .clickable { select() }
        .semantics {
            role = Role.RadioButton
            selected = isSelected
            contentDescription = "Option A"
        }
)

// GOOD - clearAndSetSemantics for complete control
Card(modifier = Modifier.clearAndSetSemantics {
    contentDescription = "Article: ${article.title}, by ${article.author}, ${article.readTime} min read"
    role = Role.Button
    onClick(label = "Open article") { openArticle(); true }
}) {
    ArticleContent(article)
}
```

**Report format:**
```
SEMANTICS: [PASS/WARN]
- Custom clickable elements without semantics: [count]
- Toggle elements without stateDescription: [count]
- Complex cards/rows needing clearAndSetSemantics: [list]
```

### 5. Content Grouping (mergeDescendants)

**Check:** Related elements grouped so TalkBack reads them as a single unit.

```kotlin
// BAD - TalkBack reads icon and text as separate elements (two swipes)
Row {
    Icon(Icons.Default.Schedule, contentDescription = "Time")
    Text("5 min ago")
}

// GOOD - Merged into single TalkBack element
Row(
    modifier = Modifier.semantics(mergeDescendants = true) {}
) {
    Icon(Icons.Default.Schedule, contentDescription = null)
    Text("5 min ago")
}

// GOOD - Override merged text with better description
Row(
    modifier = Modifier.semantics(mergeDescendants = true) {
        contentDescription = "Posted 5 minutes ago"
    }
) {
    Icon(Icons.Default.Schedule, contentDescription = null)
    Text("5 min ago")
}
```

**Report format:**
```
CONTENT GROUPING: [PASS/WARN]
- Composite views (icon + text rows, stat groups): [count]
- Properly merged with mergeDescendants: [count]
- Missing grouping: [list]
```

### 6. Custom Accessibility Actions

**Check:** Complex gestures have accessible alternatives for TalkBack users.

```kotlin
// GOOD - Custom actions as accessible alternative to swipe gestures
LazyColumn {
    items(items) { item ->
        ItemRow(
            item = item,
            modifier = Modifier
                .pointerInput(Unit) {
                    detectHorizontalDragGestures { _, dragAmount ->
                        if (dragAmount < -100) deleteItem(item)
                    }
                }
                .semantics {
                    customActions = listOf(
                        CustomAccessibilityAction(
                            label = "Delete ${item.name}",
                            action = { deleteItem(item); true }
                        ),
                        CustomAccessibilityAction(
                            label = "Archive ${item.name}",
                            action = { archiveItem(item); true }
                        )
                    )
                }
        )
    }
}
```

**Report format:**
```
CUSTOM ACTIONS: [PASS/WARN]
- Custom gestures (swipe, drag, long-press): [count]
- With accessible custom actions: [count]
- Missing accessible alternatives: [list]
```

### 7. State Descriptions for Toggles

**Check:** Switches, checkboxes, and toggle buttons describe their current state.

```kotlin
// BAD - TalkBack only says "Switch, on" with no context
Switch(checked = notificationsEnabled, onCheckedChange = { notificationsEnabled = it })

// GOOD - Descriptive state for context
Switch(
    checked = notificationsEnabled,
    onCheckedChange = { notificationsEnabled = it },
    modifier = Modifier.semantics {
        stateDescription = if (notificationsEnabled) "Notifications on" else "Notifications off"
        contentDescription = "Push notifications"
    }
)

// GOOD - Checkbox with state
Checkbox(
    checked = isSelected,
    onCheckedChange = { isSelected = it },
    modifier = Modifier.semantics {
        stateDescription = if (isSelected) "Selected" else "Not selected"
    }
)
```

**Report format:**
```
STATE DESCRIPTIONS: [PASS/WARN]
- Toggle elements (Switch, Checkbox, RadioButton): [count]
- With explicit stateDescription: [count]
- Missing state descriptions: [list]
```

### 8. Live Regions for Dynamic Content

**Check:** Content that updates dynamically announces changes to TalkBack.

```kotlin
// BAD - Score updates silently, TalkBack users miss changes
Text(text = "$homeScore - $awayScore")

// GOOD - TalkBack announces updates
Text(
    text = "$homeScore - $awayScore",
    modifier = Modifier.semantics {
        liveRegion = LiveRegionMode.Polite  // Announces when content changes
        contentDescription = "Score: $homeTeam $homeScore, $awayTeam $awayScore"
    }
)

// GOOD - Assertive for important updates (interrupts current reading)
Text(
    text = errorMessage,
    modifier = Modifier.semantics {
        liveRegion = LiveRegionMode.Assertive
    }
)
```

**Report format:**
```
LIVE REGIONS: [PASS/WARN]
- Dynamic content (scores, timers, status indicators): [count]
- With liveRegion semantics: [count]
- Missing live region markup: [list]
```

### 9. Heading Hierarchy

**Check:** Screens use semantic headings for TalkBack navigation.

```kotlin
// GOOD - Section headings for TalkBack heading navigation
Text(
    text = "Recent Activity",
    style = MaterialTheme.typography.titleLarge,
    modifier = Modifier.semantics { heading() }
)

// GOOD - Screen title
Text(
    text = "Settings",
    style = MaterialTheme.typography.headlineMedium,
    modifier = Modifier.semantics { heading() }
)
```

**Report format:**
```
HEADING HIERARCHY: [PASS/WARN]
- Logical section headings in UI: [count]
- Marked with heading() semantics: [count]
- Headings missing semantic markup: [list]
```

### 10. Switch Access Support

**Check:** All actions are reachable via directional navigation (keyboard/Switch Access).

```kotlin
// GOOD - focusable elements in logical order
Column {
    TextField(
        value = username,
        onValueChange = { username = it },
        label = { Text("Username") },
        keyboardOptions = KeyboardOptions(imeAction = ImeAction.Next),
        keyboardActions = KeyboardActions(onNext = { focusManager.moveFocus(FocusDirection.Down) })
    )
    TextField(
        value = password,
        onValueChange = { password = it },
        label = { Text("Password") },
        keyboardOptions = KeyboardOptions(imeAction = ImeAction.Done),
        keyboardActions = KeyboardActions(onDone = { login() })
    )
}

// BAD - Non-interactive element consuming focus
Box(
    modifier = Modifier
        .focusable()  // Decoration elements should not be focusable
        .background(Color.Gray)
) {
    // Visual decoration only
}
```

**Report format:**
```
SWITCH ACCESS: [PASS/WARN]
- Focus order issues detected: [list]
- Non-interactive elements consuming focus: [list]
- Keyboard action chaining (Next/Done): [present/missing]
```

### 11. Reduce Motion Support

**Check:** Animations respect the system reduce motion preference.

```kotlin
// GOOD - Check reduce motion preference
@Composable
fun AnimatedContent(visible: Boolean) {
    val reduceMotion = LocalAccessibilityManager.current?.isEnabled == true
    // Note: Use the system WindowManager accessibility flag

    AnimatedVisibility(
        visible = visible,
        enter = if (reduceMotion) EnterTransition.None else fadeIn() + slideInVertically(),
        exit = if (reduceMotion) ExitTransition.None else fadeOut() + slideOutVertically()
    )
}

// GOOD - Compose animation with reduced motion awareness
val transition = updateTransition(targetState = visible, label = "visibility")
val alpha by transition.animateFloat(
    transitionSpec = {
        if (/* reduceMotion */ false) snap() else tween(300)
    },
    label = "alpha"
) { state -> if (state) 1f else 0f }
```

**Report format:**
```
REDUCE MOTION: [PASS/WARN]
- Animated transitions: [count]
- Respecting reduce motion preference: [count]
- Animations ignoring preference: [list]
```

### 12. High Contrast / Font Scaling

**Check:** UI adapts to system font scale and high contrast settings.

```kotlin
// GOOD - Uses sp units (respects font scale)
Text(
    text = "Body text",
    style = MaterialTheme.typography.bodyMedium  // Uses sp internally
)

// BAD - Fixed pixel size ignores accessibility text size
Text(
    text = "Body text",
    fontSize = 16.dp.value.sp  // Convert from dp is wrong pattern
)

// GOOD - Layout expands for large text
LazyColumn {
    items(items) { item ->
        ListItem(
            headlineContent = { Text(item.title) },
            supportingContent = { Text(item.subtitle) },
            // ListItem automatically handles text overflow
        )
    }
}

// BAD - Fixed height clips large text
Box(modifier = Modifier.height(48.dp)) {
    Text(text = longText)  // Will clip at large font sizes
}
```

**Report format:**
```
FONT SCALING: [PASS/WARN]
- Text using sp units (via MaterialTheme.typography): [count]
- Hardcoded pixel text sizes: [list]
- Fixed-height containers with text: [list]
```

### 13. RTL Layout Support

**Check:** Layouts mirror correctly in right-to-left languages.

```kotlin
// GOOD - Uses start/end (mirrors in RTL)
Row {
    Icon(
        imageVector = Icons.AutoMirrored.Default.ArrowForward,
        contentDescription = null,
        modifier = Modifier.padding(start = 8.dp)
    )
    Text(
        text = "Navigate",
        modifier = Modifier.padding(end = 8.dp)
    )
}

// BAD - Uses left/right (does NOT mirror in RTL)
Row {
    Icon(
        imageVector = Icons.Default.ArrowForward,  // Does not auto-mirror
        contentDescription = null,
        modifier = Modifier.padding(left = 8.dp)  // VIOLATION: use start
    )
}

// GOOD - LayoutDirection awareness for custom drawing
Canvas(modifier = Modifier.fillMaxSize()) {
    val isRtl = layoutDirection == LayoutDirection.Rtl
    val x = if (isRtl) size.width - 20.dp.toPx() else 20.dp.toPx()
    drawCircle(color = Color.Blue, center = Offset(x, size.height / 2))
}
```

**Report format:**
```
RTL SUPPORT: [PASS/WARN]
- Padding using left/right (should use start/end): [list]
- Icons that need AutoMirrored variant: [list]
- Custom drawing without LayoutDirection handling: [list]
```

---

## Audit Output Format

```markdown
## Android Accessibility Audit: [Feature/File Name]

### Summary
- Overall: [PASS/NEEDS WORK/FAIL]
- Issues found: [count]
- Critical (blocks users): [count]

### TalkBack Support
[details]

### Content Grouping
[details]

### Touch Targets
[details]

### Semantics
[details]

### State Descriptions
[details]

### Custom Actions
[details]

### Live Regions
[details]

### Heading Hierarchy
[details]

### Switch Access
[details]

### Reduce Motion
[details]

### Font Scaling
[details]

### RTL Support
[details]

### Contrast Ratios
[details]

### Testing Checklist
- [ ] Test with TalkBack enabled
- [ ] Test with Switch Access
- [ ] Verify all touch targets >= 48dp
- [ ] Test with largest system font size
- [ ] Test in RTL layout (Developer Options → Force RTL)
- [ ] Test with high contrast text enabled
- [ ] Verify TalkBack grouping on composite views
- [ ] Check state descriptions on toggles
- [ ] Verify live regions announce updates
- [ ] Test custom gestures have accessible alternatives

### Recommendations
1. [ordered by severity]
2. ...
```

---

## Severity Levels

| Level | Criteria | Action |
|---|---|---|
| Critical | Missing TalkBack labels on interactive elements, touch targets < 48dp, custom gestures with no accessible alternative | Block PR |
| Warning | Missing stateDescription on toggles, missing content grouping on composite views, hardcoded left/right padding, no live region on dynamic content, missing heading semantics | Address before shipping |
| Info | Custom actions optimization, heading hierarchy improvements, reduce motion enhancements | Optional improvement |

---

## Testing Commands

```bash
# Enable TalkBack via Developer Options or Accessibility settings
# Settings -> Accessibility -> TalkBack -> Use TalkBack

# Enable Switch Access
# Settings -> Accessibility -> Switch Access

# Force RTL layout (Developer Options)
# Settings -> Developer Options -> Force RTL layout direction

# Run Android Lint accessibility checks
./gradlew lint
# Look for: ContentDescription, TouchTargetSizeCheck, TextContrastCheck

# Run accessibility checks programmatically with Espresso
// In instrumented tests:
AccessibilityChecks.enable().setRunChecksFromRootView(true)
```
