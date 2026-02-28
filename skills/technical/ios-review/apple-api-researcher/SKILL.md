---
name: apple-api-researcher
description: Research latest Apple APIs using Xcode documentation and official sources. Use when implementing new iOS features to find current best practices and API usage patterns.
compatibility: "Requires macOS with Xcode installed for documentation access"
context: fork
metadata:
  author: coreyyoung
  version: 1.0.0
  category: technical
  tags: [ios, apple, api-research, xcode, documentation, swift]
---

# Apple API Researcher

**Category:** technical/ios-review

**Brief Description:** Research agent that investigates Apple's latest APIs, frameworks, and best practices. Sources include Xcode's built-in documentation, Apple Developer documentation, WWDC sessions, and Human Interface Guidelines. Use before implementing new iOS features.

---

## When to Use This Skill

Trigger this skill when:
- Implementing a new iOS feature
- User asks "what's the best way to do X in iOS 26?"
- Exploring unfamiliar Apple frameworks
- Checking if an API is available in target iOS version
- Finding recommended patterns from Apple
- Understanding deprecations and migrations
- Researching WWDC announcements

---

## Research Process

### 1. Identify the Domain

First, categorize the feature request:

| Domain | Frameworks | Example Features |
|--------|------------|------------------|
| UI/UX | SwiftUI, UIKit, AppKit | Glass effects, navigation, animations |
| Data | SwiftData, CoreData, CloudKit | Persistence, sync, queries |
| Media | AVFoundation, PhotoKit, Vision | Video, photos, ML analysis |
| System | Foundation, BackgroundTasks | Networking, scheduling |
| Hardware | CoreLocation, CoreMotion, ARKit | Sensors, AR, location |
| Services | StoreKit, HealthKit, HomeKit | Purchases, health, smart home |
| AI/ML | CoreML, CreateML, Foundation Models | On-device intelligence |

### 2. Check Documentation Sources

#### Primary Sources (in order of authority)

1. **Xcode Documentation**
   - Location: Help → Developer Documentation
   - Most accurate for API signatures and availability
   - Includes migration guides

2. **Apple Developer Documentation**
   - URL: developer.apple.com/documentation/
   - Comprehensive guides and tutorials
   - Sample code projects

3. **Human Interface Guidelines**
   - URL: developer.apple.com/design/human-interface-guidelines/
   - Design patterns and recommendations
   - Platform-specific guidance

4. **WWDC Sessions**
   - URL: developer.apple.com/videos/
   - Deep dives into new features
   - Best practices from Apple engineers

### 3. Verify API Availability

```swift
// Check minimum deployment target
@available(iOS 26.0, *)
func useNewFeature() {
    // iOS 26+ only code
}

// Runtime availability check
if #available(iOS 26, *) {
    // Use new API
} else {
    // Fallback
}
```

**Document availability:**
```
API: [name]
Introduced: iOS [version]
Deprecated: iOS [version] (if applicable)
Replacement: [new API] (if deprecated)
```

### 4. Extract Usage Patterns

For each researched API, document:

```markdown
## [API/Feature Name]

### Availability
- Minimum iOS: X.X
- Frameworks: [list]
- Swift version: X.X

### Basic Usage
[code example]

### Best Practices
1. [from Apple documentation]
2. [from WWDC sessions]

### Common Pitfalls
- [gotchas to avoid]

### Related APIs
- [complementary frameworks/APIs]

### Sample Code
- [Apple sample project links]
```

---

## Research Output Format

```markdown
## Apple API Research: [Topic]

### Query
[Original user question/requirement]

### Recommended Approach
[High-level recommendation]

### Primary API
**Framework:** [name]
**Availability:** iOS [version]+
**Documentation:** [link]

### Implementation Pattern
[code example from Apple docs]

### Alternative Approaches
1. [if applicable]
2. [if applicable]

### Caveats
- [limitations]
- [known issues]
- [deprecation warnings]

### Resources
- Documentation: [link]
- WWDC Session: [link]
- Sample Code: [link]

### Athlead Integration Notes
[How this fits with existing architecture]
```

---

## Common Research Scenarios

### New Framework Investigation

When user asks about a framework they haven't used:

1. Find framework documentation
2. Identify key types and protocols
3. Find Getting Started guide
4. Locate sample projects
5. Check for Athlead-specific considerations

### Migration Research

When moving from deprecated to new API:

1. Find deprecation notice
2. Identify replacement API
3. Compare functionality
4. Document migration steps
5. Check for backward compatibility needs

### WWDC Feature Research

When implementing a WWDC-announced feature:

1. Find relevant WWDC session(s)
2. Check documentation availability
3. Verify iOS version requirements
4. Look for beta release notes
5. Check for known issues

---

## Documentation Paths

### Xcode Built-in Documentation

```
/Applications/Xcode.app/Contents/Developer/Documentation/
└── DocSets/
    └── com.apple.adc.documentation.AppleiOS[version].docset/
```

### Common Documentation URLs

| Framework | URL |
|-----------|-----|
| SwiftUI | developer.apple.com/documentation/swiftui |
| UIKit | developer.apple.com/documentation/uikit |
| SwiftData | developer.apple.com/documentation/swiftdata |
| Foundation Models | developer.apple.com/documentation/foundationmodels |
| StoreKit | developer.apple.com/documentation/storekit |
| HealthKit | developer.apple.com/documentation/healthkit |

---

## Integration with Athlead

When researching for Athlead features:

1. **Check existing conventions:**
   - `docs/swift-conventions.md`
   - `docs/swift-best-practices.md`
   - `docs/liquid-glass-conventions.md`

2. **Consider architecture fit:**
   - MVC pattern compatibility
   - Service layer integration
   - Controller coordination

3. **Document findings:**
   - Update relevant docs if new patterns discovered
   - Note any convention modifications needed

---

## Dependencies

**Required context:**
- `/Users/coreyyoung/Desktop/Projects/athlead/docs/swift-conventions.md`
- `/Users/coreyyoung/Desktop/Projects/athlead/docs/swift-best-practices.md`

**Related skills:**
- `swift-mvc` - Architecture integration
- `ios-liquid-glass-reviewer` - Design system research
- `swift-concurrency-auditor` - Concurrency patterns
