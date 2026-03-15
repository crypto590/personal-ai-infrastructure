# Composables (Jetpack Compose)

**Part of:** [kotlin-android](../SKILL.md) > Architecture

**Related:**
- [viewmodels.md](viewmodels.md) - ViewModels that Composables observe
- [navigation.md](navigation.md) - Navigation patterns in Composables

---

## Overview

Composables render UI and delegate actions to ViewModels. They observe ViewModel state and never call repositories directly or mutate state externally.

**Key characteristics:**
- Obtain ViewModel with `hiltViewModel()` (or `viewModel()` without Hilt)
- Collect state with `collectAsStateWithLifecycle()` — not `collectAsState()`
- Delegate all actions to ViewModel methods
- No business logic in Composables
- Never call Repositories directly
- State flows down, events flow up (unidirectional data flow)

---

## Composable Naming and Parameter Conventions

```kotlin
// Screen-level composables (full screen, own ViewModel)
@Composable
fun UserProfileScreen(
    userId: String,                              // Route arguments first
    onNavigateToSettings: () -> Unit,            // Navigation callbacks
    onNavigateBack: () -> Unit,
    viewModel: UserProfileViewModel = hiltViewModel()  // ViewModel last with default
)

// UI components (stateless, receive data)
@Composable
fun UserCard(
    user: User,                    // Data first
    onClick: () -> Unit,           // Callbacks
    modifier: Modifier = Modifier  // Modifier always last with default
)

// Slot API composables
@Composable
fun AppScaffold(
    title: String,
    navigationIcon: @Composable () -> Unit = {},
    actions: @Composable RowScope.() -> Unit = {},
    content: @Composable (PaddingValues) -> Unit
)
```

---

## Basic Screen Pattern

```kotlin
@Composable
fun UserScreen(
    viewModel: UserViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    when (val state = uiState) {
        is UserUiState.Loading -> {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator()
            }
        }
        is UserUiState.Success -> {
            UserContent(
                user = state.user,
                onRefresh = viewModel::refresh
            )
        }
        is UserUiState.Error -> {
            ErrorScreen(
                message = state.message,
                onRetry = viewModel::retry
            )
        }
    }

    LaunchedEffect(Unit) {
        viewModel.loadUser()
    }
}

@Composable
private fun UserContent(
    user: User,
    onRefresh: () -> Unit,
    modifier: Modifier = Modifier
) {
    // Pure UI — receives data, calls callbacks
    Column(modifier = modifier.fillMaxSize().padding(16.dp)) {
        Text(text = user.displayName, style = MaterialTheme.typography.headlineMedium)
        Text(text = user.email, style = MaterialTheme.typography.bodyLarge)
    }
}
```

---

## State Hoisting Pattern

Hoist state to the lowest common ancestor that needs it:

```kotlin
// Stateful composable (owns ViewModel)
@Composable
fun SearchScreen(viewModel: SearchViewModel = hiltViewModel()) {
    val query by viewModel.query.collectAsStateWithLifecycle()
    val results by viewModel.results.collectAsStateWithLifecycle()

    SearchScreenContent(
        query = query,
        results = results,
        onQueryChange = viewModel::onQueryChanged,
        onClearQuery = viewModel::clearQuery
    )
}

// Stateless composable (receives state and callbacks)
@Composable
fun SearchScreenContent(
    query: String,
    results: SearchUiState,
    onQueryChange: (String) -> Unit,
    onClearQuery: () -> Unit,
    modifier: Modifier = Modifier
) {
    Column(modifier = modifier.fillMaxSize()) {
        SearchBar(
            query = query,
            onQueryChange = onQueryChange,
            onClearQuery = onClearQuery
        )
        SearchResults(state = results)
    }
}
```

**Benefits of hoisting:**
- Stateless components are easily tested and previewed
- State logic is centralized in the ViewModel
- Components are reusable across contexts

---

## ViewModel Integration

### collectAsStateWithLifecycle (preferred)

```kotlin
// GOOD — respects lifecycle, stops collecting when app goes to background
val uiState by viewModel.uiState.collectAsStateWithLifecycle()

// BAD — collects even when app is in background (battery waste)
val uiState by viewModel.uiState.collectAsState()
```

Requires dependency:
```kotlin
implementation("androidx.lifecycle:lifecycle-runtime-compose:2.8.x")
```

### Collecting Multiple Flows

```kotlin
@Composable
fun DashboardScreen(viewModel: DashboardViewModel = hiltViewModel()) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    val isRefreshing by viewModel.isRefreshing.collectAsStateWithLifecycle()
    val hasNotifications by viewModel.hasNotifications.collectAsStateWithLifecycle()

    // Use all three independently
}
```

---

## LaunchedEffect, rememberCoroutineScope, DisposableEffect

### LaunchedEffect — side effects tied to composition lifecycle

```kotlin
// Run once when composable enters composition
LaunchedEffect(Unit) {
    viewModel.loadData()
}

// Re-run when key changes
LaunchedEffect(userId) {
    viewModel.loadUser(userId)
}

// Collect one-time events (navigation, snackbars)
val snackbarHostState = remember { SnackbarHostState() }
LaunchedEffect(Unit) {
    viewModel.events.collect { event ->
        when (event) {
            is UiEvent.ShowSnackbar -> snackbarHostState.showSnackbar(event.message)
            is UiEvent.NavigateToDetail -> onNavigateToDetail(event.id)
        }
    }
}
```

### rememberCoroutineScope — user-triggered coroutines

```kotlin
val scope = rememberCoroutineScope()
val snackbarHostState = remember { SnackbarHostState() }

Button(onClick = {
    // Coroutine launched by user action, not composition lifecycle
    scope.launch {
        snackbarHostState.showSnackbar("Item saved")
    }
}) {
    Text("Save")
}
```

### DisposableEffect — cleanup when leaving composition

```kotlin
DisposableEffect(lifecycleOwner) {
    val observer = LifecycleEventObserver { _, event ->
        if (event == Lifecycle.Event.ON_RESUME) {
            viewModel.onResume()
        }
    }
    lifecycleOwner.lifecycle.addObserver(observer)

    onDispose {
        lifecycleOwner.lifecycle.removeObserver(observer)
    }
}
```

---

## Key Composable Patterns

### List Pattern (LazyColumn)

```kotlin
@Composable
fun ArticleListScreen(viewModel: ArticleViewModel = hiltViewModel()) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    val isRefreshing by viewModel.isRefreshing.collectAsStateWithLifecycle()

    PullToRefreshBox(
        isRefreshing = isRefreshing,
        onRefresh = viewModel::refresh,
        modifier = Modifier.fillMaxSize()
    ) {
        when (val state = uiState) {
            is ArticleListUiState.Loading -> LoadingIndicator()
            is ArticleListUiState.Empty -> EmptyState(message = "No articles")
            is ArticleListUiState.Success -> {
                LazyColumn {
                    items(
                        items = state.articles,
                        key = { it.id }  // Stable keys for efficient recomposition
                    ) { article ->
                        ArticleCard(
                            article = article,
                            onClick = { viewModel.onArticleClicked(article.id) }
                        )
                        HorizontalDivider()
                    }
                }
            }
            is ArticleListUiState.Error -> ErrorState(
                message = state.message,
                onRetry = viewModel::retry
            )
        }
    }
}

@Composable
fun ArticleCard(
    article: Article,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        onClick = onClick,
        modifier = modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 8.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(text = article.title, style = MaterialTheme.typography.titleMedium)
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = article.preview,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                maxLines = 2,
                overflow = TextOverflow.Ellipsis
            )
        }
    }
}
```

### Form Pattern

```kotlin
@Composable
fun SignUpScreen(viewModel: SignUpViewModel = hiltViewModel()) {
    val formState by viewModel.formState.collectAsStateWithLifecycle()
    val snackbarHostState = remember { SnackbarHostState() }

    LaunchedEffect(Unit) {
        viewModel.events.collect { event ->
            when (event) {
                is SignUpEvent.ShowError -> snackbarHostState.showSnackbar(event.message)
                is SignUpEvent.NavigateToHome -> onNavigateToHome()
            }
        }
    }

    Scaffold(
        snackbarHost = { SnackbarHost(snackbarHostState) },
        topBar = { TopAppBar(title = { Text("Create Account") }) }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            OutlinedTextField(
                value = formState.email,
                onValueChange = viewModel::onEmailChanged,
                label = { Text("Email") },
                isError = formState.emailError != null,
                supportingText = formState.emailError?.let { { Text(it) } },
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Email),
                singleLine = true,
                modifier = Modifier.fillMaxWidth()
            )

            OutlinedTextField(
                value = formState.password,
                onValueChange = viewModel::onPasswordChanged,
                label = { Text("Password") },
                isError = formState.passwordError != null,
                supportingText = formState.passwordError?.let { { Text(it) } },
                visualTransformation = PasswordVisualTransformation(),
                singleLine = true,
                modifier = Modifier.fillMaxWidth()
            )

            Button(
                onClick = viewModel::onSubmit,
                enabled = formState.isValid && !formState.isSubmitting,
                modifier = Modifier.fillMaxWidth()
            ) {
                if (formState.isSubmitting) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(20.dp),
                        strokeWidth = 2.dp
                    )
                } else {
                    Text("Create Account")
                }
            }
        }
    }
}
```

### Detail Screen Pattern

```kotlin
@Composable
fun ProductDetailScreen(
    productId: String,
    onNavigateBack: () -> Unit,
    onNavigateToCart: () -> Unit,
    viewModel: ProductDetailViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    LaunchedEffect(productId) {
        viewModel.loadProduct(productId)
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Product") },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, "Back")
                    }
                },
                actions = {
                    IconButton(onClick = onNavigateToCart) {
                        Icon(Icons.Default.ShoppingCart, "Cart")
                    }
                }
            )
        }
    ) { padding ->
        when (val state = uiState) {
            is ProductDetailUiState.Loading -> LoadingIndicator(modifier = Modifier.padding(padding))
            is ProductDetailUiState.Success -> ProductDetailContent(
                product = state.product,
                onAddToCart = { viewModel.addToCart(state.product) },
                modifier = Modifier.padding(padding)
            )
            is ProductDetailUiState.Error -> ErrorState(
                message = state.message,
                onRetry = { viewModel.loadProduct(productId) },
                modifier = Modifier.padding(padding)
            )
        }
    }
}
```

---

## Preview Annotations

```kotlin
// Single preview
@Preview(showBackground = true)
@Composable
private fun UserCardPreview() {
    MaterialTheme {
        UserCard(
            user = User(id = "1", name = "Alice Smith", email = "alice@example.com"),
            onClick = {}
        )
    }
}

// Multiple configurations
@Preview(name = "Light", showBackground = true)
@Preview(name = "Dark", uiMode = Configuration.UI_MODE_NIGHT_YES, showBackground = true)
@Preview(name = "Large font", fontScale = 1.5f, showBackground = true)
@Composable
private fun ArticleCardPreviews() {
    MaterialTheme {
        ArticleCard(
            article = Article(
                id = "1",
                title = "Preview Article",
                preview = "This is a preview of the article content that shows how it looks."
            ),
            onClick = {}
        )
    }
}

// Full screen preview
@Preview(showSystemUi = true)
@Composable
private fun UserScreenPreview() {
    MaterialTheme {
        UserContent(
            user = User(id = "1", name = "Alice", email = "alice@example.com"),
            onRefresh = {}
        )
    }
}
```

---

## remember vs rememberSaveable

```kotlin
// remember — survives recomposition, lost on config change or process death
val listState = remember { LazyListState() }
val snackbarState = remember { SnackbarHostState() }
val focusRequester = remember { FocusRequester() }

// rememberSaveable — survives recomposition AND config changes/process death
var searchQuery by rememberSaveable { mutableStateOf("") }
var isFilterExpanded by rememberSaveable { mutableStateOf(false) }

// rememberSaveable with custom Saver for complex types
var selectedTab by rememberSaveable(
    stateSaver = Saver(
        save = { it.ordinal },
        restore = { Tab.entries[it] }
    )
) { mutableStateOf(Tab.HOME) }
```

**Guideline:** Use `rememberSaveable` for user-visible UI state that would be jarring to lose (text input, selected tab). Use `remember` for technical objects (state holders, focus requesters).

---

## CompositionLocal

Use `CompositionLocal` for data that needs to be available deep in the tree without passing through every composable:

```kotlin
// Define
val LocalAppConfig = compositionLocalOf<AppConfig> {
    error("No AppConfig provided")
}

// Provide at root
@Composable
fun AppRoot() {
    CompositionLocalProvider(LocalAppConfig provides AppConfig.default) {
        AppNavigation()
    }
}

// Consume anywhere in the tree
@Composable
fun SomeDeepComponent() {
    val config = LocalAppConfig.current
    Text(text = config.appName)
}
```

**Use sparingly.** Overuse makes data flow hard to trace. Good candidates: theming, navigation, analytics, feature flags.

---

## Performance: Stability

### @Immutable and @Stable

```kotlin
// Tell the Compose compiler this class is stable (safe to skip recomposition)
@Immutable
data class UserCardData(
    val id: String,
    val name: String,
    val avatarUrl: String?
)

// For classes with stable observable state but mutable internals
@Stable
class FilterState {
    var selectedCategory by mutableStateOf<Category?>(null)
    var priceRange by mutableStateOf(0f..100f)
}
```

### derivedStateOf — avoid recomposition from rapid state changes

```kotlin
@Composable
fun ItemList(items: List<Item>) {
    val listState = rememberLazyListState()

    // Only recomposes when showScrollToTop actually changes (true/false),
    // not every time firstVisibleItemIndex changes
    val showScrollToTop by remember {
        derivedStateOf { listState.firstVisibleItemIndex > 2 }
    }

    Box {
        LazyColumn(state = listState) {
            items(items, key = { it.id }) { ItemRow(it) }
        }
        if (showScrollToTop) {
            FloatingActionButton(onClick = { /* scroll to top */ }) {
                Icon(Icons.Default.KeyboardArrowUp, "Scroll to top")
            }
        }
    }
}
```

### ImmutableList for stable collections

```kotlin
// Unstable — List is not @Immutable in Compose compiler's view
data class NewsUiState(val articles: List<Article>)

// Stable — ImmutableList from kotlinx.collections.immutable
@Immutable
data class NewsUiState(val articles: ImmutableList<Article>)

// In ViewModel
import kotlinx.collections.immutable.toImmutableList

_uiState.value = NewsUiState(articles = result.toImmutableList())
```

---

## Anti-Patterns

### Side Effects in Composition

```kotlin
// BAD — network call during composition
@Composable
fun UserScreen(viewModel: UserViewModel) {
    viewModel.loadUser()  // Called on every recomposition!
    // ...
}

// GOOD — side effect in LaunchedEffect
@Composable
fun UserScreen(viewModel: UserViewModel) {
    LaunchedEffect(Unit) {
        viewModel.loadUser()  // Called once
    }
    // ...
}
```

### Calling Repositories Directly

```kotlin
// BAD — Composable bypasses ViewModel
@Composable
fun UserScreen(repo: UserRepository = get()) {
    val user by repo.observeUser("1").collectAsStateWithLifecycle()
    // ...
}

// GOOD — always through ViewModel
@Composable
fun UserScreen(viewModel: UserViewModel = hiltViewModel()) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    // ...
}
```

### Unstable Lambda Captures

```kotlin
// BAD — new lambda instance on each recomposition causes unnecessary recomposition of children
@Composable
fun ItemList(items: List<Item>, viewModel: ItemViewModel) {
    LazyColumn {
        items(items) { item ->
            ItemRow(
                item = item,
                onClick = { viewModel.onItemClicked(item.id) }  // New lambda each time
            )
        }
    }
}

// GOOD — use stable function references or remember
@Composable
fun ItemList(items: List<Item>, onItemClick: (String) -> Unit) {
    LazyColumn {
        items(items, key = { it.id }) { item ->
            ItemRow(item = item, onClick = { onItemClick(item.id) })
        }
    }
}
```

### collectAsState Instead of collectAsStateWithLifecycle

```kotlin
// BAD — collects when app is in background
val state by viewModel.uiState.collectAsState()

// GOOD — stops collecting when lifecycle is not at least STARTED
val state by viewModel.uiState.collectAsStateWithLifecycle()
```
