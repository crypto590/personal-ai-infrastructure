---
name: Athlead uses bun test, not vitest
description: When fixing or porting tests in athlead, use bun test — never suggest vitest as an alternative
type: feedback
---

Athlead's test runner is `bun test` exclusively. Every test file imports from `bun:test` (`import { describe, test, expect, mock, beforeEach } from "bun:test"`), and there is no Vitest configuration in the repo.

**Why:** This is a deliberate platform choice consistent with the rest of the toolchain (`bun` for package management, `bun --watch` for dev, `bun build` for compilation). Mixing test runners would mean two mocking APIs, two config surfaces, and two CI invocations.

**How to apply:**
- When tests fail because of `bun test`-specific behaviour (module mock caching across dynamic imports, etc.), the fix is structural — split tests into separate files so each gets a fresh module graph, or refactor to avoid the foot-gun. Do NOT propose porting to Vitest, Jest, or Node test as the solution.
- When suggesting test improvements or follow-ups, name `bun test` features (`mock.module`, `mock.restore`, `bun:test`'s `describe.skip`/`test.skip`) rather than the Vitest equivalents.
- If the user complains that a fix used the wrong runner, that's the kind of paper-cut to avoid here.
