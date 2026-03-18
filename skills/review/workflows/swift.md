# Swift Review Checklist

Apply this checklist to all changed `.swift` files. This workflow orchestrates the existing ios-swift review checklists — read and apply each referenced file rather than duplicating their content.

## How to Use

Read and apply each referenced checklist below to the changed Swift files. Each checklist file contains detailed rules and examples specific to its domain.

## Checklists

### Concurrency
Read and apply: `ios-swift/review/concurrency.md`

Key areas covered:
- Actor isolation violations
- Task cancellation handling (checking `Task.isCancelled`, using `withTaskCancellationHandler`)
- Sendable conformance for types crossing isolation boundaries
- MainActor usage for UI updates
- Structured vs unstructured concurrency choices
- Data race prevention

### Pattern Validation
Read and apply: `ios-swift/review/pattern-validation.md`

Key areas covered:
- MVC architecture compliance (Controllers, Services, Models, Views separation)
- Service layer patterns and proper abstraction
- Dependency injection correctness
- Navigation patterns
- Protocol-oriented design

### Accessibility
Read and apply: `ios-swift/review/accessibility.md`

Key areas covered:
- VoiceOver labels and hints on all interactive elements
- Dynamic Type support (no fixed font sizes)
- Color contrast ratios meeting WCAG guidelines
- Accessibility traits and actions
- Focus management for custom controls

### Liquid Glass (iOS 26+)
Read and apply: `ios-swift/review/liquid-glass.md`

Key areas covered:
- Single-layer glass rule (no stacking glass on glass)
- Appropriate glass surface usage (navigation bars, tab bars, toolbars)
- Text and icon readability over glass backgrounds
- Proper use of `.glassEffect()` modifier
- Fallback behavior for older iOS versions
