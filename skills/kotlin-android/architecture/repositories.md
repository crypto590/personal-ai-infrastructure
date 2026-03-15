# Repositories

**Part of:** [kotlin-android](../SKILL.md) > Architecture

**Related:**
- [viewmodels.md](viewmodels.md) - ViewModels that use Repositories
- [models.md](models.md) - Models that Repositories return
- [error-handling.md](error-handling.md) - Error handling in Repositories

---

## Overview

Repositories are the data layer. They handle async operations like network calls, database queries, and caching. Repositories are always interface-based for testability and follow the offline-first pattern when applicable.

**Key characteristics:**
- Always define an interface + implementation
- Return `Result<T>` or `Flow<T>` for reactive data
- No UI state — stateless operations (caching is acceptable)
- Return domain Models, never ViewModels or UI state
- No `@MainActor` — background execution only
- Never import Compose-specific classes

---

## File Organization

- **One repository per domain area, always.** Each repository has its own interface and implementation. 1:1 makes testing and discovery clean.
- Name files after the interface: `UserRepository` → `UserRepository.kt`, implementation in `UserRepositoryImpl.kt`
- Include the interface in a separate file or the same file as the implementation for small repositories.
- Place repositories in the same feature folder as the ViewModel that uses them, or in a shared `data/` folder for cross-feature data.

---

## Interface-Based Design

### Always Define Interface + Implementation

```kotlin
// Interface (in UserRepository.kt)
interface UserRepository {
    suspend fun fetchUser(id: String): Result<User>
    suspend fun updateUser(user: User): Result<User>
    suspend fun deleteUser(id: String): Result<Unit>
    fun observeUser(id: String): Flow<User?>
}

// Implementation (in UserRepositoryImpl.kt)
class UserRepositoryImpl @Inject constructor(
    private val remoteDataSource: UserRemoteDataSource,
    private val localDataSource: UserLocalDataSource
) : UserRepository {

    override suspend fun fetchUser(id: String): Result<User> {
        return try {
            val dto = remoteDataSource.getUser(id)
            val user = dto.toDomain()
            localDataSource.saveUser(user.toEntity())
            Result.success(user)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun updateUser(user: User): Result<User> {
        return try {
            val dto = remoteDataSource.updateUser(user.id, user.toDto())
            Result.success(dto.toDomain())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun deleteUser(id: String): Result<Unit> {
        return try {
            remoteDataSource.deleteUser(id)
            localDataSource.deleteUser(id)
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override fun observeUser(id: String): Flow<User?> =
        localDataSource.observeUser(id).map { it?.toDomain() }
}
```

---

## Repository vs DataSource Distinction

Repositories orchestrate one or more DataSources. DataSources handle a single data source type (network, database, cache).

```
Repository
├── RemoteDataSource  (Retrofit API calls)
├── LocalDataSource   (Room DAO calls)
└── CacheDataSource   (in-memory cache)
```

**Repository** — orchestrates, applies business rules, handles offline-first logic
**DataSource** — thin wrapper around a single source (API, DB, cache)

---

## Network Data Source (Retrofit)

```kotlin
interface UserRemoteDataSource {
    suspend fun getUser(id: String): UserDto
    suspend fun updateUser(id: String, body: UpdateUserRequest): UserDto
    suspend fun deleteUser(id: String)
}

class UserRemoteDataSourceImpl @Inject constructor(
    private val api: UserApi
) : UserRemoteDataSource {

    override suspend fun getUser(id: String): UserDto = api.getUser(id)

    override suspend fun updateUser(id: String, body: UpdateUserRequest): UserDto =
        api.updateUser(id, body)

    override suspend fun deleteUser(id: String) = api.deleteUser(id)
}

// Retrofit API interface
interface UserApi {
    @GET("users/{id}")
    suspend fun getUser(@Path("id") id: String): UserDto

    @PUT("users/{id}")
    suspend fun updateUser(
        @Path("id") id: String,
        @Body body: UpdateUserRequest
    ): UserDto

    @DELETE("users/{id}")
    suspend fun deleteUser(@Path("id") id: String)
}
```

---

## Local Data Source (Room DAO)

```kotlin
// DAO
@Dao
interface UserDao {
    @Query("SELECT * FROM users WHERE id = :id")
    fun observeUser(id: String): Flow<UserEntity?>

    @Query("SELECT * FROM users")
    fun observeAllUsers(): Flow<List<UserEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUser(user: UserEntity)

    @Update
    suspend fun updateUser(user: UserEntity)

    @Query("DELETE FROM users WHERE id = :id")
    suspend fun deleteUser(id: String)
}

// Local DataSource wrapping the DAO
interface UserLocalDataSource {
    fun observeUser(id: String): Flow<UserEntity?>
    fun observeAllUsers(): Flow<List<UserEntity>>
    suspend fun saveUser(user: UserEntity)
    suspend fun deleteUser(id: String)
}

class UserLocalDataSourceImpl @Inject constructor(
    private val dao: UserDao
) : UserLocalDataSource {

    override fun observeUser(id: String): Flow<UserEntity?> = dao.observeUser(id)

    override fun observeAllUsers(): Flow<List<UserEntity>> = dao.observeAllUsers()

    override suspend fun saveUser(user: UserEntity) = dao.insertUser(user)

    override suspend fun deleteUser(id: String) = dao.deleteUser(id)
}
```

---

## Repository Implementation: Offline-First Pattern

The offline-first pattern shows cached data immediately, then refreshes from network:

```kotlin
class ArticleRepositoryImpl @Inject constructor(
    private val remoteDataSource: ArticleRemoteDataSource,
    private val localDataSource: ArticleLocalDataSource
) : ArticleRepository {

    // Offline-first: emit local data, then refresh from network
    override fun observeArticles(): Flow<List<Article>> = flow {
        // 1. Emit cached data immediately
        val cached = localDataSource.getAllArticles().first()
        if (cached.isNotEmpty()) {
            emit(cached.map { it.toDomain() })
        }

        // 2. Fetch from network and update cache
        try {
            val dtos = remoteDataSource.getArticles()
            val entities = dtos.map { it.toEntity() }
            localDataSource.replaceAll(entities)
        } catch (e: Exception) {
            // Network failed — cached data was already emitted
        }
    }.flatMapLatest {
        // 3. Continue observing local DB (Room will emit updates)
        localDataSource.getAllArticles().map { entities ->
            entities.map { it.toDomain() }
        }
    }

    // Network-first for single item fetch
    override suspend fun fetchArticle(id: String): Result<Article> {
        return try {
            val dto = remoteDataSource.getArticle(id)
            val entity = dto.toEntity()
            localDataSource.saveArticle(entity)
            Result.success(dto.toDomain())
        } catch (e: Exception) {
            // Fall back to cached data
            val cached = localDataSource.getArticle(id)
            if (cached != null) {
                Result.success(cached.toDomain())
            } else {
                Result.failure(e)
            }
        }
    }
}
```

---

## Hilt Module: Binding Interface to Implementation

```kotlin
@Module
@InstallIn(SingletonComponent::class)
abstract class DataModule {

    // Repositories
    @Binds
    @Singleton
    abstract fun bindUserRepository(impl: UserRepositoryImpl): UserRepository

    @Binds
    @Singleton
    abstract fun bindArticleRepository(impl: ArticleRepositoryImpl): ArticleRepository

    // DataSources
    @Binds
    @Singleton
    abstract fun bindUserRemoteDataSource(impl: UserRemoteDataSourceImpl): UserRemoteDataSource

    @Binds
    @Singleton
    abstract fun bindUserLocalDataSource(impl: UserLocalDataSourceImpl): UserLocalDataSource
}

@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideRetrofit(): Retrofit = Retrofit.Builder()
        .baseUrl("https://api.example.com/")
        .addConverterFactory(kotlinx.serialization.json.Json.asConverterFactory(
            "application/json".toMediaType()
        ))
        .build()

    @Provides
    @Singleton
    fun provideUserApi(retrofit: Retrofit): UserApi =
        retrofit.create(UserApi::class.java)
}

@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {

    @Provides
    @Singleton
    fun provideDatabase(@ApplicationContext context: Context): AppDatabase =
        Room.databaseBuilder(context, AppDatabase::class.java, "app_database")
            .fallbackToDestructiveMigration()
            .build()

    @Provides
    fun provideUserDao(db: AppDatabase): UserDao = db.userDao()
}
```

---

## Caching Strategies

### In-Memory Cache

```kotlin
class PostRepositoryImpl @Inject constructor(
    private val remoteDataSource: PostRemoteDataSource,
    private val localDataSource: PostLocalDataSource
) : PostRepository {

    // Simple in-memory cache with expiry
    private var cacheTimestamp: Long = 0
    private val cacheDuration = 5 * 60 * 1000L // 5 minutes

    private fun isCacheValid(): Boolean =
        System.currentTimeMillis() - cacheTimestamp < cacheDuration

    override suspend fun getPosts(): Result<List<Post>> {
        // Return from DB if cache is fresh
        if (isCacheValid()) {
            val cached = localDataSource.getAllPosts().first()
            if (cached.isNotEmpty()) {
                return Result.success(cached.map { it.toDomain() })
            }
        }

        return try {
            val dtos = remoteDataSource.getPosts()
            localDataSource.replaceAll(dtos.map { it.toEntity() })
            cacheTimestamp = System.currentTimeMillis()
            Result.success(dtos.map { it.toDomain() })
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun invalidateCache() {
        cacheTimestamp = 0
    }
}
```

### Room as the Single Source of Truth

```kotlin
class NewsRepositoryImpl @Inject constructor(
    private val api: NewsApi,
    private val dao: NewsDao
) : NewsRepository {

    // Room is the single source of truth
    // Network writes to Room, UI reads from Room
    override fun getLatestNews(): Flow<List<Article>> = dao.observeArticles()
        .map { entities -> entities.map { it.toDomain() } }

    override suspend fun refreshNews(): Result<Unit> {
        return try {
            val articles = api.getLatestNews()
            dao.replaceAll(articles.map { it.toEntity() })
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

---

## Error Handling with Result Type

```kotlin
// Repository wraps exceptions in Result.failure
class ProductRepositoryImpl @Inject constructor(
    private val api: ProductApi
) : ProductRepository {

    override suspend fun getProduct(id: String): Result<Product> {
        return try {
            val dto = api.getProduct(id)
            Result.success(dto.toDomain())
        } catch (e: HttpException) {
            when (e.code()) {
                401 -> Result.failure(AppError.Unauthorized)
                404 -> Result.failure(AppError.NotFound("Product not found"))
                in 500..599 -> Result.failure(AppError.ServerError(e.code()))
                else -> Result.failure(AppError.Unknown(e.message()))
            }
        } catch (e: IOException) {
            Result.failure(AppError.NetworkUnavailable)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

---

## Flow Emissions for Reactive Data

```kotlin
interface MessageRepository {
    fun observeMessages(conversationId: String): Flow<List<Message>>
    suspend fun sendMessage(conversationId: String, text: String): Result<Message>
}

class MessageRepositoryImpl @Inject constructor(
    private val dao: MessageDao,
    private val api: MessageApi,
    private val socketService: WebSocketService
) : MessageRepository {

    // Cold Flow from Room — emits whenever DB changes
    override fun observeMessages(conversationId: String): Flow<List<Message>> =
        dao.observeMessages(conversationId)
            .map { entities -> entities.map { it.toDomain() } }
            .distinctUntilChanged()

    override suspend fun sendMessage(conversationId: String, text: String): Result<Message> {
        return try {
            val dto = api.sendMessage(conversationId, SendMessageRequest(text))
            val message = dto.toDomain()
            dao.insertMessage(message.toEntity())
            Result.success(message)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

---

## Testing with Fake Repositories

```kotlin
// Fake repository for testing (in test source set)
class FakeUserRepository : UserRepository {
    var shouldFail = false
    var networkDelay = 0L

    private val users = mutableMapOf<String, User>()
    private val userFlow = MutableStateFlow<List<User>>(emptyList())

    fun seedUser(user: User) {
        users[user.id] = user
        userFlow.value = users.values.toList()
    }

    override suspend fun fetchUser(id: String): Result<User> {
        if (networkDelay > 0) delay(networkDelay)
        return if (shouldFail) {
            Result.failure(IOException("Network error"))
        } else {
            users[id]?.let { Result.success(it) }
                ?: Result.failure(Exception("User not found"))
        }
    }

    override suspend fun updateUser(user: User): Result<User> {
        if (shouldFail) return Result.failure(IOException("Network error"))
        users[user.id] = user
        userFlow.value = users.values.toList()
        return Result.success(user)
    }

    override fun observeUser(id: String): Flow<User?> =
        userFlow.map { it.find { u -> u.id == id } }
}

// ViewModel test using fake
class UserViewModelTest {
    private val fakeRepo = FakeUserRepository()
    private val viewModel = UserViewModel(repository = fakeRepo)

    @Before
    fun setup() {
        fakeRepo.seedUser(User(id = "1", name = "Alice", email = "alice@example.com"))
    }

    @Test
    fun `fetchUser success sets Success state`() = runTest {
        viewModel.loadUser("1")
        advanceUntilIdle()

        val state = viewModel.uiState.value
        assertIs<UserUiState.Success>(state)
        assertEquals("Alice", state.user.name)
    }

    @Test
    fun `fetchUser failure sets Error state`() = runTest {
        fakeRepo.shouldFail = true
        viewModel.loadUser("1")
        advanceUntilIdle()

        assertIs<UserUiState.Error>(viewModel.uiState.value)
    }
}
```

---

## Repository Rules

### DO

**1. Always define an interface**
```kotlin
// GOOD
interface UserRepository { suspend fun fetchUser(id: String): Result<User> }
class UserRepositoryImpl : UserRepository { ... }

// BAD — not testable
class UserRepository { suspend fun fetchUser(id: String): Result<User> { ... } }
```

**2. Return Result<T> for operations that can fail**
```kotlin
// GOOD
suspend fun fetchUser(id: String): Result<User>

// BAD — forces caller to handle exceptions
suspend fun fetchUser(id: String): User
```

**3. Return Flow<T> for reactive / observable data**
```kotlin
// GOOD — Room Flow emits on every DB change
fun observeUsers(): Flow<List<User>>

// BAD for reactive data — only fetches once
suspend fun getUsers(): List<User>
```

**4. Keep repositories focused per domain**
```kotlin
// GOOD — focused
interface UserRepository { suspend fun fetchUser(id: String): Result<User> }
interface PostRepository { suspend fun fetchPosts(userId: String): Result<List<Post>> }

// BAD — too broad
interface DataRepository {
    suspend fun fetchUser(id: String): Result<User>
    suspend fun fetchPosts(userId: String): Result<List<Post>>
    suspend fun fetchComments(postId: String): Result<List<Comment>>
}
```

**5. Map exceptions to domain errors at the repository boundary**
```kotlin
// GOOD — ViewModel receives clean AppError
override suspend fun fetchUser(id: String): Result<User> = try {
    Result.success(api.getUser(id).toDomain())
} catch (e: HttpException) {
    Result.failure(AppError.from(e))
} catch (e: IOException) {
    Result.failure(AppError.NetworkUnavailable)
}
```

### DON'T

**1. Never store UI state in repositories**
```kotlin
// BAD
class UserRepositoryImpl : UserRepository {
    var isLoading = false  // UI state belongs in ViewModel!
}
```

**2. Never return ViewModels or Composables**
```kotlin
// BAD
suspend fun fetchUser(id: String): UserViewModel

// GOOD
suspend fun fetchUser(id: String): Result<User>
```

**3. Never use @MainActor in repositories**
```kotlin
// BAD
@MainActor
class UserRepositoryImpl : UserRepository

// GOOD — background execution
class UserRepositoryImpl : UserRepository
```

**4. Never import Compose in repositories**
```kotlin
// BAD
import androidx.compose.runtime.State
class UserRepositoryImpl : UserRepository {
    val userState: State<User?> = ...
}
```

**5. Never call repositories from Composables directly**
```kotlin
// BAD — in Composable
val userRepo = hiltViewModel<SomeViewModel>().repo  // Wrong!

// GOOD — always through ViewModel
val uiState by viewModel.uiState.collectAsStateWithLifecycle()
```
