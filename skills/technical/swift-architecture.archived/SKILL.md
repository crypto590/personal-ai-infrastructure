---
name: swift-architecture
description: "[ARCHIVED - use swift-mvc instead] Progressive architecture for Swift/SwiftUI apps that scales with complexity. Start simple with @State, add ViewModels for logic, extract Services when shared. NOT for new projects - superseded by swift-mvc skill."
metadata:
  author: coreyyoung
  version: 1.0.0
  category: technical
  tags: [swift, swiftui, architecture, progressive, solid, archived]
---

# Swift Architecture

**Category:** technical

**Brief Description:** Progressive architecture approach for Swift/SwiftUI that starts simple and scales with complexity. Use Level 1 (@State) for simple UI, Level 2 (ViewModels) for business logic, Level 3 (Services) for shared functionality. Integrates SOLID principles throughout.

---

## When to Use This Skill

Trigger this skill when:
- Building iOS/macOS/watchOS apps with SwiftUI
- Making architectural decisions for Swift projects
- Asking "where should this logic live?"
- Organizing Swift code or file structure
- User mentions MVVM, architecture patterns, or app structure
- Reviewing Swift code for architectural patterns
- Refactoring existing Swift/SwiftUI code
- Deciding between @State, ViewModel, or Service
- Questions about ViewModels, Services, or SOLID principles
- Setting up dependency injection in Swift

---

## Core Principle

**Scale architecture with feature complexity**. Start with the simplest solution and add architectural layers only when complexity demands it. This prevents over-engineering while maintaining clean, testable code.

---

## Three-Level Architecture

### Quick Overview

**Level 1: Simple Views with @State**
- Use when: View has only local UI state, no business logic
- Pattern: State lives directly in SwiftUI view
- Example: Settings toggles, tab selection, simple forms

**Level 2: Views with ViewModels**
- Use when: Need API calls, validation, or complex logic
- Pattern: `@Observable` ViewModel handles logic, View handles UI
- Example: Profile loading, form validation, data fetching

**Level 3: Shared Services**
- Use when: Logic needed across multiple ViewModels
- Pattern: Extract to service that ViewModels depend on
- Example: Authentication, networking, data persistence

### Decision Tree

```
Does the view only display/update simple local state?
├─ YES → Level 1: @State in view
└─ NO → Does it need API calls, validation, or complex logic?
    ├─ YES → Level 2: Add ViewModel
    └─ Is this logic shared across multiple features?
        ├─ YES → Level 3: Extract to Service
        └─ NO → Keep in ViewModel
```

---

## SOLID Principles Integration

This architecture embeds SOLID principles at every level:

- **Single Responsibility**: Each ViewModel/Service has one clear purpose
- **Open/Closed**: Use protocols for extensibility without modification
- **Liskov Substitution**: Protocols ensure consistent behavior
- **Interface Segregation**: Small, focused protocols
- **Dependency Inversion**: Always inject dependencies via protocols

See [SOLID_PRINCIPLES.md](SOLID_PRINCIPLES.md) for comprehensive examples.

---

## Detailed Documentation

### Architecture Implementation
- **Complete architecture guide**: [ARCHITECTURE_LEVELS.md](ARCHITECTURE_LEVELS.md)
  - Detailed Level 1, 2, 3 patterns
  - File organization strategies
  - When to refactor between levels
  - Testing strategies per level
  - Anti-patterns to avoid

### Specialized Topics
- **ViewModel patterns**: [VIEWMODEL_PATTERNS.md](VIEWMODEL_PATTERNS.md)
  - State management strategies
  - Error handling patterns
  - Validation approaches
  - Pagination, search, and common patterns
  - ViewModel testing

- **Service layer**: [SERVICE_LAYER.md](SERVICE_LAYER.md)
  - Common service types (Auth, Network, Persistence)
  - Dependency injection strategies
  - Protocol-based design
  - Service testing and mocking
  - Caching strategies

- **SOLID principles**: [SOLID_PRINCIPLES.md](SOLID_PRINCIPLES.md)
  - Each principle explained with Swift examples
  - Good vs bad implementations
  - Real-world applications
  - How principles combine

### Practical Resources
- **Real-world examples**: [EXAMPLES.md](EXAMPLES.md)
  - Feature evolution from Level 1 → 2 → 3
  - User profile feature progression
  - Todo list feature progression
  - Search feature progression

- **Quick lookup**: [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
  - Code templates for each level
  - Common patterns cheat sheet
  - Decision tree
  - Anti-patterns list

---

## Dependencies

**Related skills:**
- None yet (first Swift skill in PAI)

**Recommended context files:**
- `/Users/coreyyoung/Claude/context/knowledge/languages/swift/` - Swift language specifics
- `/Users/coreyyoung/Claude/context/knowledge/frameworks/swiftui/` - SwiftUI patterns
- `/Users/coreyyoung/Claude/context/knowledge/patterns/dependency-injection/` - DI patterns

**Future skill connections:**
- `swift-style-conventions.md` - Code style and naming
- `swiftui-patterns.md` - UI-specific patterns
- `swift-testing.md` - Testing strategies

---

## Quick Reference

| Scenario | Architecture Level | Read |
|----------|-------------------|------|
| Toggle, picker, simple form | Level 1: @State | [ARCHITECTURE_LEVELS.md](ARCHITECTURE_LEVELS.md#level-1) |
| API call needed | Level 2: ViewModel | [ARCHITECTURE_LEVELS.md](ARCHITECTURE_LEVELS.md#level-2) |
| Form validation | Level 2: ViewModel | [VIEWMODEL_PATTERNS.md](VIEWMODEL_PATTERNS.md#validation) |
| Logic shared across screens | Level 3: Service | [SERVICE_LAYER.md](SERVICE_LAYER.md) |
| SOLID principle question | See principles | [SOLID_PRINCIPLES.md](SOLID_PRINCIPLES.md) |
| Need code example | See examples | [EXAMPLES.md](EXAMPLES.md) |

---

## Common Usage Patterns

### Pattern 1: Starting a New Feature
1. Start with Level 1 (@State in view)
2. If API needed → Move to Level 2 (add ViewModel)
3. If logic reused → Move to Level 3 (extract Service)

### Pattern 2: Refactoring Existing Code
1. Identify current architecture level
2. Check if complexity matches level (see Decision Tree)
3. Refactor up or down as needed
4. See [ARCHITECTURE_LEVELS.md](ARCHITECTURE_LEVELS.md#when-to-refactor)

### Pattern 3: Code Review
1. Verify appropriate architecture level for complexity
2. Check SOLID principles compliance
3. Ensure dependency injection is used
4. See [QUICK_REFERENCE.md](QUICK_REFERENCE.md#anti-patterns)

---

## File Organization Example

```
YourApp/
├── Views/
│   ├── Profile/
│   │   ├── ProfileView.swift          # Level 2: Has ViewModel
│   │   └── ProfileViewModel.swift
│   └── Settings/
│       └── SettingsView.swift         # Level 1: Just @State
├── Services/
│   ├── AuthenticationService.swift    # Level 3: Shared across app
│   ├── NetworkService.swift
│   └── PersistenceService.swift
└── Models/
    └── User.swift
```

See [ARCHITECTURE_LEVELS.md](ARCHITECTURE_LEVELS.md#file-organization) for complete organization strategies.

---

## Notes

**Philosophy**: This skill teaches developers to match architecture to complexity rather than applying blanket patterns. It prevents over-engineering simple features while providing clear guidance for when to add architectural layers.

**Transferability**: These patterns translate well to React (hooks), Flutter (Provider/BLoC), and other modern UI frameworks. The "progressive complexity" approach is universal.

**Learning Path**: Best for developers learning iOS development or transitioning from other platforms. Provides a clear decision framework that grows with their understanding.
