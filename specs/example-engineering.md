# Spec: Add Dark Mode Toggle to Settings Page

> Created: 2026-03-10
> Priority: high
> Time Limit: 5 minutes

---

## Instructions

**Context:**
The app has a settings page at `src/app/settings/page.tsx`. We use Tailwind CSS with the `class` dark mode strategy (configured in tailwind.config.ts). There is already a ThemeContext at `src/contexts/ThemeContext.tsx` that exposes `theme` and `toggleTheme`, but no UI control is wired up to it.

**Constraints:**
- Use the existing ThemeContext — do not create a new state management approach
- Follow the existing component patterns in `src/components/ui/`
- Must persist preference to localStorage (the context already does this)
- Accessible: must work with keyboard navigation and screen readers
- No new dependencies

**Approach:**
1. Build the toggle component first
2. Wire it into the settings page
3. Verify the theme switches correctly
4. Add a test

---

## Tasks

1. Create `src/components/ui/ThemeToggle.tsx` — a toggle switch that uses ThemeContext to switch between light/dark mode
2. Add the ThemeToggle to the settings page in the "Appearance" section (create the section if it does not exist)
3. Ensure the toggle reflects the current theme state on page load
4. Add a unit test at `src/components/ui/__tests__/ThemeToggle.test.tsx` covering: renders, toggles theme on click, reflects initial state

---

## Deliverables

**Success looks like:**
- A working dark mode toggle on the settings page
- Theme persists across page reloads
- Toggle is accessible (aria-label, keyboard support)
- Test passes

**Artifacts to produce:**
- [ ] `src/components/ui/ThemeToggle.tsx` — the toggle component
- [ ] Updated `src/app/settings/page.tsx` — with toggle integrated
- [ ] `src/components/ui/__tests__/ThemeToggle.test.tsx` — unit test
- [ ] Terminal output from running the test suite

---

## Time Limit

**Default: 5 minutes.**

If you are approaching the time limit:
1. Stop working on new tasks
2. Document what you completed and what remains
3. Deliver partial results with a clear status summary
4. List any blockers or decisions that need human input

Do NOT spend time polishing — deliver what you have.
