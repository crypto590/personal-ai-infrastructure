# Swift Architecture Skill

A comprehensive skill for building iOS apps with progressive, scalable architecture that follows modern SwiftUI patterns and SOLID principles.

**Category**: Technical  
**PAI-Compliant**: Yes (Progressive disclosure, ~150-line SKILL.md)

---

## What This Skill Provides

This skill teaches a **"start simple, add complexity when needed"** approach to iOS development:

- **Level 1**: Simple views with `@State` (no ViewModel needed)
- **Level 2**: Views with `@Observable` ViewModels (when business logic appears)
- **Level 3**: Shared Services (when logic is used across features)

Plus comprehensive **SOLID principles** integration at every level.

---

## Files in This Skill

### Core Documentation

- **[SKILL.md](SKILL.md)** - **Start here!** Main entry point
  - Brief overview with triggers and dependencies (~150 lines)
  - Quick decision tree
  - References to all detailed documentation
  - PAI-compliant metadata for efficient loading

### Detailed Documentation (Progressive Disclosure)

Read these when you need deeper knowledge on specific topics:

- **[ARCHITECTURE_LEVELS.md](ARCHITECTURE_LEVELS.md)** - Complete architecture guide
  - Detailed Level 1, 2, 3 patterns with code examples
  - File organization strategies
  - When to refactor between levels
  - Testing strategies per level
  - Anti-patterns to avoid

- **[VIEWMODEL_PATTERNS.md](VIEWMODEL_PATTERNS.md)** - Comprehensive ViewModel patterns
  - State management strategies
  - Error handling patterns
  - Validation approaches
  - Testing ViewModels
  - Common patterns (search, pagination, optimistic updates)

- **[SERVICE_LAYER.md](SERVICE_LAYER.md)** - Building robust services
  - Common service types (Auth, Network, Persistence, Location)
  - Dependency injection strategies
  - Protocol-based design
  - Error handling in services
  - Caching strategies
  - Testing services

- **[SOLID_PRINCIPLES.md](SOLID_PRINCIPLES.md)** - SOLID principles with Swift examples
  - Single Responsibility (SRP)
  - Open/Closed (OCP)
  - Liskov Substitution (LSP)
  - Interface Segregation (ISP)
  - Dependency Inversion (DIP)
  - Real-world examples combining all principles

### Practical Resources

- **[EXAMPLES.md](EXAMPLES.md)** - Real-world feature evolution
  - User profile feature progression (Level 1 → 2 → 3)
  - Todo list feature progression
  - Search feature progression
  - Decision examples for each level

- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Quick lookup cheat sheet
  - Code templates for each level
  - Common patterns
  - Decision tree
  - Anti-patterns list
  - SOLID quick checks

### Additional

- **[CROSS_REFERENCES_UPDATE.md](CROSS_REFERENCES_UPDATE.md)** - Documentation of restructuring
  - Shows how skill was made PAI-compliant
  - Cross-reference map
  - Token efficiency gains

---

## How Claude Uses This Skill

### Automatic Triggering

Claude loads this skill when you:
- Start building an iOS/macOS/watchOS app
- Ask about architecture decisions
- Need help organizing code
- Want to add features to existing apps
- Ask where logic should live
- Request code reviews or refactoring
- Mention MVVM, ViewModels, Services, or SOLID

### Progressive Loading

**Initial Load** (~1,500 tokens):
- SKILL.md metadata and overview
- Knows all available detailed files
- Can answer basic architecture questions

**When Needed** (+3,000-5,000 tokens per file):
- Loads specific detailed files based on your question
- Example: If you ask about ViewModels, loads VIEWMODEL_PATTERNS.md
- Example: If you ask about SOLID, loads SOLID_PRINCIPLES.md

**Typical Usage**: ~4,500 tokens (SKILL.md + one detailed file)  
**Complex Usage**: ~10,500 tokens (SKILL.md + three detailed files)  
**Savings**: 55-75% compared to loading everything upfront

---

## Quick Start Guide

### For Learning Developers

1. Start with **[SKILL.md](SKILL.md)** to understand the core approach
2. Build a simple feature using Level 1 (just `@State`)
3. When you add API calls, graduate to Level 2 (ViewModel)
4. Reference the deep dive files as questions arise

### For Experienced Developers

Use this as a reference for:
- Consistent patterns across your codebase
- Teaching team members the approach
- Quick decision-making on architecture levels
- SOLID principle applications in Swift

---

## Architecture Philosophy

This skill follows these core beliefs:

1. **Don't over-engineer simple features** - Start with the simplest solution
2. **Scale with complexity** - Add architectural layers as features demand them
3. **SOLID principles apply everywhere** - Good design principles work at all levels
4. **Protocol-based design** - Depend on abstractions for flexibility and testability
5. **Dependency injection** - Always inject dependencies for testability

---

## Quick Decision Tree

```
Does the view only display/update simple local state?
├─ YES → Level 1: @State in view
└─ NO → Does it need API calls, validation, or complex logic?
    ├─ YES → Level 2: Add ViewModel
    └─ Is this logic shared across multiple features?
        ├─ YES → Level 3: Extract to Service
        └─ NO → Keep in ViewModel
```

See [SKILL.md](SKILL.md) or [ARCHITECTURE_LEVELS.md](ARCHITECTURE_LEVELS.md#decision-tree) for more details.

---

## Example Project Structure

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

## Transferable to Other Platforms

The principles in this skill transfer to:

| Platform | Level 1 | Level 2 | Level 3 |
|----------|---------|---------|---------|
| **React** | useState | Custom hooks | Context/Redux |
| **Flutter** | StatefulWidget | ChangeNotifier | Provider/BLoC |
| **Android Compose** | remember/mutableState | ViewModel | Repository |
| **Angular** | Component state | Component logic | Services |

The "progressive complexity" approach is universal across platforms.

---

## Installing This Skill

### In Claude.ai (Projects)

This skill is designed for PAI (Personal AI Infrastructure) integration:

1. **Option A**: Upload to Project
   - Zip the `swift-architecture` directory
   - Upload to your Claude.ai Project
   - Claude will auto-discover and use it

2. **Option B**: Reference from PAI
   - Move to `/Users/coreyyoung/Claude/skills/technical/swift-architecture/`
   - Reference from your project's CLAUDE.md:
     ```markdown
     ## Load PAI Skills
     - Read: /Users/coreyyoung/Claude/skills/technical/swift-architecture/SKILL.md
     ```

### For Claude Code CLI

1. Move directory to `/Users/coreyyoung/Claude/skills/technical/swift-architecture/`
2. Claude Code will auto-discover it
3. Use naturally: "Help me build a Swift app with proper architecture"

---

## PAI Compliance

This skill follows PAI (Personal AI Infrastructure) best practices:

✅ **Progressive Disclosure**: Brief SKILL.md (~150 lines) with detailed files loaded on demand  
✅ **Metadata First**: Clear triggers and dependencies  
✅ **Cross-Referenced**: All files link together properly  
✅ **Single Responsibility**: Each file covers one focused topic  
✅ **Build Once, Use Everywhere**: Works across all Swift projects  

**Token Efficiency**: 55-75% reduction compared to loading all content upfront.

---

## Maintenance & Updates

### When to Update This Skill

Update the skill when you:
- Discover better architectural patterns
- Find common mistakes to add to anti-patterns
- Learn new SOLID applications
- Encounter new edge cases
- Swift/SwiftUI introduces new patterns

### How to Update

1. **Simple additions**: Add to relevant file (e.g., new pattern → VIEWMODEL_PATTERNS.md)
2. **New concepts**: Create new file and reference from SKILL.md
3. **Corrections**: Update the specific section in the relevant file
4. **Keep SKILL.md brief**: Don't add details to SKILL.md, add them to detail files

---

## Feedback and Iteration

As you use this skill:
- Note when Claude's suggestions don't match your expectations
- Observe what patterns emerge naturally in your codebase
- Update the skill based on real usage patterns
- Add project-specific conventions to your project's CLAUDE.md (not to this skill)

**Remember**: This skill contains universal Swift architecture patterns. Project-specific details belong in your project files, not here.

---

## Version History

- **v1.1.0** (2025-11-03): Restructured for PAI compliance
  - Reduced SKILL.md from ~400 lines to ~150 lines
  - Extracted detailed content to ARCHITECTURE_LEVELS.md
  - Renamed SOLID_DEEP_DIVE.md to SOLID_PRINCIPLES.md
  - Added comprehensive cross-references
  - Added CROSS_REFERENCES_UPDATE.md documentation
  - Achieved 55-75% token efficiency improvement

- **v1.0.0** (2025-11-03): Initial comprehensive skill
  - Three-level progressive architecture
  - SOLID principles integration
  - ViewModel and Service patterns
  - Real-world examples
  - Quick reference

---

## Next Steps

1. ✅ Read [SKILL.md](SKILL.md) to understand the approach
2. ✅ Ask Claude to help build a Swift feature
3. ✅ Reference deep dive files as needed
4. ✅ Update skill based on your learnings

**Remember:** This skill grows with you. It's a living document that should reflect your evolving expertise.

---

**Questions?** 
- Check [SKILL.md](SKILL.md) for overview
- Check [ARCHITECTURE_LEVELS.md](ARCHITECTURE_LEVELS.md) for architecture details
- Check [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for fast lookups
- Check [CROSS_REFERENCES_UPDATE.md](CROSS_REFERENCES_UPDATE.md) for restructuring details
