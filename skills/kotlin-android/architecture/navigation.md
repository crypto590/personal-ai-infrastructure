# Navigation (Navigation Compose)

**Part of:** [kotlin-android](../SKILL.md) > Architecture

**Related:**
- [viewmodels.md](viewmodels.md) - ViewModels that emit navigation events
- [composables.md](composables.md) - Composables that handle navigation

---

## Overview

Use type-safe Navigation Compose 2.8+ with `@Serializable` route classes. ViewModels own navigation intent via a sealed class or Channel; Composables own the `NavController` mechanism.

**Principle:**
- ViewModel declares WHAT to navigate to (sealed interface events)
- Composable implements HOW to navigate (NavController.navigate())
- Routes are `@Serializable` data classes/objects — never plain strings

---

## Type-Safe Routes (Navigation 2.8+)

### Route Definitions

```kotlin
// In a shared Routes.kt file or per-feature
@Serializable
data object HomeRoute

@Serializable
data object SearchRoute

@Serializable
data class ProfileRoute(val userId: String)

@Serializable
data class ArticleDetailRoute(val articleId: String, val fromPush: Boolean = false)

// Grouped top-level destinations
@Serializable
sealed interface TopLevelRoute {
    @Serializable data object Home : TopLevelRoute
    @Serializable data object Search : TopLevelRoute
    @Serializable data object Profile : TopLevelRoute
}
```

### Basic NavHost Setup

```kotlin
@Composable
fun AppNavigation(modifier: Modifier = Modifier) {
    val navController = rememberNavController()

    NavHost(
        navController = navController,
        startDestination = HomeRoute,
        modifier = modifier
    ) {
        composable<HomeRoute> {
            HomeScreen(
                onNavigateToArticle = { id ->
                    navController.navigate(ArticleDetailRoute(articleId = id))
                },
                onNavigateToSearch = {
                    navController.navigate(SearchRoute)
                }
            )
        }

        composable<SearchRoute> {
            SearchScreen(
                onNavigateBack = { navController.popBackStack() },
                onNavigateToArticle = { id ->
                    navController.navigate(ArticleDetailRoute(articleId = id))
                }
            )
        }

        composable<ArticleDetailRoute> { backStackEntry ->
            val route = backStackEntry.toRoute<ArticleDetailRoute>()
            ArticleDetailScreen(
                articleId = route.articleId,
                onNavigateBack = { navController.popBackStack() }
            )
        }

        composable<ProfileRoute> { backStackEntry ->
            val route = backStackEntry.toRoute<ProfileRoute>()
            ProfileScreen(
                userId = route.userId,
                onNavigateBack = { navController.popBackStack() }
            )
        }
    }
}
```

---

## Navigation Events from ViewModel

### Channel for One-Time Events

```kotlin
@HiltViewModel
class ArticleViewModel @Inject constructor(
    private val repository: ArticleRepository
) : ViewModel() {

    sealed interface NavEvent {
        data class ToDetail(val articleId: String) : NavEvent
        data object ToSearch : NavEvent
        data object Back : NavEvent
    }

    private val _navEvents = Channel<NavEvent>(Channel.BUFFERED)
    val navEvents = _navEvents.receiveAsFlow()

    fun onArticleClicked(articleId: String) {
        viewModelScope.launch {
            _navEvents.send(NavEvent.ToDetail(articleId))
        }
    }

    fun onSearchClicked() {
        viewModelScope.launch {
            _navEvents.send(NavEvent.ToSearch)
        }
    }
}

// Composable collects and acts on navigation events
@Composable
fun ArticleListScreen(
    onNavigateToDetail: (String) -> Unit,
    onNavigateToSearch: () -> Unit,
    viewModel: ArticleViewModel = hiltViewModel()
) {
    LaunchedEffect(Unit) {
        viewModel.navEvents.collect { event ->
            when (event) {
                is ArticleViewModel.NavEvent.ToDetail -> onNavigateToDetail(event.articleId)
                is ArticleViewModel.NavEvent.ToSearch -> onNavigateToSearch()
                is ArticleViewModel.NavEvent.Back -> { /* handled by caller */ }
            }
        }
    }

    // UI content...
}
```

---

## Nested Navigation Graphs Per Feature

Structure your navigation into feature-scoped `NavGraphBuilder` extensions:

```kotlin
// articles/ArticlesNavGraph.kt
fun NavGraphBuilder.articlesGraph(navController: NavController) {
    composable<ArticleListRoute> {
        ArticleListScreen(
            onNavigateToDetail = { id ->
                navController.navigate(ArticleDetailRoute(articleId = id))
            }
        )
    }
    composable<ArticleDetailRoute> { backStackEntry ->
        val route = backStackEntry.toRoute<ArticleDetailRoute>()
        ArticleDetailScreen(
            articleId = route.articleId,
            onNavigateBack = { navController.popBackStack() }
        )
    }
}

// settings/SettingsNavGraph.kt
fun NavGraphBuilder.settingsGraph(navController: NavController) {
    composable<SettingsRoute> {
        SettingsScreen(onNavigateBack = { navController.popBackStack() })
    }
    composable<NotificationsSettingsRoute> {
        NotificationsSettingsScreen(onNavigateBack = { navController.popBackStack() })
    }
}

// Root NavHost composes feature graphs
@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(navController = navController, startDestination = HomeRoute) {
        composable<HomeRoute> { HomeScreen(navController) }
        articlesGraph(navController)
        settingsGraph(navController)
    }
}
```

---

## Bottom Navigation with NavigationBar

```kotlin
@Composable
fun MainScreen() {
    val navController = rememberNavController()
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentDestination = navBackStackEntry?.destination

    val topLevelDestinations = listOf(
        TopLevelDest(HomeRoute, Icons.Default.Home, "Home"),
        TopLevelDest(SearchRoute, Icons.Default.Search, "Search"),
        TopLevelDest(ProfileRoute(userId = "me"), Icons.Default.Person, "Profile")
    )

    Scaffold(
        bottomBar = {
            NavigationBar {
                topLevelDestinations.forEach { dest ->
                    NavigationBarItem(
                        icon = { Icon(dest.icon, dest.label) },
                        label = { Text(dest.label) },
                        selected = currentDestination?.hasRoute(dest.route::class) == true,
                        onClick = {
                            navController.navigate(dest.route) {
                                // Pop to start destination to avoid large back stack
                                popUpTo(navController.graph.findStartDestination().id) {
                                    saveState = true
                                }
                                launchSingleTop = true
                                restoreState = true
                            }
                        }
                    )
                }
            }
        }
    ) { padding ->
        NavHost(
            navController = navController,
            startDestination = HomeRoute,
            modifier = Modifier.padding(padding)
        ) {
            composable<HomeRoute> { HomeScreen() }
            composable<SearchRoute> { SearchScreen() }
            composable<ProfileRoute> { backStackEntry ->
                val route = backStackEntry.toRoute<ProfileRoute>()
                ProfileScreen(userId = route.userId)
            }
        }
    }
}

data class TopLevelDest<T : Any>(
    val route: T,
    val icon: ImageVector,
    val label: String
)
```

---

## Navigation Drawer

```kotlin
@Composable
fun DrawerNavigation() {
    val navController = rememberNavController()
    val drawerState = rememberDrawerState(initialValue = DrawerValue.Closed)
    val scope = rememberCoroutineScope()

    ModalNavigationDrawer(
        drawerState = drawerState,
        drawerContent = {
            ModalDrawerSheet {
                Spacer(modifier = Modifier.height(16.dp))
                NavigationDrawerItem(
                    label = { Text("Home") },
                    icon = { Icon(Icons.Default.Home, "Home") },
                    selected = false,
                    onClick = {
                        navController.navigate(HomeRoute)
                        scope.launch { drawerState.close() }
                    }
                )
                NavigationDrawerItem(
                    label = { Text("Settings") },
                    icon = { Icon(Icons.Default.Settings, "Settings") },
                    selected = false,
                    onClick = {
                        navController.navigate(SettingsRoute)
                        scope.launch { drawerState.close() }
                    }
                )
            }
        }
    ) {
        Scaffold(
            topBar = {
                TopAppBar(
                    title = { Text("App") },
                    navigationIcon = {
                        IconButton(onClick = { scope.launch { drawerState.open() } }) {
                            Icon(Icons.Default.Menu, "Menu")
                        }
                    }
                )
            }
        ) { padding ->
            NavHost(navController, HomeRoute, Modifier.padding(padding)) {
                composable<HomeRoute> { HomeScreen() }
                composable<SettingsRoute> { SettingsScreen() }
            }
        }
    }
}
```

---

## Deep Linking Configuration

```kotlin
// Route with deep link support
@Serializable
data class ArticleDetailRoute(val articleId: String)

// In NavHost
composable<ArticleDetailRoute>(
    deepLinks = listOf(
        navDeepLink<ArticleDetailRoute>(
            basePath = "https://example.com/articles"
        )
    )
) { backStackEntry ->
    val route = backStackEntry.toRoute<ArticleDetailRoute>()
    ArticleDetailScreen(articleId = route.articleId)
}

// AndroidManifest.xml intent filter
// <intent-filter>
//   <action android:name="android.intent.action.VIEW" />
//   <category android:name="android.intent.category.DEFAULT" />
//   <category android:name="android.intent.category.BROWSABLE" />
//   <data android:scheme="https" android:host="example.com" android:pathPrefix="/articles" />
// </intent-filter>
```

---

## Back Stack Management

```kotlin
// Navigate and clear back stack (e.g., after login)
navController.navigate(HomeRoute) {
    popUpTo(0) { inclusive = true }  // Pop everything
    launchSingleTop = true
}

// Navigate to top-level tab without stacking
navController.navigate(SearchRoute) {
    popUpTo(navController.graph.findStartDestination().id) {
        saveState = true
    }
    launchSingleTop = true
    restoreState = true
}

// Navigate back with result
// In destination screen:
navController.previousBackStackEntry?.savedStateHandle?.set("result", "saved")
navController.popBackStack()

// In origin screen:
val savedStateHandle = navController.currentBackStackEntry?.savedStateHandle
val result = savedStateHandle?.get<String>("result")
```

---

## Modal and Dialog Destinations

```kotlin
// Dialog destination
@Serializable
data object ConfirmDeleteRoute

// In NavHost
dialog<ConfirmDeleteRoute> {
    AlertDialog(
        onDismissRequest = { navController.popBackStack() },
        title = { Text("Delete item?") },
        text = { Text("This cannot be undone.") },
        confirmButton = {
            TextButton(onClick = {
                navController.popBackStack()
                viewModel.confirmDelete()
            }) { Text("Delete") }
        },
        dismissButton = {
            TextButton(onClick = { navController.popBackStack() }) { Text("Cancel") }
        }
    )
}

// Bottom sheet state via nullable ViewModel state (preferred for ModalBottomSheet)
@HiltViewModel
class FeatureViewModel : ViewModel() {
    private val _sheetContent = MutableStateFlow<SheetContent?>(null)
    val sheetContent: StateFlow<SheetContent?> = _sheetContent.asStateFlow()

    sealed interface SheetContent {
        data class EditItem(val item: Item) : SheetContent
        data object ShareOptions : SheetContent
    }

    fun showSheet(content: SheetContent) { _sheetContent.value = content }
    fun dismissSheet() { _sheetContent.value = null }
}

@Composable
fun FeatureScreen(viewModel: FeatureViewModel = hiltViewModel()) {
    val sheetContent by viewModel.sheetContent.collectAsStateWithLifecycle()

    // Main content...

    sheetContent?.let { content ->
        ModalBottomSheet(onDismissRequest = viewModel::dismissSheet) {
            when (content) {
                is FeatureViewModel.SheetContent.EditItem -> EditContent(content.item)
                is FeatureViewModel.SheetContent.ShareOptions -> ShareContent()
            }
        }
    }
}
```

---

## Tab Navigation Within a Screen

```kotlin
@Composable
fun ProfileScreen(userId: String) {
    var selectedTab by rememberSaveable { mutableIntStateOf(0) }
    val tabs = listOf("Posts", "Followers", "Following")

    Column {
        TabRow(selectedTabIndex = selectedTab) {
            tabs.forEachIndexed { index, title ->
                Tab(
                    selected = selectedTab == index,
                    onClick = { selectedTab = index },
                    text = { Text(title) }
                )
            }
        }

        when (selectedTab) {
            0 -> UserPostsTab(userId = userId)
            1 -> FollowersTab(userId = userId)
            2 -> FollowingTab(userId = userId)
        }
    }
}
```

---

## Navigation Testing

```kotlin
@Test
fun `clicking article navigates to detail screen`() {
    val navController = TestNavHostController(ApplicationProvider.getApplicationContext())

    composeTestRule.setContent {
        navController.navigatorProvider.addNavigator(ComposeNavigator())
        NavHost(navController, startDestination = HomeRoute) {
            composable<HomeRoute> {
                HomeScreen(
                    onNavigateToArticle = { id ->
                        navController.navigate(ArticleDetailRoute(articleId = id))
                    }
                )
            }
            composable<ArticleDetailRoute> { ArticleDetailScreen() }
        }
    }

    composeTestRule.onNodeWithText("First Article").performClick()

    assertEquals(
        ArticleDetailRoute::class.qualifiedName,
        navController.currentBackStackEntry?.destination?.route
    )
}
```

---

## Anti-Patterns

### String-Based Routes (Pre-2.8 Pattern)

```kotlin
// BAD — no type safety, typo-prone
navController.navigate("article_detail/$articleId")

composable("article_detail/{articleId}") { backStackEntry ->
    val id = backStackEntry.arguments?.getString("articleId") ?: return@composable
    ArticleDetailScreen(articleId = id)
}

// GOOD — type-safe @Serializable routes
navController.navigate(ArticleDetailRoute(articleId = articleId))

composable<ArticleDetailRoute> { backStackEntry ->
    val route = backStackEntry.toRoute<ArticleDetailRoute>()
    ArticleDetailScreen(articleId = route.articleId)
}
```

### Navigation Logic in Composables

```kotlin
// BAD — navigation decision buried in UI
@Composable
fun ArticleCard(article: Article, navController: NavController) {
    Card(onClick = {
        if (article.isPremium && !userIsPremium) {
            navController.navigate(UpgradeRoute)  // Business logic in composable!
        } else {
            navController.navigate(ArticleDetailRoute(article.id))
        }
    }) { /* content */ }
}

// GOOD — ViewModel owns the logic, composable passes event
@Composable
fun ArticleCard(article: Article, onArticleClicked: (Article) -> Unit) {
    Card(onClick = { onArticleClicked(article) }) { /* content */ }
}

// ViewModel decides where to navigate
fun onArticleClicked(article: Article) {
    viewModelScope.launch {
        if (article.isPremium && !userRepository.isPremiumUser()) {
            _navEvents.send(NavEvent.ToUpgrade)
        } else {
            _navEvents.send(NavEvent.ToDetail(article.id))
        }
    }
}
```

### Holding NavController in ViewModel

```kotlin
// BAD — NavController is a UI concern, ViewModel shouldn't hold it
@HiltViewModel
class MyViewModel @Inject constructor(
    private val navController: NavController  // Wrong!
) : ViewModel()

// GOOD — ViewModel emits events, Composable handles NavController
@HiltViewModel
class MyViewModel @Inject constructor() : ViewModel() {
    private val _navEvents = Channel<NavEvent>(Channel.BUFFERED)
    val navEvents = _navEvents.receiveAsFlow()
}
```
