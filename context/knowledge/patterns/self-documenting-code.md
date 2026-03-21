# Self-Documenting Code Patterns

Language-agnostic principles for writing code that explains itself through structure, naming, and data shape — not comments.

---

## Semantic Functions

Semantic functions are the building blocks of the codebase. They are minimal, pure, and self-describing.

**Rules:**
- Take in all required inputs as parameters, return all necessary outputs directly
- No side effects unless the side effect IS the explicit goal (e.g., `write_to_disk()`)
- Safe to reuse without understanding internals — the name tells you what it does
- Should not need any comments — the code itself is the definition
- Extremely unit-testable because they are well-defined

**Examples:**
- `quadratic_formula(a, b, c) → [x1, x2]`
- `retry_with_exponential_backoff(fn, maxRetries, delay) → Result`
- `parse_iso_date(input) → Date | Error`
- `calculate_shipping_cost(weight, zone) → Price`

**Naming:** Name by what it does, not where it's used. The name should make re-use obvious and safe.

**When to extract:** If logic within a larger flow is not immediately clear, extract it into a semantic function even if it's only used once. The name provides indexing for future readers (human and agent).

---

## Pragmatic Functions

Pragmatic functions are wrappers around semantic functions and unique business logic. They are the complex processes of the codebase.

**Rules:**
- Compose semantic functions + unique logic for a specific use case
- Should generally not be used in more than a few places
- If reused widely, break the shared logic into semantic functions
- Expected to change completely over time — internals and purpose may both shift
- Testing falls into integration testing, not unit testing

**Examples:**
- `provision_new_workspace_for_github_repo(repo, user)`
- `handle_user_signup_webhook(payload)`
- `process_monthly_billing_cycle(orgId)`
- `sync_roster_from_csv_upload(file, teamId)`

**Naming:** Name by where/when it's used, not by the abstract operation. The name signals to readers that behavior is context-dependent and should not be relied on for an exact internal contract.

**Comments:** Add doc comments above pragmatic functions, but only for unexpected behavior:
- DO: "Fails early if balance < 10 — intentional guard against overdraft"
- DO: "Retries up to 3x on 429, but NOT on 5xx — vendor recommends this"
- DON'T: Restate the function name or describe obvious parameters
- DON'T: Trust existing doc comments blindly — they may be stale. Fact-check when the comment seems wrong.

---

## Models

The shape of your data should make wrong states impossible.

### Core Principle
Every optional field is a question the rest of the codebase has to answer every time it touches that data. Every loosely typed field is an invitation for callers to pass something that looks right but isn't.

### Rules

**Make wrong states impossible:**
- If two fields should never exist together, enforce that structurally (e.g., discriminated unions, sealed classes, enums with associated data)
- When models enforce correctness, bugs surface at construction rather than deep in unrelated flows

**Name precisely:**
- A model's name should be specific enough that you can look at any field and know whether it belongs
- If the name doesn't tell you, the model is trying to be too many things
- Good names: `UnverifiedEmail`, `PendingInvite`, `BillingAddress`, `ActiveSubscription`
- Bad signal: a `phone_number` field on `BillingAddress` — that field doesn't belong

**Compose, don't merge:**
- When two concepts are needed together but are independent, compose them:
  ```
  UserAndWorkspace { user: User, workspace: Workspace }
  ```
- Don't flatten workspace fields into User — it couples two independent domains

**Brand/nominal types:**
- Values with identical shapes can represent different domain concepts
- `{ id: "123" }` might be a `DocumentReference` or a `MessagePointer`
- Brand types wrap primitives in distinct types so the compiler catches swaps:
  ```
  DocumentId(UUID)  // not a bare UUID
  TeamId(String)    // not a bare String
  ```
- Accidentally swapping two branded IDs becomes a compile error instead of a silent bug three layers deep

---

## Where Things Break

### Function Drift
A semantic function morphs into a pragmatic function when someone adds "just one quick side effect" for convenience. Other callers that relied on its purity now do things they didn't intend.

**Detection signals:**
- A function named like a semantic function (`calculate_tax`) that also sends an email or writes to a database
- A function whose behavior depends on hidden state (global variables, class properties not in the parameter list)
- A function that used to have unit tests but they started "needing" mocks for external services

**Fix:** Extract the side effect. Keep the semantic function pure. Create a pragmatic function that composes them.

### Model Drift
Models break the same way but slower. They start focused, then someone adds "just one more" optional field because creating a new model feels like overhead.

**Detection signals:**
- A model with 3+ optional fields that are only set in specific contexts
- A model whose name no longer describes all its fields (`User` with `lastInvoiceAmount`)
- Fields that are set to `null` in most records — they probably belong to a different model
- Consumers of the model having to check "which kind of X is this?" before using it

**Fix:** Split the model into the distinct things it's been coupling together. Use composition to recombine when both are needed.

---

## Decision Framework

| Question | Semantic Function | Pragmatic Function |
|----------|------------------|--------------------|
| Can I reuse this safely without reading the internals? | Yes | No — read the internals first |
| Does it have side effects? | Only if that IS the purpose | Yes, expected |
| Does it need comments? | No — name is the documentation | Yes — doc unexpected behavior |
| How do I test it? | Unit test | Integration test |
| Will it change frequently? | Rarely — it's a building block | Often — it's a process |
| How do I name it? | By what it does | By where/when it's used |

---

## Application to Code Review

When reviewing code, check for:

1. **Function classification** — Is this function semantic or pragmatic? Does the naming match?
2. **Semantic purity** — Do semantic functions have hidden side effects or depend on external state?
3. **Model coherence** — Do all fields belong under this model's name? Are there optional fields that signal model drift?
4. **Brand types on domain IDs** — Are bare primitives used where domain-specific types would prevent cross-domain bugs?
5. **Comment appropriateness** — Semantic functions with comments (unnecessary) or pragmatic functions without them (missing unexpected behavior docs)?
6. **Composition vs merging** — Are independent concepts flattened into one model when they should be composed?
