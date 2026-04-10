# SwiftUI Performance Audit

**Part of:** [ios-swift](../SKILL.md) > Review

Adapted from [Dimillian/Skills](https://github.com/Dimillian/Skills) (Thomas Ricouard).

Systematic workflow for diagnosing SwiftUI performance issues. Supplements `swiftui-tips.md` performance section with a structured profiling and remediation process.

---

## When to Use

- Slow rendering or janky scrolling
- High CPU or memory usage
- Excessive view updates / invalidation storms
- Layout thrash
- Main thread hangs

---

## 6-Step Workflow

### Step 1: Classify Symptom

| Symptom | Likely Category |
|---|---|
| Choppy scrolling | Identity churn, layout thrash, main-thread work |
| Slow initial render | Heavy `body` computation, image decode |
| CPU spike during interaction | Invalidation storms, broad observation |
| Memory growth over time | Leaked views, unbounded caches, image accumulation |
| Hang / freeze | Main-thread blocking, synchronous I/O |
| Excessive rebuilds | Broad `@Observable` fan-out, unnecessary environment reads |

### Step 2: Code-First Review

Scan for these code smells before reaching for Instruments:

**Invalidation storms:**
- `@Observable` class with many properties where views only use a few
- Broad `@Environment` reads causing unnecessary rebuilds
- `@State` that should be local stored at a parent level

**Unstable identity:**
- `ForEach` without stable `Identifiable` conformance
- Using array index as identity: `ForEach(0..<items.count, id: \.self)`
- Computed `id` that changes between renders

**Heavy `body` computation:**
- Sorting, filtering, or mapping inside `body`
- Date/number formatting inside `body`
- Creating objects (formatters, contexts) inside `body`

**Layout thrash:**
- Deeply nested `GeometryReader` or preference key chains
- `GeometryReader` inside `ScrollView` items
- Recursive layout dependencies

**Main-thread image work:**
- Large image decode without downsampling
- No `AsyncImage` or background processing for remote images
- Asset catalog images that are oversized for their display size

**Broad animation:**
- `.animation()` without explicit `value` parameter
- `withAnimation` wrapping large state changes
- Animation on parent affecting many children unnecessarily

### Step 3: Profile (If Code Review Inconclusive)

Request from user:
- Instruments Time Profiler trace (or call tree screenshot)
- SwiftUI Instrument timeline showing view body evaluations
- Device model, OS version, Debug vs Release build
- Exact interaction being profiled
- Before/after metrics if available

### Step 4: Diagnose

Map evidence to categories:

| Category | Evidence |
|---|---|
| Invalidation | High body evaluation count in SwiftUI Instrument |
| Identity churn | Views being destroyed/recreated in timeline |
| Layout thrash | GeometryProxy reads in hot path |
| Main-thread work | Time Profiler showing heavy frames on main |
| Image cost | ImageIO or CGImage in hot path |
| Animation cost | CA::Layer or animation interpolation in frames |

**Prioritize by impact, not ease of explanation.** Distinguish code-level suspicion from trace-backed evidence.

### Step 5: Remediate

| Problem | Fix |
|---|---|
| Broad observation fan-out | Narrow `@Observable` to specific view needs, split into focused objects |
| Unstable `ForEach` identity | Make model `Identifiable` with stable IDs |
| Heavy `body` computation | Move to `let` derivation, `@State` cache, or `.task` |
| Layout thrash | Replace `GeometryReader` with `containerRelativeFrame()`, reduce nesting |
| Main-thread image decode | Use `AsyncImage`, `.resizable()`, or background downsampling |
| Broad animation | Add explicit `value:` parameter, scope to affected views only |
| Memory growth | Check for view leaks (strong reference cycles in closures), bound caches |

**Use `equatable()` modifier only when cheaper than recomputation.** Don't add it speculatively.

### Step 6: Verify

- Re-run the same profile capture
- Compare baseline metrics (body evaluation count, frame drops, CPU %, memory peak)
- Summarize delta

---

## Output Format

```
## Performance Audit: [Feature/View Name]

### Metrics
| Metric | Before | After |
|--------|--------|-------|
| Body evaluations | ? | ? |
| Frame drops | ? | ? |
| Peak CPU | ? | ? |
| Memory peak | ? | ? |

### Issues (by impact)
1. [CRITICAL] Description — Evidence — Fix
2. [HIGH] Description — Evidence — Fix
3. [MEDIUM] Description — Evidence — Fix

### Proposed Fixes
- [ ] Fix 1 (effort: low/medium/high)
- [ ] Fix 2 (effort: low/medium/high)
```
