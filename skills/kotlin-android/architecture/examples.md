# Real-World Examples

**Part of:** [kotlin-android](../SKILL.md) > Architecture

---

## Overview

Complete, production-ready feature examples. Each example covers Model, Repository interface + implementation, ViewModel with sealed UiState, and a full Composable screen. Copy-paste ready for real projects.

---

## Example 1: User Profile Feature

### Model

```kotlin
// features/user/model/User.kt
import kotlinx.serialization.Serializable

@Serializable
data class User(
    val id: String,
    val name: String,
    val email: String,
    val bio: String? = null,
    val avatarUrl: String? = null,
    val createdAt: String = ""
) {
    val displayName: String
        get() = name.ifEmpty { email }

    val initials: String
        get() {
            val parts = name.trim().split(" ")
            return parts.take(2).mapNotNull { it.firstOrNull()?.uppercaseChar() }
                .joinToString("")
                .ifEmpty { email.firstOrNull()?.uppercaseChar()?.toString() ?: "?" }
        }
}
```

### Repository

```kotlin
// features/user/data/UserRepository.kt
interface UserRepository {
    suspend fun fetchUser(id: String): Result<User>
    suspend fun updateUser(user: User): Result<User>
}

// features/user/data/UserRepositoryImpl.kt
import javax.inject.Inject

class UserRepositoryImpl @Inject constructor(
    private val apiService: ApiService
) : UserRepository {

    override suspend fun fetchUser(id: String): Result<User> {
        return try {
            val response = apiService.getUser(id)
            Result.success(response.toDomain())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun updateUser(user: User): Result<User> {
        return try {
            val response = apiService.putUser(user.id, user.toRequest())
            Result.success(response.toDomain())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

### ViewModel

```kotlin
// features/user/UserViewModel.kt
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

sealed interface UserUiState {
    data object Loading : UserUiState
    data class Success(val user: User) : UserUiState
    data class Error(val message: String) : UserUiState
}

@HiltViewModel
class UserViewModel @Inject constructor(
    private val repository: UserRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<UserUiState>(UserUiState.Loading)
    val uiState: StateFlow<UserUiState> = _uiState.asStateFlow()

    fun loadUser(id: String) {
        viewModelScope.launch {
            _uiState.value = UserUiState.Loading
            repository.fetchUser(id)
                .onSuccess { _uiState.value = UserUiState.Success(it) }
                .onFailure { _uiState.value = UserUiState.Error(it.message ?: "Unknown error") }
        }
    }

    fun clearError() {
        if (_uiState.value is UserUiState.Error) {
            _uiState.value = UserUiState.Loading
        }
    }
}
```

### Composable

```kotlin
// features/user/UserScreen.kt
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import coil.compose.AsyncImage

@Composable
fun UserScreen(
    userId: String,
    onNavigateBack: () -> Unit = {},
    viewModel: UserViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    LaunchedEffect(userId) {
        viewModel.loadUser(userId)
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Profile") },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(
                            imageVector = Icons.Default.ArrowBack,
                            contentDescription = "Back"
                        )
                    }
                }
            )
        }
    ) { paddingValues ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues),
            contentAlignment = Alignment.Center
        ) {
            when (val state = uiState) {
                is UserUiState.Loading -> {
                    CircularProgressIndicator(
                        modifier = Modifier.testTag("loading_indicator")
                    )
                }
                is UserUiState.Success -> {
                    UserProfileContent(user = state.user)
                }
                is UserUiState.Error -> {
                    AlertDialog(
                        onDismissRequest = { viewModel.clearError() },
                        confirmButton = {
                            TextButton(onClick = { viewModel.clearError() }) {
                                Text("OK")
                            }
                        },
                        title = { Text("Error") },
                        text = { Text(state.message) }
                    )
                }
            }
        }
    }
}

@Composable
private fun UserProfileContent(user: User) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // Avatar
        if (user.avatarUrl != null) {
            AsyncImage(
                model = user.avatarUrl,
                contentDescription = "Profile photo of ${user.displayName}",
                modifier = Modifier
                    .size(96.dp)
                    .clip(CircleShape),
                contentScale = ContentScale.Crop
            )
        } else {
            Box(
                modifier = Modifier
                    .size(96.dp)
                    .clip(CircleShape)
                    .background(MaterialTheme.colorScheme.primaryContainer),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = user.initials,
                    style = MaterialTheme.typography.headlineMedium,
                    color = MaterialTheme.colorScheme.onPrimaryContainer
                )
            }
        }

        // Name and email
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Text(
                text = user.displayName,
                style = MaterialTheme.typography.headlineSmall,
                fontWeight = FontWeight.Bold
            )
            Text(
                text = user.email,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }

        // Bio
        user.bio?.let { bio ->
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.surfaceVariant
                )
            ) {
                Text(
                    text = bio,
                    modifier = Modifier.padding(16.dp),
                    style = MaterialTheme.typography.bodyLarge
                )
            }
        }
    }
}
```

---

## Example 2: Sign-In Form

### Model

```kotlin
// features/auth/model/AuthModels.kt
import kotlinx.serialization.Serializable

@Serializable
data class Credentials(
    val email: String,
    val password: String
)

@Serializable
data class AuthResponse(
    val userId: String,
    val token: String,
    val refreshToken: String
)
```

### Repository

```kotlin
// features/auth/data/AuthRepository.kt
interface AuthRepository {
    suspend fun signIn(credentials: Credentials): Result<AuthResponse>
    suspend fun signOut(): Result<Unit>
}

// features/auth/data/AuthRepositoryImpl.kt
import android.content.SharedPreferences
import androidx.core.content.edit
import javax.inject.Inject

class AuthRepositoryImpl @Inject constructor(
    private val apiService: ApiService,
    private val prefs: SharedPreferences
) : AuthRepository {

    override suspend fun signIn(credentials: Credentials): Result<AuthResponse> {
        return try {
            val response = apiService.postSignIn(
                email = credentials.email,
                password = credentials.password
            )
            prefs.edit {
                putString("auth_token", response.token)
                putString("user_id", response.userId)
            }
            Result.success(response.toDomain())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun signOut(): Result<Unit> {
        return try {
            prefs.edit {
                remove("auth_token")
                remove("user_id")
            }
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

### ViewModel

```kotlin
// features/auth/SignInViewModel.kt
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import javax.inject.Inject

data class SignInUiState(
    val email: String = "",
    val password: String = "",
    val isPasswordVisible: Boolean = false,
    val isLoading: Boolean = false,
    val emailError: String? = null,
    val generalError: String? = null
) {
    val isFormValid: Boolean
        get() = emailError == null && email.isNotEmpty() && password.length >= 8
}

sealed interface SignInEvent {
    data object NavigateToHome : SignInEvent
}

@HiltViewModel
class SignInViewModel @Inject constructor(
    private val repository: AuthRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(SignInUiState())
    val uiState: StateFlow<SignInUiState> = _uiState.asStateFlow()

    private val _events = Channel<SignInEvent>(Channel.BUFFERED)
    val events = _events.receiveAsFlow()

    fun onEmailChanged(email: String) {
        _uiState.update { state ->
            state.copy(
                email = email,
                emailError = validateEmail(email)
            )
        }
    }

    fun onPasswordChanged(password: String) {
        _uiState.update { it.copy(password = password) }
    }

    fun onTogglePasswordVisibility() {
        _uiState.update { it.copy(isPasswordVisible = !it.isPasswordVisible) }
    }

    fun onSignIn() {
        val state = _uiState.value
        if (!state.isFormValid) return

        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, generalError = null) }

            repository.signIn(Credentials(state.email, state.password))
                .onSuccess {
                    _events.send(SignInEvent.NavigateToHome)
                }
                .onFailure { error ->
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            generalError = error.message ?: "Sign in failed"
                        )
                    }
                }

            _uiState.update { it.copy(isLoading = false) }
        }
    }

    fun onDismissError() {
        _uiState.update { it.copy(generalError = null) }
    }

    private fun validateEmail(email: String): String? {
        if (email.isEmpty()) return null
        return if (!android.util.Patterns.EMAIL_ADDRESS.matcher(email).matches()) {
            "Invalid email address"
        } else null
    }
}
```

### Composable

```kotlin
// features/auth/SignInScreen.kt
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Visibility
import androidx.compose.material.icons.filled.VisibilityOff
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle

@Composable
fun SignInScreen(
    onNavigateToHome: () -> Unit,
    viewModel: SignInViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    LaunchedEffect(Unit) {
        viewModel.events.collect { event ->
            when (event) {
                is SignInEvent.NavigateToHome -> onNavigateToHome()
            }
        }
    }

    Scaffold { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(horizontal = 24.dp),
            verticalArrangement = Arrangement.Center,
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = "Sign In",
                style = MaterialTheme.typography.headlineMedium,
                modifier = Modifier.padding(bottom = 32.dp)
            )

            // Email field
            OutlinedTextField(
                value = uiState.email,
                onValueChange = viewModel::onEmailChanged,
                label = { Text("Email") },
                isError = uiState.emailError != null,
                supportingText = uiState.emailError?.let { { Text(it) } },
                keyboardOptions = KeyboardOptions(
                    keyboardType = KeyboardType.Email,
                    imeAction = ImeAction.Next
                ),
                singleLine = true,
                modifier = Modifier
                    .fillMaxWidth()
                    .testTag("email_field")
            )

            Spacer(modifier = Modifier.height(12.dp))

            // Password field
            OutlinedTextField(
                value = uiState.password,
                onValueChange = viewModel::onPasswordChanged,
                label = { Text("Password") },
                visualTransformation = if (uiState.isPasswordVisible) {
                    VisualTransformation.None
                } else {
                    PasswordVisualTransformation()
                },
                trailingIcon = {
                    IconButton(onClick = viewModel::onTogglePasswordVisibility) {
                        Icon(
                            imageVector = if (uiState.isPasswordVisible) {
                                Icons.Default.Visibility
                            } else {
                                Icons.Default.VisibilityOff
                            },
                            contentDescription = if (uiState.isPasswordVisible) {
                                "Hide password"
                            } else {
                                "Show password"
                            }
                        )
                    }
                },
                keyboardOptions = KeyboardOptions(
                    keyboardType = KeyboardType.Password,
                    imeAction = ImeAction.Done
                ),
                keyboardActions = KeyboardActions(
                    onDone = { viewModel.onSignIn() }
                ),
                singleLine = true,
                modifier = Modifier
                    .fillMaxWidth()
                    .testTag("password_field")
            )

            Spacer(modifier = Modifier.height(24.dp))

            // Sign In button
            Button(
                onClick = viewModel::onSignIn,
                enabled = uiState.isFormValid && !uiState.isLoading,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(52.dp)
            ) {
                if (uiState.isLoading) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(20.dp),
                        color = MaterialTheme.colorScheme.onPrimary,
                        strokeWidth = 2.dp
                    )
                } else {
                    Text("Sign In")
                }
            }
        }
    }

    // Error dialog
    uiState.generalError?.let { error ->
        AlertDialog(
            onDismissRequest = viewModel::onDismissError,
            confirmButton = {
                TextButton(onClick = viewModel::onDismissError) { Text("OK") }
            },
            title = { Text("Sign In Failed") },
            text = { Text(error) }
        )
    }
}
```

---

## Example 3: Post List with Pagination

### Model

```kotlin
// features/posts/model/Post.kt
import kotlinx.serialization.Serializable

@Serializable
data class Post(
    val id: String,
    val authorId: String,
    val title: String,
    val body: String,
    val createdAt: String,
    val likeCount: Int = 0
) {
    val preview: String
        get() = body.take(120).let { if (body.length > 120) "$it..." else it }
}

@Serializable
data class PostPage(
    val items: List<Post>,
    val nextCursor: String? = null,
    val totalCount: Int = 0
) {
    val hasMore: Boolean get() = nextCursor != null
}
```

### Repository

```kotlin
// features/posts/data/PostRepository.kt
interface PostRepository {
    suspend fun fetchPosts(cursor: String? = null, limit: Int = 20): Result<PostPage>
    suspend fun refreshPosts(): Result<PostPage>
}

// features/posts/data/PostRepositoryImpl.kt
import javax.inject.Inject

class PostRepositoryImpl @Inject constructor(
    private val apiService: ApiService
) : PostRepository {

    override suspend fun fetchPosts(cursor: String?, limit: Int): Result<PostPage> {
        return try {
            val response = apiService.getPosts(cursor = cursor, limit = limit)
            Result.success(response.toDomain())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun refreshPosts(): Result<PostPage> {
        return fetchPosts(cursor = null)
    }
}
```

### ViewModel

```kotlin
// features/posts/PostListViewModel.kt
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import javax.inject.Inject

sealed interface PostListUiState {
    data object Loading : PostListUiState
    data object Empty : PostListUiState
    data class Success(
        val posts: List<Post>,
        val isLoadingMore: Boolean = false,
        val hasMore: Boolean = false
    ) : PostListUiState
    data class Error(val message: String) : PostListUiState
}

@HiltViewModel
class PostListViewModel @Inject constructor(
    private val repository: PostRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<PostListUiState>(PostListUiState.Loading)
    val uiState: StateFlow<PostListUiState> = _uiState.asStateFlow()

    private var nextCursor: String? = null
    private var isLoadingMore = false

    init {
        loadPosts()
    }

    fun loadPosts() {
        viewModelScope.launch {
            _uiState.value = PostListUiState.Loading
            nextCursor = null

            repository.fetchPosts()
                .onSuccess { page ->
                    nextCursor = page.nextCursor
                    _uiState.value = if (page.items.isEmpty()) {
                        PostListUiState.Empty
                    } else {
                        PostListUiState.Success(
                            posts = page.items,
                            hasMore = page.hasMore
                        )
                    }
                }
                .onFailure { error ->
                    _uiState.value = PostListUiState.Error(error.message ?: "Failed to load posts")
                }
        }
    }

    fun loadMore() {
        val currentState = _uiState.value as? PostListUiState.Success ?: return
        if (isLoadingMore || !currentState.hasMore) return

        isLoadingMore = true
        _uiState.update { (it as PostListUiState.Success).copy(isLoadingMore = true) }

        viewModelScope.launch {
            repository.fetchPosts(cursor = nextCursor)
                .onSuccess { page ->
                    nextCursor = page.nextCursor
                    _uiState.update { state ->
                        val current = state as PostListUiState.Success
                        current.copy(
                            posts = current.posts + page.items,
                            isLoadingMore = false,
                            hasMore = page.hasMore
                        )
                    }
                }
                .onFailure {
                    _uiState.update { state ->
                        (state as PostListUiState.Success).copy(isLoadingMore = false)
                    }
                }
            isLoadingMore = false
        }
    }

    fun refresh() {
        loadPosts()
    }
}
```

### Composable

```kotlin
// features/posts/PostListScreen.kt
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.material3.*
import androidx.compose.material3.pulltorefresh.PullToRefreshBox
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle

@Composable
fun PostListScreen(
    onPostClick: (String) -> Unit = {},
    viewModel: PostListViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    val isRefreshing = uiState is PostListUiState.Loading

    Scaffold(
        topBar = {
            TopAppBar(title = { Text("Posts") })
        }
    ) { paddingValues ->
        PullToRefreshBox(
            isRefreshing = isRefreshing,
            onRefresh = viewModel::refresh,
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            when (val state = uiState) {
                is PostListUiState.Loading -> {
                    Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                        CircularProgressIndicator()
                    }
                }
                is PostListUiState.Empty -> {
                    Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                        Text(
                            text = "No posts yet",
                            style = MaterialTheme.typography.bodyLarge,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
                is PostListUiState.Success -> {
                    PostList(
                        state = state,
                        onPostClick = onPostClick,
                        onLoadMore = viewModel::loadMore
                    )
                }
                is PostListUiState.Error -> {
                    Column(
                        modifier = Modifier.fillMaxSize(),
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.Center
                    ) {
                        Text(
                            text = state.message,
                            color = MaterialTheme.colorScheme.error
                        )
                        Spacer(Modifier.height(16.dp))
                        Button(onClick = viewModel::loadPosts) {
                            Text("Retry")
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun PostList(
    state: PostListUiState.Success,
    onPostClick: (String) -> Unit,
    onLoadMore: () -> Unit
) {
    val listState = rememberLazyListState()

    LazyColumn(
        state = listState,
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        items(
            items = state.posts,
            key = { it.id }
        ) { post ->
            PostCard(
                post = post,
                onClick = { onPostClick(post.id) }
            )

            // Trigger load more when near end of list
            if (post == state.posts.last() && state.hasMore) {
                LaunchedEffect(post.id) {
                    onLoadMore()
                }
            }
        }

        if (state.isLoadingMore) {
            item {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator(modifier = Modifier.size(24.dp))
                }
            }
        }
    }
}

@Composable
private fun PostCard(
    post: Post,
    onClick: () -> Unit
) {
    Card(
        onClick = onClick,
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = post.title,
                style = MaterialTheme.typography.titleMedium
            )
            Spacer(Modifier.height(4.dp))
            Text(
                text = post.preview,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Spacer(Modifier.height(8.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = "${post.likeCount} likes",
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Text(
                    text = post.createdAt,
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}
```

---

## Example 4: Search with Debounce

### Model

```kotlin
// features/search/model/SearchResult.kt
import kotlinx.serialization.Serializable

@Serializable
data class SearchResult(
    val id: String,
    val title: String,
    val description: String,
    val type: String = "",
    val imageUrl: String? = null
)
```

### Repository

```kotlin
// features/search/data/SearchRepository.kt
interface SearchRepository {
    suspend fun search(query: String): Result<List<SearchResult>>
    suspend fun getRecentSearches(): List<String>
    suspend fun saveSearch(query: String)
}

// features/search/data/SearchRepositoryImpl.kt
import android.content.SharedPreferences
import androidx.core.content.edit
import javax.inject.Inject

class SearchRepositoryImpl @Inject constructor(
    private val apiService: ApiService,
    private val prefs: SharedPreferences
) : SearchRepository {

    override suspend fun search(query: String): Result<List<SearchResult>> {
        return try {
            val results = apiService.search(query = query.trim())
            Result.success(results.map { it.toDomain() })
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun getRecentSearches(): List<String> {
        val raw = prefs.getString("recent_searches", null) ?: return emptyList()
        return raw.split(",").filter { it.isNotEmpty() }.take(10)
    }

    override suspend fun saveSearch(query: String) {
        val recent = getRecentSearches().toMutableList()
        recent.remove(query)
        recent.add(0, query)
        prefs.edit { putString("recent_searches", recent.take(10).joinToString(",")) }
    }
}
```

### ViewModel

```kotlin
// features/search/SearchViewModel.kt
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import javax.inject.Inject

sealed interface SearchUiState {
    data object Idle : SearchUiState
    data object Searching : SearchUiState
    data class Results(
        val query: String,
        val items: List<SearchResult>
    ) : SearchUiState
    data object Empty : SearchUiState
    data class Error(val message: String) : SearchUiState
}

@HiltViewModel
class SearchViewModel @Inject constructor(
    private val repository: SearchRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<SearchUiState>(SearchUiState.Idle)
    val uiState: StateFlow<SearchUiState> = _uiState.asStateFlow()

    private val _query = MutableStateFlow("")
    val query: StateFlow<String> = _query.asStateFlow()

    private val _recentSearches = MutableStateFlow<List<String>>(emptyList())
    val recentSearches: StateFlow<List<String>> = _recentSearches.asStateFlow()

    private var searchJob: Job? = null

    init {
        loadRecentSearches()
    }

    fun onQueryChanged(query: String) {
        _query.value = query

        if (query.isBlank()) {
            searchJob?.cancel()
            _uiState.value = SearchUiState.Idle
            return
        }

        searchJob?.cancel()
        searchJob = viewModelScope.launch {
            _uiState.value = SearchUiState.Searching
            delay(300) // debounce

            repository.search(query)
                .onSuccess { results ->
                    _uiState.value = if (results.isEmpty()) {
                        SearchUiState.Empty
                    } else {
                        SearchUiState.Results(query = query, items = results)
                    }
                }
                .onFailure { error ->
                    _uiState.value = SearchUiState.Error(error.message ?: "Search failed")
                }
        }
    }

    fun onClearQuery() {
        _query.value = ""
        _uiState.value = SearchUiState.Idle
        searchJob?.cancel()
    }

    fun onResultSelected(result: SearchResult) {
        viewModelScope.launch {
            repository.saveSearch(_query.value)
            loadRecentSearches()
        }
    }

    private fun loadRecentSearches() {
        viewModelScope.launch {
            _recentSearches.value = repository.getRecentSearches()
        }
    }
}
```

### Composable

```kotlin
// features/search/SearchScreen.kt
import androidx.compose.animation.AnimatedContent
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.History
import androidx.compose.material.icons.filled.Search
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SearchScreen(
    onResultSelected: (SearchResult) -> Unit = {},
    viewModel: SearchViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    val query by viewModel.query.collectAsStateWithLifecycle()
    val recentSearches by viewModel.recentSearches.collectAsStateWithLifecycle()

    Scaffold(
        topBar = {
            SearchBar(
                query = query,
                onQueryChange = viewModel::onQueryChanged,
                onSearch = {},
                active = false,
                onActiveChange = {},
                leadingIcon = { Icon(Icons.Default.Search, contentDescription = null) },
                trailingIcon = {
                    if (query.isNotEmpty()) {
                        IconButton(onClick = viewModel::onClearQuery) {
                            Icon(Icons.Default.Close, contentDescription = "Clear search")
                        }
                    }
                },
                placeholder = { Text("Search...") },
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 8.dp)
                    .testTag("search_bar")
            ) {}
        }
    ) { paddingValues ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            AnimatedContent(
                targetState = uiState,
                label = "search_state"
            ) { state ->
                when (state) {
                    is SearchUiState.Idle -> {
                        if (recentSearches.isNotEmpty()) {
                            RecentSearchesList(
                                searches = recentSearches,
                                onSearchSelected = viewModel::onQueryChanged
                            )
                        }
                    }
                    is SearchUiState.Searching -> {
                        Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                            CircularProgressIndicator()
                        }
                    }
                    is SearchUiState.Results -> {
                        SearchResultsList(
                            results = state.items,
                            onResultSelected = { result ->
                                viewModel.onResultSelected(result)
                                onResultSelected(result)
                            }
                        )
                    }
                    is SearchUiState.Empty -> {
                        Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                Icon(
                                    imageVector = Icons.Default.Search,
                                    contentDescription = null,
                                    modifier = Modifier.size(48.dp),
                                    tint = MaterialTheme.colorScheme.onSurfaceVariant
                                )
                                Spacer(Modifier.height(8.dp))
                                Text(
                                    text = "No results for \"${query}\"",
                                    style = MaterialTheme.typography.bodyLarge,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant
                                )
                            }
                        }
                    }
                    is SearchUiState.Error -> {
                        Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                            Text(
                                text = state.message,
                                color = MaterialTheme.colorScheme.error,
                                style = MaterialTheme.typography.bodyMedium
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun RecentSearchesList(
    searches: List<String>,
    onSearchSelected: (String) -> Unit
) {
    LazyColumn {
        item {
            Text(
                text = "Recent Searches",
                style = MaterialTheme.typography.labelLarge,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.padding(horizontal = 16.dp, vertical = 12.dp)
            )
        }
        items(searches) { query ->
            ListItem(
                headlineContent = { Text(query) },
                leadingContent = {
                    Icon(
                        Icons.Default.History,
                        contentDescription = null,
                        tint = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                },
                modifier = Modifier.clickable { onSearchSelected(query) }
            )
        }
    }
}

@Composable
private fun SearchResultsList(
    results: List<SearchResult>,
    onResultSelected: (SearchResult) -> Unit
) {
    LazyColumn(
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        items(results, key = { it.id }) { result ->
            SearchResultCard(result = result, onClick = { onResultSelected(result) })
        }
    }
}

@Composable
private fun SearchResultCard(
    result: SearchResult,
    onClick: () -> Unit
) {
    Card(
        onClick = onClick,
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = result.title,
                style = MaterialTheme.typography.titleSmall
            )
            Spacer(Modifier.height(4.dp))
            Text(
                text = result.description,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}
```
