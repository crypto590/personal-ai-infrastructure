# Material Design 3 Compliance Review

**Part of:** [kotlin-android](../SKILL.md) > Review

**Trigger:** Before completing any Android UI feature, PR review for Compose UI code, implementing new screens or components, checking for hardcoded colors, reviewing typography or spacing, implementing dark mode or dynamic color, checking icon usage or elevation patterns.

---

## Audit Checklist

### 1. Component Usage Appropriateness

**Check:** Correct Material3 components used for each UI pattern.

```kotlin
// GOOD - Material3 components
import androidx.compose.material3.*

Button(onClick = { }) { Text("Primary Action") }
OutlinedButton(onClick = { }) { Text("Secondary Action") }
TextButton(onClick = { }) { Text("Tertiary Action") }
FilledTonalButton(onClick = { }) { Text("Tonal Action") }
ElevatedButton(onClick = { }) { Text("Elevated") }

// FAB variants
FloatingActionButton(onClick = { }) { Icon(Icons.Default.Add, "Add") }
SmallFloatingActionButton(onClick = { }) { Icon(Icons.Default.Add, "Add") }
LargeFloatingActionButton(onClick = { }) { Icon(Icons.Default.Add, "Add") }
ExtendedFloatingActionButton(
    text = { Text("New Item") },
    icon = { Icon(Icons.Default.Add, null) },
    onClick = { }
)

// VIOLATION - Custom button instead of Material3 component
Box(
    modifier = Modifier
        .background(Color.Blue, RoundedCornerShape(8.dp))
        .clickable { }
        .padding(16.dp)
) {
    Text("Custom Button", color = Color.White)  // VIOLATION: use Button()
}
```

**Component Selection Guide:**

| Pattern | Correct Component |
|---|---|
| Primary action | `Button` |
| Secondary action | `OutlinedButton` |
| Subtle action | `TextButton` |
| List items | `ListItem` |
| Chips/filters | `FilterChip`, `AssistChip`, `InputChip`, `SuggestionChip` |
| Cards | `Card`, `ElevatedCard`, `OutlinedCard`, `FilledCard` |
| Top app bar | `TopAppBar`, `CenterAlignedTopAppBar`, `MediumTopAppBar`, `LargeTopAppBar` |
| Navigation | `NavigationBar`, `NavigationRail`, `NavigationDrawer` |
| Search | `SearchBar`, `DockedSearchBar` |
| Dialogs | `AlertDialog`, `BasicAlertDialog` |
| Bottom sheets | `ModalBottomSheet`, `BottomSheetScaffold` |
| Sliders | `Slider`, `RangeSlider` |
| Progress | `LinearProgressIndicator`, `CircularProgressIndicator` |
| Dividers | `HorizontalDivider`, `VerticalDivider` |

**Report format:**
```
COMPONENT USAGE: [PASS/WARN]
- Custom components replacing M3 equivalents: [list]
- Correct M3 components used: [count]
- Violations: [list with suggested replacements]
```

### 2. Color Role Usage

**Check:** All colors reference `MaterialTheme.colorScheme`, never hardcoded.

```kotlin
// GOOD - Semantic color roles
Text(
    text = "Primary content",
    color = MaterialTheme.colorScheme.onSurface
)
Surface(color = MaterialTheme.colorScheme.surfaceVariant) {
    Text(
        text = "Secondary content",
        color = MaterialTheme.colorScheme.onSurfaceVariant
    )
}

// GOOD - Error state using error color role
Text(
    text = errorMessage,
    color = MaterialTheme.colorScheme.error
)

// VIOLATION - Hardcoded color
Text(
    text = "Label",
    color = Color(0xFF1A73E8)  // VIOLATION: hardcoded blue
)
Text(
    text = "Error",
    color = Color.Red  // VIOLATION: hardcoded
)

// VIOLATION - Non-semantic Color object
Card(containerColor = Color.White)  // VIOLATION: does not adapt to dark mode
```

**Color Role Reference:**

| Role | Light | Dark | Usage |
|---|---|---|---|
| `primary` | Brand color | Brand color | Key components, FABs |
| `onPrimary` | White | Dark | Text/icons on primary |
| `primaryContainer` | Light brand | Dark brand | Filled buttons, selected chips |
| `onPrimaryContainer` | Dark brand | Light brand | Text on primaryContainer |
| `surface` | White | Dark gray | Cards, sheets, dialogs |
| `onSurface` | Near black | White | Text on surfaces |
| `surfaceVariant` | Light gray | Dark gray | Input fields, disabled surfaces |
| `onSurfaceVariant` | Gray | Light gray | Placeholder text, icons |
| `error` | Red | Light red | Error states |
| `onError` | White | Dark | Text on error |

**Report format:**
```
COLOR ROLES: [PASS/FAIL]
- MaterialTheme.colorScheme usage: [count]
- Hardcoded Color values: [list - violations]
- Non-adaptive Color.White/Color.Black: [list - violations]
```

### 3. Typography Compliance

**Check:** All text uses `MaterialTheme.typography` text styles.

```kotlin
// GOOD - Material3 typography scale
Text(text = "Display", style = MaterialTheme.typography.displayLarge)
Text(text = "Headline", style = MaterialTheme.typography.headlineMedium)
Text(text = "Title", style = MaterialTheme.typography.titleLarge)
Text(text = "Body", style = MaterialTheme.typography.bodyMedium)
Text(text = "Label", style = MaterialTheme.typography.labelSmall)

// VIOLATION - Hardcoded font size
Text(text = "Label", fontSize = 14.sp)  // VIOLATION: use MaterialTheme.typography

// VIOLATION - Non-adaptive fontWeight
Text(text = "Bold Label", fontWeight = FontWeight.Bold)  // WARNING: prefer typography role

// GOOD - Custom typography via MaterialTheme
@Composable
fun AppTypography() = Typography(
    bodyLarge = TextStyle(
        fontFamily = AppFontFamily,
        fontWeight = FontWeight.Normal,
        fontSize = 16.sp
    )
)
MaterialTheme(typography = AppTypography()) { /* content */ }
```

**Typography Scale Reference:**

| Role | Size | Weight | Usage |
|---|---|---|---|
| `displayLarge` | 57sp | Regular | Hero text |
| `headlineLarge` | 32sp | Regular | Screen titles |
| `headlineMedium` | 28sp | Regular | Section headers |
| `titleLarge` | 22sp | Regular | App bar titles |
| `titleMedium` | 16sp | Medium | Card titles |
| `bodyLarge` | 16sp | Regular | Primary body |
| `bodyMedium` | 14sp | Regular | Secondary body |
| `labelLarge` | 14sp | Medium | Button labels |
| `labelSmall` | 11sp | Medium | Captions |

**Report format:**
```
TYPOGRAPHY: [PASS/WARN]
- MaterialTheme.typography usage: [count]
- Hardcoded fontSize values: [list - violations]
- Hardcoded fontWeight without typography role: [list - warnings]
```

### 4. Shape System Usage

**Check:** Shapes reference `MaterialTheme.shapes`, not hardcoded corner radii.

```kotlin
// GOOD - Material3 shape tokens
Card(shape = MaterialTheme.shapes.medium) { /* content */ }
Button(shape = MaterialTheme.shapes.full) { Text("Pill button") }
Surface(shape = MaterialTheme.shapes.large) { /* content */ }

// VIOLATION - Hardcoded corner radius
Card(shape = RoundedCornerShape(8.dp)) {  // VIOLATION: use MaterialTheme.shapes
    /* content */
}

// GOOD - Custom shape scale via MaterialTheme
MaterialTheme(
    shapes = Shapes(
        small = RoundedCornerShape(4.dp),
        medium = RoundedCornerShape(8.dp),
        large = RoundedCornerShape(16.dp)
    )
) { /* content */ }
```

**Report format:**
```
SHAPE SYSTEM: [PASS/WARN]
- MaterialTheme.shapes usage: [count]
- Hardcoded RoundedCornerShape values: [list - warnings]
```

### 5. Dynamic Color Support (Android 12+)

**Check:** Dynamic color (Monet) enabled for Android 12+ with proper fallback.

```kotlin
// GOOD - Dynamic color with fallback
@Composable
fun AppTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    dynamicColor: Boolean = true,
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
        }
        darkTheme -> DarkColorScheme
        else -> LightColorScheme
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = AppTypography,
        content = content
    )
}

// VIOLATION - No dynamic color support
@Composable
fun AppTheme(darkTheme: Boolean, content: @Composable () -> Unit) {
    val colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme  // VIOLATION: no dynamic
    MaterialTheme(colorScheme = colorScheme, content = content)
}
```

**Report format:**
```
DYNAMIC COLOR: [PASS/WARN]
- dynamicColorScheme support: [present/missing]
- API 31 build version check: [present/missing]
- Fallback color scheme: [present/missing]
```

### 6. Dark Mode Support

**Check:** All colors and surfaces adapt correctly to dark mode.

```kotlin
// GOOD - Adaptive via MaterialTheme
Surface(
    color = MaterialTheme.colorScheme.surface,
    contentColor = MaterialTheme.colorScheme.onSurface
) {
    Text("Adapts to dark mode automatically")
}

// VIOLATION - Fixed white background
Box(modifier = Modifier.background(Color.White)) {  // VIOLATION: invisible in dark mode
    Text("Label", color = Color.Black)
}

// GOOD - Preview in both themes
@Preview(name = "Light")
@Preview(name = "Dark", uiMode = Configuration.UI_MODE_NIGHT_YES)
@Composable
fun PreviewScreen() {
    AppTheme {
        MyScreen()
    }
}
```

**Report format:**
```
DARK MODE: [PASS/FAIL]
- Hardcoded backgrounds ignoring dark mode: [list - violations]
- Adaptive color role usage: [count]
- @Preview with both light/dark variants: [count/total screens]
```

### 7. Elevation and Surface Tones

**Check:** Material3 uses surface tones (not shadows) for elevation hierarchy.

```kotlin
// GOOD - Surface with elevation (M3 tones the surface color)
Surface(
    tonalElevation = 2.dp,
    shadowElevation = 0.dp  // M3 prefers tonal elevation over shadow
) {
    /* content */
}

// GOOD - Card elevation
ElevatedCard(
    elevation = CardDefaults.elevatedCardElevation(defaultElevation = 6.dp)
) {
    /* content */
}

// WARNING - High shadow elevation (M3 uses tonal elevation)
Surface(shadowElevation = 16.dp) {  // WARNING: prefer tonalElevation in M3
    /* content */
}
```

**Report format:**
```
ELEVATION: [PASS/WARN]
- tonalElevation usage: [count]
- shadowElevation > 4dp (M3 discourages): [list - warnings]
- Surface.tonalElevation for hierarchy: [present/missing]
```

### 8. Icon Usage

**Check:** Material Icons used correctly, outlined vs filled convention followed.

```kotlin
// GOOD - Outlined icons for unselected, filled for selected
@Composable
fun NavItem(selected: Boolean, label: String, icon: ImageVector, filledIcon: ImageVector) {
    NavigationBarItem(
        selected = selected,
        onClick = { },
        icon = {
            Icon(
                imageVector = if (selected) filledIcon else icon,
                contentDescription = label
            )
        },
        label = { Text(label) }
    )
}

// Usage
NavItem(
    selected = currentRoute == "home",
    label = "Home",
    icon = Icons.Outlined.Home,
    filledIcon = Icons.Filled.Home
)

// VIOLATION - Filled icon for unselected state
NavigationBarItem(
    selected = false,
    icon = { Icon(Icons.Filled.Home, "Home") }  // WARNING: use Outlined when not selected
)
```

**Report format:**
```
ICON USAGE: [PASS/WARN]
- Outlined/filled selection pattern: [followed/violations list]
- contentDescription on all icons: [count/total]
- Icons.AutoMirrored for RTL icons: [count]
```

### 9. Spacing and Padding Consistency

**Check:** Spacing follows Material3 baseline grid (4dp multiples).

```kotlin
// GOOD - 4dp baseline grid multiples
Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {  // 2 * 4dp
    Text("Title", modifier = Modifier.padding(horizontal = 16.dp))  // 4 * 4dp
    Text("Body", modifier = Modifier.padding(horizontal = 16.dp, vertical = 12.dp))
}

// WARNING - Non-grid-aligned spacing
Text(
    modifier = Modifier.padding(horizontal = 13.dp)  // WARNING: not a 4dp multiple
)

// GOOD - ListItem for consistent list padding
LazyColumn {
    items(items) { item ->
        ListItem(
            headlineContent = { Text(item.title) },
            supportingContent = { Text(item.subtitle) },
            leadingContent = { Icon(item.icon, null) }
        )
    }
}
```

**Report format:**
```
SPACING: [PASS/WARN]
- Non-4dp-multiple padding values: [list - warnings]
- ListItem for standard list rows: [count/total lists]
- Consistent spacing in Column/Row Arrangement: [count]
```

---

## Audit Output Format

```markdown
## Material Design 3 Compliance Audit: [Feature/File Name]

### Summary
- Overall: [PASS/NEEDS WORK/FAIL]
- Issues found: [count]
- Critical (hardcoded colors breaking dark mode): [count]

### Component Usage
[details]

### Color Roles
[details]

### Typography
[details]

### Shape System
[details]

### Dynamic Color
[details]

### Dark Mode
[details]

### Elevation
[details]

### Icon Usage
[details]

### Spacing
[details]

### Recommendations
1. [ordered by severity]
2. ...
```

---

## Severity Levels

| Level | Criteria | Action |
|---|---|---|
| Critical | Hardcoded `Color.White`/`Color.Black` breaking dark mode, custom Box/Modifier replacing M3 components for primary actions | Block PR |
| Warning | Hardcoded `fontSize`/`fontWeight` instead of typography roles, `RoundedCornerShape` instead of `MaterialTheme.shapes`, missing dynamic color support, filled icons for unselected nav items | Address before shipping |
| Info | Non-4dp-multiple spacing, missing light/dark preview variants, shadow elevation over tonal | Optional improvement |
