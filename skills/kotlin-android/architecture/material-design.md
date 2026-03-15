# Material Design 3

**Part of:** [kotlin-android](../SKILL.md) > Architecture

**Related:**
- [examples.md](examples.md) - Components used in complete feature examples
- [quick-reference.md](quick-reference.md) - Component cheat sheet

---

## Overview

**Material Design 3** (Material You) is Android's modern design system. It emphasizes personalized dynamic color, expressive typography, and adaptive layouts across phones, tablets, and foldables. All components come from `androidx.compose.material3`.

**Key pillars:**
- Dynamic color generated from wallpaper (Android 12+)
- Semantic color roles (primary, secondary, tertiary, surface variants)
- Adaptive layouts for multiple screen sizes
- Accessible, expressive components

---

## App-Level Theme Setup

```kotlin
// ui/theme/Theme.kt
import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.platform.LocalContext

@Composable
fun AppTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    dynamicColor: Boolean = true,
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context)
            else dynamicLightColorScheme(context)
        }
        darkTheme -> darkColorScheme()
        else -> lightColorScheme()
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = AppTypography,
        shapes = AppShapes,
        content = content
    )
}
```

---

## Custom Color Scheme

```kotlin
// ui/theme/Color.kt
import androidx.compose.ui.graphics.Color

// Brand colors
val BrandPrimary = Color(0xFF1A73E8)
val BrandOnPrimary = Color(0xFFFFFFFF)
val BrandPrimaryContainer = Color(0xFFD3E3FD)
val BrandOnPrimaryContainer = Color(0xFF001B3E)

// Custom schemes
private val LightColorScheme = lightColorScheme(
    primary = BrandPrimary,
    onPrimary = BrandOnPrimary,
    primaryContainer = BrandPrimaryContainer,
    onPrimaryContainer = BrandOnPrimaryContainer,
    secondary = Color(0xFF535F70),
    onSecondary = Color(0xFFFFFFFF),
    secondaryContainer = Color(0xFFD7E3F7),
    onSecondaryContainer = Color(0xFF101C2B),
    surface = Color(0xFFF8F9FF),
    onSurface = Color(0xFF191C20),
    surfaceVariant = Color(0xFFDFE2EB),
    onSurfaceVariant = Color(0xFF43474E),
    error = Color(0xFFBA1A1A),
    onError = Color(0xFFFFFFFF)
)

private val DarkColorScheme = darkColorScheme(
    primary = Color(0xFFA2C4FF),
    onPrimary = Color(0xFF003063),
    primaryContainer = Color(0xFF00468C),
    onPrimaryContainer = Color(0xFFD3E3FD),
    secondary = Color(0xFFBAC8DB),
    onSecondary = Color(0xFF253140),
    surface = Color(0xFF111318),
    onSurface = Color(0xFFE2E2E9),
    surfaceVariant = Color(0xFF43474E),
    onSurfaceVariant = Color(0xFFC3C7CF),
    error = Color(0xFFFFB4AB),
    onError = Color(0xFF690005)
)

@Composable
fun AppTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    dynamicColor: Boolean = true,
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            if (darkTheme) dynamicDarkColorScheme(LocalContext.current)
            else dynamicLightColorScheme(LocalContext.current)
        }
        darkTheme -> DarkColorScheme
        else -> LightColorScheme
    }

    MaterialTheme(colorScheme = colorScheme, typography = AppTypography, content = content)
}
```

---

## Typography System

```kotlin
// ui/theme/Type.kt
import androidx.compose.material3.Typography
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.Font
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp

val Inter = FontFamily(
    Font(R.font.inter_regular, FontWeight.Normal),
    Font(R.font.inter_medium, FontWeight.Medium),
    Font(R.font.inter_semibold, FontWeight.SemiBold),
    Font(R.font.inter_bold, FontWeight.Bold)
)

val AppTypography = Typography(
    displayLarge = TextStyle(fontFamily = Inter, fontWeight = FontWeight.Normal, fontSize = 57.sp),
    displayMedium = TextStyle(fontFamily = Inter, fontWeight = FontWeight.Normal, fontSize = 45.sp),
    displaySmall = TextStyle(fontFamily = Inter, fontWeight = FontWeight.Normal, fontSize = 36.sp),
    headlineLarge = TextStyle(fontFamily = Inter, fontWeight = FontWeight.SemiBold, fontSize = 32.sp),
    headlineMedium = TextStyle(fontFamily = Inter, fontWeight = FontWeight.SemiBold, fontSize = 28.sp),
    headlineSmall = TextStyle(fontFamily = Inter, fontWeight = FontWeight.SemiBold, fontSize = 24.sp),
    titleLarge = TextStyle(fontFamily = Inter, fontWeight = FontWeight.SemiBold, fontSize = 22.sp),
    titleMedium = TextStyle(fontFamily = Inter, fontWeight = FontWeight.Medium, fontSize = 16.sp),
    titleSmall = TextStyle(fontFamily = Inter, fontWeight = FontWeight.Medium, fontSize = 14.sp),
    bodyLarge = TextStyle(fontFamily = Inter, fontWeight = FontWeight.Normal, fontSize = 16.sp),
    bodyMedium = TextStyle(fontFamily = Inter, fontWeight = FontWeight.Normal, fontSize = 14.sp),
    bodySmall = TextStyle(fontFamily = Inter, fontWeight = FontWeight.Normal, fontSize = 12.sp),
    labelLarge = TextStyle(fontFamily = Inter, fontWeight = FontWeight.Medium, fontSize = 14.sp),
    labelMedium = TextStyle(fontFamily = Inter, fontWeight = FontWeight.Medium, fontSize = 12.sp),
    labelSmall = TextStyle(fontFamily = Inter, fontWeight = FontWeight.Medium, fontSize = 11.sp)
)

// Typography usage
Text("Title", style = MaterialTheme.typography.titleLarge)
Text("Body text", style = MaterialTheme.typography.bodyMedium)
Text("Caption", style = MaterialTheme.typography.labelSmall)
```

---

## Shape System

```kotlin
// ui/theme/Shape.kt
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Shapes
import androidx.compose.ui.unit.dp

val AppShapes = Shapes(
    extraSmall = RoundedCornerShape(4.dp),
    small = RoundedCornerShape(8.dp),
    medium = RoundedCornerShape(12.dp),
    large = RoundedCornerShape(16.dp),
    extraLarge = RoundedCornerShape(28.dp)
)

// Usage via MaterialTheme.shapes
Box(
    modifier = Modifier
        .clip(MaterialTheme.shapes.medium)
        .background(MaterialTheme.colorScheme.surfaceVariant)
)

Card(shape = MaterialTheme.shapes.large) { /* ... */ }
```

---

## Component Catalog

### Buttons

```kotlin
// Filled (primary action)
Button(onClick = { }) {
    Text("Primary")
}

// Filled Tonal (secondary action, less emphasis)
FilledTonalButton(onClick = { }) {
    Text("Secondary")
}

// Outlined (medium emphasis)
OutlinedButton(onClick = { }) {
    Text("Cancel")
}

// Text (lowest emphasis)
TextButton(onClick = { }) {
    Text("Learn More")
}

// Elevated (for use over surfaces)
ElevatedButton(onClick = { }) {
    Text("Elevated")
}

// With icon
Button(onClick = { }) {
    Icon(Icons.Default.Add, contentDescription = null, modifier = Modifier.size(18.dp))
    Spacer(Modifier.width(8.dp))
    Text("Add Item")
}

// Loading state
Button(
    onClick = { },
    enabled = !isLoading
) {
    if (isLoading) {
        CircularProgressIndicator(
            modifier = Modifier.size(18.dp),
            color = MaterialTheme.colorScheme.onPrimary,
            strokeWidth = 2.dp
        )
    } else {
        Text("Submit")
    }
}
```

### Cards

```kotlin
// Filled card
Card(modifier = Modifier.fillMaxWidth()) {
    Column(modifier = Modifier.padding(16.dp)) {
        Text("Card Title", style = MaterialTheme.typography.titleMedium)
        Text("Card description", style = MaterialTheme.typography.bodyMedium)
    }
}

// Outlined card
OutlinedCard(modifier = Modifier.fillMaxWidth()) {
    Column(modifier = Modifier.padding(16.dp)) {
        Text("Outlined Card")
    }
}

// Elevated card
ElevatedCard(modifier = Modifier.fillMaxWidth()) {
    Column(modifier = Modifier.padding(16.dp)) {
        Text("Elevated Card")
    }
}

// Clickable card
Card(
    onClick = { /* navigate */ },
    modifier = Modifier.fillMaxWidth()
) {
    Row(modifier = Modifier.padding(16.dp), verticalAlignment = Alignment.CenterVertically) {
        Icon(Icons.Default.Person, contentDescription = null)
        Spacer(Modifier.width(16.dp))
        Text("Alice Johnson")
    }
}
```

### Top App Bar

```kotlin
// Standard (stays same size)
TopAppBar(
    title = { Text("Screen Title") },
    navigationIcon = {
        IconButton(onClick = onBack) {
            Icon(Icons.Default.ArrowBack, "Back")
        }
    },
    actions = {
        IconButton(onClick = { }) {
            Icon(Icons.Default.MoreVert, "More")
        }
    }
)

// Large (collapses on scroll)
LargeTopAppBar(
    title = { Text("Home Feed") },
    scrollBehavior = TopAppBarDefaults.exitUntilCollapsedScrollBehavior(rememberTopAppBarState()),
    colors = TopAppBarDefaults.largeTopAppBarColors(
        containerColor = MaterialTheme.colorScheme.surface
    )
)

// Connected scroll behavior
val scrollBehavior = TopAppBarDefaults.enterAlwaysScrollBehavior()

Scaffold(
    modifier = Modifier.nestedScroll(scrollBehavior.nestedScrollConnection),
    topBar = {
        TopAppBar(title = { Text("Title") }, scrollBehavior = scrollBehavior)
    }
) { /* content */ }
```

### Navigation Bar (Bottom Navigation)

```kotlin
val items = listOf(
    NavItem("Home", Icons.Default.Home, Icons.Outlined.Home),
    NavItem("Search", Icons.Default.Search, Icons.Outlined.Search),
    NavItem("Profile", Icons.Default.Person, Icons.Outlined.Person)
)

var selectedIndex by remember { mutableIntStateOf(0) }

NavigationBar {
    items.forEachIndexed { index, item ->
        NavigationBarItem(
            selected = selectedIndex == index,
            onClick = { selectedIndex = index },
            icon = {
                Icon(
                    imageVector = if (selectedIndex == index) item.selectedIcon else item.icon,
                    contentDescription = item.label
                )
            },
            label = { Text(item.label) }
        )
    }
}
```

### Navigation Rail (Tablets)

```kotlin
NavigationRail {
    items.forEachIndexed { index, item ->
        NavigationRailItem(
            selected = selectedIndex == index,
            onClick = { selectedIndex = index },
            icon = { Icon(item.icon, item.label) },
            label = { Text(item.label) }
        )
    }
}
```

### Floating Action Button

```kotlin
// Standard FAB
FloatingActionButton(onClick = { }) {
    Icon(Icons.Default.Add, contentDescription = "Add")
}

// Extended FAB (with label)
ExtendedFloatingActionButton(
    onClick = { },
    icon = { Icon(Icons.Default.Edit, contentDescription = null) },
    text = { Text("New Post") },
    expanded = listState.isScrollingUp() // collapse on scroll
)

// Small FAB
SmallFloatingActionButton(onClick = { }) {
    Icon(Icons.Default.Add, "Add")
}

// Large FAB
LargeFloatingActionButton(onClick = { }) {
    Icon(Icons.Default.Add, "Add", modifier = Modifier.size(36.dp))
}
```

### TextField

```kotlin
// Filled (default)
var text by remember { mutableStateOf("") }

OutlinedTextField(
    value = text,
    onValueChange = { text = it },
    label = { Text("Email") },
    placeholder = { Text("user@example.com") },
    leadingIcon = { Icon(Icons.Default.Email, null) },
    trailingIcon = {
        if (text.isNotEmpty()) {
            IconButton(onClick = { text = "" }) {
                Icon(Icons.Default.Clear, "Clear")
            }
        }
    },
    isError = text.isNotEmpty() && !text.contains("@"),
    supportingText = {
        if (text.isNotEmpty() && !text.contains("@")) {
            Text("Invalid email address", color = MaterialTheme.colorScheme.error)
        }
    },
    singleLine = true,
    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Email),
    modifier = Modifier.fillMaxWidth()
)
```

### Chips

```kotlin
// Filter chip
var selected by remember { mutableStateOf(false) }

FilterChip(
    selected = selected,
    onClick = { selected = !selected },
    label = { Text("Kotlin") },
    leadingIcon = if (selected) {
        { Icon(Icons.Default.Check, null, modifier = Modifier.size(18.dp)) }
    } else null
)

// Input chip (removable)
InputChip(
    selected = false,
    onClick = { /* remove */ },
    label = { Text("android") },
    trailingIcon = {
        Icon(Icons.Default.Close, "Remove", modifier = Modifier.size(16.dp))
    }
)

// Suggestion chip
SuggestionChip(
    onClick = { /* apply suggestion */ },
    label = { Text("Kotlin") }
)

// Assist chip
AssistChip(
    onClick = { },
    label = { Text("Open in Maps") },
    leadingIcon = { Icon(Icons.Default.Map, null, modifier = Modifier.size(18.dp)) }
)
```

### Dialog

```kotlin
if (showDialog) {
    AlertDialog(
        onDismissRequest = { showDialog = false },
        icon = { Icon(Icons.Default.Warning, null) },
        title = { Text("Delete Post?") },
        text = { Text("This action cannot be undone. The post will be permanently deleted.") },
        confirmButton = {
            Button(
                onClick = {
                    onConfirmDelete()
                    showDialog = false
                },
                colors = ButtonDefaults.buttonColors(
                    containerColor = MaterialTheme.colorScheme.error
                )
            ) {
                Text("Delete")
            }
        },
        dismissButton = {
            TextButton(onClick = { showDialog = false }) {
                Text("Cancel")
            }
        }
    )
}
```

### Bottom Sheet

```kotlin
val sheetState = rememberModalBottomSheetState()

if (showSheet) {
    ModalBottomSheet(
        onDismissRequest = { showSheet = false },
        sheetState = sheetState
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 24.dp)
                .padding(bottom = 32.dp)
        ) {
            Text("Options", style = MaterialTheme.typography.titleLarge)
            Spacer(Modifier.height(16.dp))

            ListItem(
                headlineContent = { Text("Share") },
                leadingContent = { Icon(Icons.Default.Share, null) },
                modifier = Modifier.clickable { }
            )
            ListItem(
                headlineContent = { Text("Edit") },
                leadingContent = { Icon(Icons.Default.Edit, null) },
                modifier = Modifier.clickable { }
            )
            ListItem(
                headlineContent = { Text("Delete") },
                leadingContent = {
                    Icon(Icons.Default.Delete, null, tint = MaterialTheme.colorScheme.error)
                },
                headlineColor = MaterialTheme.colorScheme.error,
                modifier = Modifier.clickable { }
            )
        }
    }
}
```

### Snackbar

```kotlin
val snackbarHostState = remember { SnackbarHostState() }

Scaffold(
    snackbarHost = { SnackbarHost(snackbarHostState) }
) { paddingValues ->
    // Content

    LaunchedEffect(Unit) {
        viewModel.events.collect { event ->
            when (event) {
                is UiEvent.ShowSnackbar -> {
                    val result = snackbarHostState.showSnackbar(
                        message = event.message,
                        actionLabel = event.action,
                        duration = SnackbarDuration.Short
                    )
                    if (result == SnackbarResult.ActionPerformed) {
                        viewModel.onSnackbarAction()
                    }
                }
            }
        }
    }
}
```

---

## Color Roles Cheat Sheet

```kotlin
// Primary: key actions, active states
MaterialTheme.colorScheme.primary              // background of primary button
MaterialTheme.colorScheme.onPrimary            // text/icon on primary background
MaterialTheme.colorScheme.primaryContainer     // filled tonal button background
MaterialTheme.colorScheme.onPrimaryContainer   // text/icon on primary container

// Secondary: supporting elements
MaterialTheme.colorScheme.secondary
MaterialTheme.colorScheme.secondaryContainer

// Surface: backgrounds for UI areas
MaterialTheme.colorScheme.surface              // screen background
MaterialTheme.colorScheme.surfaceVariant       // cards, chips
MaterialTheme.colorScheme.onSurface            // primary text
MaterialTheme.colorScheme.onSurfaceVariant     // secondary text, icons

// Error
MaterialTheme.colorScheme.error
MaterialTheme.colorScheme.onError
MaterialTheme.colorScheme.errorContainer
```

---

## Adaptive Layouts (Phones, Tablets, Foldables)

```kotlin
// Get the window size class
@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            AppTheme {
                val windowSizeClass = calculateWindowSizeClass(this)
                AppRoot(windowSizeClass = windowSizeClass)
            }
        }
    }
}

// Adapt layout based on width
@Composable
fun AppRoot(windowSizeClass: WindowSizeClass) {
    val isExpandedWidth = windowSizeClass.widthSizeClass == WindowWidthSizeClass.Expanded

    if (isExpandedWidth) {
        // Tablet / foldable expanded: NavigationRail + two-pane
        TabletLayout()
    } else {
        // Phone: NavigationBar + single pane
        PhoneLayout()
    }
}

// ListDetailPaneScaffold (large screens)
@Composable
fun PostsAdaptiveScreen() {
    val navigator = rememberListDetailPaneScaffoldNavigator<String>()

    ListDetailPaneScaffold(
        directive = navigator.scaffoldDirective,
        value = navigator.scaffoldValue,
        listPane = {
            AnimatedPane {
                PostListPane(
                    onPostSelected = { id ->
                        navigator.navigateTo(ListDetailPaneScaffoldRole.Detail, id)
                    }
                )
            }
        },
        detailPane = {
            AnimatedPane {
                val postId = navigator.currentDestination?.content
                if (postId != null) {
                    PostDetailPane(postId = postId)
                } else {
                    PlaceholderPane()
                }
            }
        }
    )
}
```

---

## Edge-to-Edge Display

```kotlin
// MainActivity.kt
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge() // call before setContent

        setContent {
            AppTheme {
                Surface(modifier = Modifier.fillMaxSize()) {
                    AppNavHost()
                }
            }
        }
    }
}

// Handle insets in Scaffold
Scaffold(
    modifier = Modifier.fillMaxSize()
) { paddingValues ->
    LazyColumn(
        contentPadding = paddingValues // respects system bar insets
    ) { /* items */ }
}

// Manual inset handling when needed
Box(
    modifier = Modifier
        .fillMaxSize()
        .windowInsetsPadding(WindowInsets.systemBars)
) { /* content */ }

// Status bar color via themes (recommended)
// In themes.xml:
// <item name="android:statusBarColor">@android:color/transparent</item>
```

---

## Material 3 Animations and Transitions

```kotlin
// AnimatedVisibility
AnimatedVisibility(
    visible = isVisible,
    enter = fadeIn() + slideInVertically(),
    exit = fadeOut() + slideOutVertically()
) {
    Card { Text("Animated content") }
}

// AnimatedContent for state changes
AnimatedContent(
    targetState = uiState,
    transitionSpec = {
        fadeIn(animationSpec = tween(300)) togetherWith fadeOut(animationSpec = tween(300))
    },
    label = "state_transition"
) { state ->
    when (state) {
        is UiState.Loading -> CircularProgressIndicator()
        is UiState.Success -> ContentView(state.data)
        is UiState.Error -> ErrorView(state.message)
    }
}

// Shared element transitions (Navigation 2.8+)
// Source
Modifier.sharedElement(
    rememberSharedContentState(key = "image-${item.id}"),
    animatedVisibilityScope = this
)

// Destination
Modifier.sharedElement(
    rememberSharedContentState(key = "image-${item.id}"),
    animatedVisibilityScope = this
)
```

---

## Migration from Material 2

| Material 2 | Material 3 |
|-----------|-----------|
| `import androidx.compose.material.*` | `import androidx.compose.material3.*` |
| `MaterialTheme.colors.primary` | `MaterialTheme.colorScheme.primary` |
| `MaterialTheme.typography.h6` | `MaterialTheme.typography.titleLarge` |
| `Surface(elevation = 4.dp)` | `Card` or `Surface(tonalElevation = 4.dp)` |
| `Scaffold(bottomBar = { BottomNavigation { } })` | `Scaffold(bottomBar = { NavigationBar { } })` |
| `TopAppBar` | `TopAppBar` (same name, different package) |
| `Button` | `Button` (same name, different package) |
| `rememberScaffoldState()` | `SnackbarHostState()` directly |
| `scaffoldState.snackbarHostState.showSnackbar()` | `snackbarHostState.showSnackbar()` |

---

## Material 3 Rules

### DO

- Use `MaterialTheme.colorScheme` for every color reference — never hardcode
- Use `MaterialTheme.typography` for all text styles
- Use `MaterialTheme.shapes` for component shapes
- Apply dynamic color when running on Android 12+ (API 31+)
- Use semantic color names (`onSurface`, `primaryContainer`) not descriptive ones
- Use `NavigationRail` on tablets and `NavigationBar` on phones
- Use `enableEdgeToEdge()` in every Activity
- Apply `fillMaxSize()` to the root `Surface`

### DON'T

- Never import from `androidx.compose.material` — only `material3`
- Never use `Color(0xFFABCDEF)` directly in Composables — define in theme
- Never mix Material 2 and Material 3 components in the same module
- Never create custom navigation components when NavigationBar / NavigationRail / NavigationDrawer meet the need
- Never hardcode font sizes — use typography scale
- Never hardcode corner radii — use shapes from theme

---

*Material Design 3 guidelines: https://m3.material.io*
