# Models (Data Classes)

**Part of:** [kotlin-android](../SKILL.md) > Architecture

**Related:**
- [repositories.md](repositories.md) - Repositories that return Models
- [viewmodels.md](viewmodels.md) - ViewModels that use Models

---

## Overview

Models are immutable data structures with computed properties for business logic. They represent the core domain entities of your application.

**Key characteristics:**
- Always `data class`, never regular `class`
- Always immutable (`val` properties only)
- No `suspend` functions or coroutines
- No `MutableStateFlow`, `LiveData`, or ViewModel references
- Business logic in computed properties (custom getters)
- Conform to `@Serializable` or use custom serialization

---

## File Organization

- **Group by cohesion, not by count.** Related types that always travel together can share a file (e.g., `PipelineModels.kt` for `PipelineAthlete`, `PipelineStage`, `PipelineSummary`).
- A single substantial type gets its own file: `UserProfile` → `UserProfile.kt`
- Avoid grab-bag model files — if the types are unrelated, split them into separate files.
- **Test:** if you change one type, do you always change the others? If yes, they belong together. If no, separate files.
- Place models in the same feature folder as the ViewModel and repository that use them.

---

## Rules

### Always

**1. Use data class**
```kotlin
// GOOD
data class User(val id: String, val name: String, val email: String)

// BAD
class User(val id: String, val name: String, val email: String)
```

**2. Use val only (immutable properties)**
```kotlin
// GOOD
data class Product(val id: String, val price: Double, val stock: Int)

// BAD
data class Product(var id: String, var price: Double, var stock: Int)
```

**3. Use computed properties for derived logic**
```kotlin
data class Order(
    val items: List<OrderItem>,
    val taxRate: Double
) {
    val subtotal: Double
        get() = items.sumOf { it.price * it.quantity }

    val tax: Double
        get() = subtotal * taxRate

    val total: Double
        get() = subtotal + tax

    val isEmpty: Boolean
        get() = items.isEmpty()
}
```

### Never

**1. Never use suspend functions in models**
```kotlin
// BAD
data class User(val id: String) {
    suspend fun loadProfile(): Profile { /* ... */ }
}

// GOOD - put in Repository
interface UserRepository {
    suspend fun fetchProfile(userId: String): Result<Profile>
}
```

**2. Never store mutable UI state in models**
```kotlin
// BAD
data class User(
    val id: String,
    var isLoading: Boolean = false  // UI state!
)

// GOOD - put in ViewModel
sealed interface UserUiState {
    data object Loading : UserUiState
    data class Success(val user: User) : UserUiState
}
```

**3. Never reference ViewModels or Context**
```kotlin
// BAD
data class Article(
    val id: String,
    val viewModel: ArticleViewModel  // Wrong!
)

// GOOD
data class Article(val id: String, val title: String, val body: String)
```

---

## Patterns

### Basic Domain Model

```kotlin
data class User(
    val id: String,
    val name: String,
    val email: String,
    val avatarUrl: String?,
    val createdAt: Long  // Unix timestamp
) {
    val displayName: String
        get() = name.ifBlank { email }

    val initials: String
        get() = name.split(" ")
            .take(2)
            .mapNotNull { it.firstOrNull()?.uppercaseChar() }
            .joinToString("")

    val hasAvatar: Boolean
        get() = avatarUrl != null
}
```

### Nested Types

```kotlin
data class User(
    val id: String,
    val name: String,
    val address: Address
) {
    data class Address(
        val street: String,
        val city: String,
        val state: String,
        val zip: String
    ) {
        val formatted: String
            get() = "$street, $city, $state $zip"
    }
}
```

### Sealed Class for Domain State

```kotlin
data class Order(
    val id: String,
    val items: List<OrderItem>,
    val status: Status
) {
    sealed class Status {
        data object Pending : Status()
        data object Processing : Status()
        data class Shipped(val trackingNumber: String) : Status()
        data object Delivered : Status()
        data class Cancelled(val reason: String) : Status()
    }

    val canCancel: Boolean
        get() = status is Status.Pending || status is Status.Processing

    val isActive: Boolean
        get() = status !is Status.Delivered && status !is Status.Cancelled
}
```

### Collections with Computed Properties

```kotlin
data class Team(
    val id: String,
    val name: String,
    val members: List<User>
) {
    val memberCount: Int
        get() = members.size

    val isEmpty: Boolean
        get() = members.isEmpty()

    fun isMember(userId: String): Boolean =
        members.any { it.id == userId }

    fun getMember(userId: String): User? =
        members.find { it.id == userId }
}
```

---

## Sealed Classes for UI State

Define UI states as sealed interfaces in the same file as the ViewModel or in a dedicated UiState file:

```kotlin
// Feature-level UI state
sealed interface ProductUiState {
    data object Loading : ProductUiState
    data class Success(val product: Product) : ProductUiState
    data class Error(val message: String) : ProductUiState
}

// Generic reusable UI state
sealed interface UiState<out T> {
    data object Loading : UiState<Nothing>
    data class Success<T>(val data: T) : UiState<T>
    data class Error(val message: String) : UiState<Nothing>
    data object Empty : UiState<Nothing>
}
```

---

## Room Entity Patterns

Room entity classes add database annotations but remain data classes:

```kotlin
@Entity(tableName = "users")
data class UserEntity(
    @PrimaryKey val id: String,
    @ColumnInfo(name = "display_name") val name: String,
    val email: String,
    @ColumnInfo(name = "avatar_url") val avatarUrl: String?,
    @ColumnInfo(name = "created_at") val createdAt: Long
)

// Separate domain model from entity
data class User(
    val id: String,
    val name: String,
    val email: String,
    val avatarUrl: String?,
    val createdAt: Long
)

// Mapping extension functions
fun UserEntity.toDomain(): User = User(
    id = id, name = name, email = email,
    avatarUrl = avatarUrl, createdAt = createdAt
)

fun User.toEntity(): UserEntity = UserEntity(
    id = id, name = name, email = email,
    avatarUrl = avatarUrl, createdAt = createdAt
)
```

### Room with Relationships

```kotlin
data class PostWithAuthor(
    @Embedded val post: PostEntity,
    @Relation(
        parentColumn = "author_id",
        entityColumn = "id"
    )
    val author: UserEntity
)
```

---

## Retrofit/API Response Models

Keep API DTOs separate from domain models:

```kotlin
// API DTO (matches JSON structure)
@Serializable
data class UserDto(
    val id: String,
    val name: String,
    val email: String,
    @SerialName("avatar_url") val avatarUrl: String? = null,
    @SerialName("created_at") val createdAt: Long
)

// Generic paginated response
@Serializable
data class PagedResponse<T>(
    val data: List<T>,
    val meta: Meta
) {
    @Serializable
    data class Meta(
        val page: Int,
        @SerialName("total_pages") val totalPages: Int,
        @SerialName("total_count") val totalCount: Int
    ) {
        val hasMore: Boolean
            get() = page < totalPages
    }
}

// Mapping DTO to domain
fun UserDto.toDomain(): User = User(
    id = id,
    name = name,
    email = email,
    avatarUrl = avatarUrl,
    createdAt = createdAt
)
```

---

## Parcelable with @Parcelize

Use `@Parcelize` for models passed between Activities or Fragments (less common with Navigation Compose, but still useful for Intent extras):

```kotlin
@Parcelize
data class EventSummary(
    val id: String,
    val title: String,
    val date: Long
) : Parcelable
```

Add to `build.gradle.kts`:
```kotlin
plugins {
    id("kotlin-parcelize")
}
```

---

## Kotlin Serialization vs Moshi vs Gson

**Recommendation: Kotlin Serialization (kotlinx.serialization)**

```kotlin
// Add to build.gradle.kts
plugins {
    kotlin("plugin.serialization")
}
dependencies {
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.7.x")
}
```

**Kotlin Serialization** (preferred):
```kotlin
@Serializable
data class Article(
    val id: String,
    val title: String,
    @SerialName("body_text") val body: String,
    val tags: List<String> = emptyList()
)
```

**Moshi** (acceptable for Retrofit-only projects):
```kotlin
@JsonClass(generateAdapter = true)
data class Article(
    val id: String,
    val title: String,
    @Json(name = "body_text") val body: String
)
```

**Gson** (avoid for new code — no null safety, reflection-based):
```kotlin
// AVOID in new code
data class Article(
    val id: String,   // Gson uses reflection, no null-safety guarantees
    val title: String
)
```

**Decision guide:**
- New project: Kotlin Serialization
- Existing Retrofit + Moshi project: Keep Moshi
- Legacy Gson: Migrate to Kotlin Serialization when convenient
- Multiplatform (KMP): Kotlin Serialization only

---

## ProGuard Rules for Release Builds

When using Kotlin Serialization, add to `proguard-rules.pro`:

```
# Kotlin Serialization
-keepattributes *Annotation*, InnerClasses
-dontnote kotlinx.serialization.AnnotationsKt
-keepclassmembers class kotlinx.serialization.json.** {
    *** Companion;
}
-keepclasseswithmembers class **$$serializer {
    kotlinx.serialization.descriptors.SerialDescriptor descriptor;
}
-keepclassmembers @kotlinx.serialization.Serializable class ** {
    *** Companion;
    *** INSTANCE;
    kotlinx.serialization.KSerializer serializer(...);
}
```

---

## Example Models

### User Profile

```kotlin
data class UserProfile(
    val id: String,
    val username: String,
    val displayName: String,
    val email: String,
    val bio: String?,
    val avatarUrl: String?,
    val followerCount: Int,
    val followingCount: Int,
    val isVerified: Boolean,
    val createdAt: Long
) {
    val hasBio: Boolean
        get() = !bio.isNullOrBlank()

    val formattedFollowers: String
        get() = when {
            followerCount >= 1_000_000 -> "${followerCount / 1_000_000}M"
            followerCount >= 1_000 -> "${followerCount / 1_000}K"
            else -> followerCount.toString()
        }
}
```

### Post

```kotlin
data class Post(
    val id: String,
    val authorId: String,
    val title: String,
    val body: String,
    val imageUrl: String?,
    val likeCount: Int,
    val commentCount: Int,
    val isLiked: Boolean,
    val publishedAt: Long
) {
    val preview: String
        get() = body.take(120).let {
            if (body.length > 120) "$it..." else it
        }

    val hasImage: Boolean
        get() = imageUrl != null
}
```

### API Response Wrapper

```kotlin
@Serializable
data class ApiResponse<T>(
    val success: Boolean,
    val data: T? = null,
    val error: ApiError? = null
) {
    @Serializable
    data class ApiError(
        val code: String,
        val message: String
    )
}

typealias UserListResponse = ApiResponse<List<UserDto>>
typealias UserResponse = ApiResponse<UserDto>
```
