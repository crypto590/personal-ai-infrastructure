# Apple API Research

**Part of:** [ios-swift](../SKILL.md) > Review

**Trigger:** Implementing a new iOS feature, asking "what's the best way to do X in iOS 26?", exploring unfamiliar Apple frameworks, checking API availability for target iOS version, finding recommended patterns from Apple, understanding deprecations and migrations, researching WWDC announcements.

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
   - Location: Help -> Developer Documentation
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

### Integration Notes
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
5. Check for project-specific considerations

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
  DocSets/
    com.apple.adc.documentation.AppleiOS[version].docset/
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
