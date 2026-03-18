# Kotlin Review Checklist

Apply this checklist to all changed `.kt` and `.kts` files. This workflow orchestrates the existing kotlin-android review checklists — read and apply each referenced file rather than duplicating their content.

## How to Use

Read and apply each referenced checklist below to the changed Kotlin files. Each checklist file contains detailed rules and examples specific to its domain.

## Checklists

### Concurrency
Read and apply: `kotlin-android/review/concurrency.md`

Key areas covered:
- Coroutine scope management (viewModelScope, lifecycleScope, proper custom scopes)
- Flow collection in lifecycle (using `repeatOnLifecycle` or `collectAsStateWithLifecycle`)
- StateFlow vs SharedFlow usage and appropriate replay/buffer configuration
- Dispatchers usage (Main for UI, IO for network/disk, Default for CPU-intensive)
- Structured concurrency and cancellation propagation
- SupervisorJob usage for independent child failure

### Pattern Validation
Read and apply: `kotlin-android/review/pattern-validation.md`

Key areas covered:
- MVVM architecture compliance (ViewModels, Repositories, Models, Composables)
- Repository pattern and proper data layer abstraction
- Dependency injection with Hilt (module organization, scope correctness)
- Unidirectional data flow (state down, events up)
- Use case / interactor layer when needed

### Accessibility
Read and apply: `kotlin-android/review/accessibility.md`

Key areas covered:
- TalkBack content descriptions on all interactive and meaningful elements
- Touch target sizes (48dp minimum for all interactive elements)
- Content descriptions on images and icons (`contentDescription` parameter)
- Semantic properties in Compose (`semantics` modifier)
- Focus order and traversal for custom layouts

### Material Design 3
Read and apply: `kotlin-android/review/material-design-review.md`

Key areas covered:
- Dynamic color usage (`dynamicDarkColorScheme` / `dynamicLightColorScheme`)
- Color roles applied correctly (primary, secondary, tertiary, surface variants)
- Typography scale compliance (using `MaterialTheme.typography` tokens, not custom text styles)
- Component theming consistency with Material 3 spec
- Proper elevation and surface tonal color usage
