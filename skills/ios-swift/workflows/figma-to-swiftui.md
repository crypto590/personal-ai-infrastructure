# Figma to SwiftUI Workflow

**Part of:** [ios-swift](../SKILL.md) > Workflows

Adapted from [daetojemax/figma-to-swiftui-skill](https://github.com/daetojemax/figma-to-swiftui-skill) (Ermolaev Maxim).

8-step workflow for translating Figma designs into SwiftUI. Requires Figma MCP server.

---

## Prerequisites

- Figma MCP server connected (figma-developer-mcp or figma-desktop)
- Figma URL with fileKey and nodeId, or figma-desktop with selected node
- Xcode project with SwiftUI codebase

---

## Two Modes

- **New screen:** Run all 8 steps sequentially
- **Update existing screen:** Steps 1-5, then 5b (Adaptation Audit), then Step 6+

---

## 8-Step Workflow

### Step 1: Parse Figma URL

Extract `fileKey` and `nodeId` from URL. Replace `-` with `:` in nodeId for MCP calls. Reject `/proto/` and `/board/` URLs (not design files).

### Step 2: Fetch Design Context

Call `get_design_context()` with iOS/SwiftUI prompt. Handle truncated responses via `get_metadata`. For multi-device frames, identify the correct device variant.

### Step 3: Capture Screenshot

Call `get_screenshot()` — this is the **source of truth** for visual validation. Compare against it throughout implementation.

### Step 4: Fetch Design Tokens

Call `get_variable_defs()` to get colors, spacing, typography tokens from Figma variables.

### Step 5: Download Assets

- Check SF Symbols first — prefer system symbols over custom assets
- Download via ephemeral localhost URLs from MCP
- Add to Asset Catalog with proper `Contents.json` and scale variants (1x, 2x, 3x)

### Step 5b: Adaptation Audit (Update Mode Only)

Element-by-element diff checklist:
- **ADD:** New elements not in current implementation
- **UPDATE:** Changed elements (spacing, color, typography, layout)
- **REMOVE:** Elements no longer in design
- Pay special attention to spacing changes

### Step 6: Implement in SwiftUI

Check `get_code_connect_map()` for existing component mappings. Inspect project dependencies before adding new ones.

**Critical rule:** MCP output is a design spec, not code to port. Translate design intent into idiomatic SwiftUI.

#### 6.1 Layout Translation

| Figma | SwiftUI |
|---|---|
| Auto Layout (vertical) | `VStack` |
| Auto Layout (horizontal) | `HStack` |
| Overlapping layers | `ZStack` |
| Padding | `.padding()` |
| Item spacing (gap) | `VStack(spacing:)` / `HStack(spacing:)` |
| Fill container | `.frame(maxWidth: .infinity)` |
| Hug contents | Default (no frame) |
| Fixed size | `.frame(width:height:)` |

#### 6.2 Typography Translation

Map Figma text styles to SwiftUI:
- Font family/weight → `.font()` with system or custom font
- Line height → `.lineSpacing()` (subtract font's default leading)
- Letter spacing → `.tracking()` or `.kerning()`
- Prefer system Dynamic Type sizes (`.body`, `.headline`, etc.) when close match

#### 6.3 Color Translation

- Hex values → `Color(hex:)` extension or Asset Catalog colors
- Figma variables → map to project's design token system
- Gradient fills → `LinearGradient` / `RadialGradient` / `AngularGradient`
- Dark mode → use Asset Catalog color sets with Any/Dark appearances

#### 6.4 Component Translation

| Figma Component | SwiftUI |
|---|---|
| Button variants | `Button` with `.buttonStyle()` |
| Text input | `TextField` / `SecureField` |
| Toggle | `Toggle` |
| Image | `Image` / `AsyncImage` |
| List / table | `List` / `ForEach` |
| Tab bar | `TabView` |
| Sheet / modal | `.sheet()` / `.fullScreenCover()` |
| Card | Custom View with `.background()` + `.clipShape()` |
| Component variants | View with enum parameter or `@ViewBuilder` |

#### 6.5 Effects and Decorations

| Figma | SwiftUI |
|---|---|
| Drop shadow | `.shadow()` |
| Background blur | `.blur()` / `.ultraThinMaterial` |
| Corner radius | `.clipShape(.rect(cornerRadius:))` |
| Border/stroke | `.overlay { RoundedRectangle().stroke() }` |
| Mask | `.mask { }` |
| Blend mode | `.blendMode()` |
| Liquid Glass (iOS 26+) | `.glassEffect()` |

#### 6.6 Animations and Transitions

| Figma | SwiftUI |
|---|---|
| Dissolve | `.opacity` transition |
| Move / slide | `.move(edge:)` / `.slide` transition |
| Push | `NavigationStack` push |
| Smart animate | `withAnimation` + `matchedGeometryEffect` |
| Scroll animate | `ScrollView` + `.scrollTransition` |

Check for Lottie animations — these require the `lottie-ios` package.

### Step 7: Validate (On Request Only)

Checklist:
- [ ] Layout matches screenshot
- [ ] Typography matches (font, size, weight, spacing)
- [ ] Colors match (light and dark mode)
- [ ] Assets render correctly at all scales
- [ ] Interactive states work (pressed, disabled, focused)
- [ ] Dynamic Type adjusts properly
- [ ] Safe areas respected
- [ ] Scroll behavior matches design

### Step 8: Register Code Connect Mappings

For reusable, stable components, call `add_code_connect_map()` to link Figma component to SwiftUI implementation for future use.

---

## System Elements to Skip

Do not implement — these are provided by the system:
- Keyboard, status bar, home indicator
- Navigation bar back button
- Tab bar (if using native `TabView`)
- System alerts, share sheet
- Search bar (if using `searchable()`)
- Pull-to-refresh, page indicators

---

## Key Principles

1. Always fetch design context before implementing
2. MCP output is a spec, not code — translate to idiomatic SwiftUI
3. Use existing project dependencies and design tokens
4. Project tokens override Figma values when they conflict
5. Validate only when user requests it
6. Prefer SF Symbols over custom assets
7. Follow platform conventions (Dynamic Type, safe areas, system components)

---

## MCP Tools Reference

| Tool | Purpose |
|---|---|
| `get_design_context()` | Fetch design structure and properties |
| `get_metadata()` | Get additional details for truncated responses |
| `get_screenshot()` | Capture visual reference (source of truth) |
| `get_variable_defs()` | Fetch design tokens (colors, spacing, typography) |
| `get_code_connect_map()` | Check existing Figma→SwiftUI component mappings |
| `add_code_connect_map()` | Register new component mappings |
