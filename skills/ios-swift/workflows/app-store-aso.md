# App Store ASO Optimization

**Part of:** [ios-swift](../SKILL.md) > Workflows

Adapted from [timbroddin/app-store-aso-skill](https://github.com/timbroddin/app-store-aso-skill) (Tim Broddin).

App Store Optimization: metadata generation, keyword strategy, competitive analysis, and screenshot planning.

---

## Apple App Store Character Limits

| Field | Maximum | Notes |
|---|---|---|
| App Name | 30 characters | Most important for keywords |
| Subtitle | 30 characters | Second most important |
| Promotional Text | 170 characters | Can be changed without new build |
| Description | 4,000 characters | Not indexed for search (but read by users) |
| Keywords | 100 characters | Comma-separated, **no spaces** after commas |
| What's New | 4,000 characters | Per version |

---

## 5-Step Workflow

### 1. Analyze App Context

- Core purpose and primary features
- Target audience and user personas
- Unique value propositions
- Competitive differentiators
- Current App Store category and position

### 2. Keyword Research

**Principles:**
- Keywords field: comma-separated, no spaces after commas (saves characters)
- Don't repeat words already in App Name or Subtitle (Apple indexes those)
- Don't include "app" or your company name (waste of characters)
- Singular/plural: Apple matches both, so use only one form
- Prefer less competitive long-tail keywords over generic high-competition terms

**Structure:**
```
App Name: [brand] - [primary keyword phrase]
Subtitle: [secondary keyword phrase with benefit]
Keywords: [remaining terms, no repeats from name/subtitle]
```

### 3. Generate Optimized Metadata

**App Name (30 chars):**
- Lead with brand or primary keyword
- Include most important search term
- Keep it memorable and readable

**Subtitle (30 chars):**
- Complement the name (don't repeat)
- Include a user benefit
- Second most valuable keyword real estate

**Promotional Text (170 chars):**
- Highlight current promotions, seasonal features, or new updates
- Can be updated anytime (no review needed)
- Not indexed for search

**Description (4,000 chars):**
- First 3 lines visible without "more" tap — make them count
- Structure: hook → features → social proof → call to action
- Not indexed for search, but affects conversion rate

**Keywords (100 chars):**
- Every character counts
- No spaces after commas: `keyword1,keyword2,keyword3`
- Exclude words in name/subtitle
- Mix of volume and relevance

### 4. Validate

Check every field against character limits. Failing fields must be trimmed before submission.

### 5. Screenshot Strategy

**Storyboard sequence:**
1. Hero shot — single most compelling feature
2. Core value proposition
3. Key differentiating feature
4. Social proof or user benefit
5. Secondary features

**Best practices:**
- First 3 screenshots visible in search results — prioritize impact
- Use text overlays with benefit-focused copy (not feature descriptions)
- Show real app content, not placeholder data
- Consider localized screenshots for top markets

---

## Tracking with Krankie (Optional)

[Krankie](https://github.com/nicktim/krankie) is a CLI tool for tracking App Store keyword rankings:

```bash
# Install
bun install -g krankie

# Track an app
krankie app search "your app" --platform ios
krankie app create <app_id> --platform ios

# Add keywords to track
krankie keyword add <app_id> "keyword" --store us

# Check rankings
krankie check run
krankie rankings
krankie rankings movers    # Changes since last check
krankie rankings history <keyword_id>

# Automate daily checks
krankie cron install --hour 6
```

**ASO integration:**
1. Establish baseline rankings before metadata changes
2. Track competitor apps and their keyword positions
3. Monitor `rankings movers` after updates to measure impact
4. Use `rankings history` for trend analysis
