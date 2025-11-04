# Context Template

Copy-paste template for creating new PAI context (reference) files.

**Referenced from**: [SKILL.md](SKILL.md)

**Related**:
- [skill-template.md](skill-template.md) - Skill file template
- [structure.md](structure.md) - PAI structure reference
- [best-practices.md](best-practices.md) - Best practices

---

## When to Use This Template

Use this template when:
- Creating reference documentation
- Adding API documentation to PAI
- Documenting syntax or configuration
- Capturing framework-specific knowledge
- Any "what things are" content

---

## Basic Context File Template

For simple reference files (100-300 lines):

```markdown
# [Topic Name]

[1-2 sentence description of what this context covers]

**Referenced from**: [skill-name.md](../../skills/category/skill-name.md)

**Related**:
- [related-context.md](related-context.md) - [What it covers]
- [another-related.md](another-related.md) - [Why it's related]

---

## Overview

[Brief overview of the topic - 2-3 paragraphs]

**Key features:**
- [Feature 1]
- [Feature 2]
- [Feature 3]

**When to use:** [Brief guidance on when this applies]

---

## [Main Section 1]

[Reference content - syntax, API details, configuration, etc.]

### [Subsection 1.1]

[Detailed reference information]

**Example:**
```[language]
[Code example if applicable]
```

### [Subsection 1.2]

[Detailed reference information]

---

## [Main Section 2]

[Reference content]

### [Subsection 2.1]

[Detailed reference information]

---

## [Main Section 3]

[Reference content]

---

## Common Patterns

[Optional: Common usage patterns for this API/syntax]

### Pattern 1: [Name]

```[language]
[Example]
```

### Pattern 2: [Name]

```[language]
[Example]
```

---

## Quick Reference

[Optional: Quick lookup table or cheat sheet]

| Item | Syntax | Description |
|------|--------|-------------|
| [Item 1] | `code` | [Description] |
| [Item 2] | `code` | [Description] |

---

## Related Resources

**Official documentation:**
- [Link to official docs]

**Other context files:**
- [related-file.md](related-file.md) - [What it covers]

**Skills that use this:**
- [skill-name.md](../../skills/category/skill.md) - [How it uses this context]
```

---

## Detailed Context File Template

For longer reference files (200-500 lines) with table of contents:

```markdown
# [Topic Name] - Complete Reference

[Description of what this context covers]

**Referenced from**: [skill-name.md](../../skills/category/skill-name.md)

**Related**:
- [related-context.md](related-context.md) - [Relationship]

---

## Table of Contents

- [Overview](#overview)
- [Section 1](#section-1)
  - [Subsection 1.1](#subsection-11)
  - [Subsection 1.2](#subsection-12)
- [Section 2](#section-2)
- [Section 3](#section-3)
- [Quick Reference](#quick-reference)

---

## Overview

[Comprehensive overview of the topic]

**Scope:** [What this covers and doesn't cover]

**Prerequisites:** [What you should know before reading this]

**Version:** [If version-specific, note which version]

---

## Section 1

[Detailed reference content]

### Subsection 1.1

[Content with examples]

**Syntax:**
```[language]
[Syntax definition]
```

**Parameters:**
- `param1` - [Description]
- `param2` - [Description]

**Example:**
```[language]
[Usage example]
```

### Subsection 1.2

[Content]

---

## Section 2

[Reference content]

---

[Continue with detailed sections...]

---

## Quick Reference

[Comprehensive quick reference section]

---

## Notes

[Additional notes, gotchas, version changes, deprecations]

---

## Related Resources

**Official documentation:**
- [Links]

**Related context:**
- [Files]

**Skills:**
- [Related skills]
```

---

## API Reference Template

For documenting APIs:

```markdown
# [API Name] API Reference

Complete API reference for [API name].

**Referenced from**: [skill-name.md](../../skills/category/skill-name.md)

**Official docs**: [Link to official documentation]

---

## Table of Contents

- [Authentication](#authentication)
- [Endpoints](#endpoints)
- [Data Models](#data-models)
- [Error Handling](#error-handling)

---

## Authentication

[How authentication works]

**Method:** [JWT, API Key, OAuth, etc.]

**Example:**
```[language]
[Authentication example]
```

---

## Endpoints

### [Endpoint 1]: [Description]

**Method:** `[HTTP METHOD]`

**URL:** `[endpoint URL]`

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `param1` | string | Yes | [Description] |
| `param2` | number | No | [Description] |

**Request body:**
```json
{
  "field1": "value",
  "field2": 123
}
```

**Response:**
```json
{
  "id": "abc123",
  "status": "success",
  "data": { }
}
```

**Error responses:**
- `400` - [Bad request description]
- `401` - [Unauthorized description]
- `404` - [Not found description]

**Example:**
```[language]
[Complete usage example]
```

---

### [Endpoint 2]: [Description]

[Same structure as above]

---

## Data Models

### [Model 1]

[Description of this model]

**Schema:**
```typescript
interface ModelName {
  field1: string;
  field2: number;
  field3?: boolean;  // Optional
}
```

**Example:**
```json
{
  "field1": "value",
  "field2": 123,
  "field3": true
}
```

---

## Error Handling

[How errors work in this API]

**Error response format:**
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message"
  }
}
```

**Common error codes:**
- `ERROR_CODE_1` - [Description and how to handle]
- `ERROR_CODE_2` - [Description and how to handle]

---

## Rate Limiting

[Rate limit information]

---

## Related Resources

**Official docs:** [Link]

**Related APIs:**
- [related-api.md](related-api.md)

**Skills:**
- [skill-that-uses-this.md](../../skills/category/skill.md)
```

---

## Configuration Reference Template

For documenting configuration files:

```markdown
# [Tool/Framework] Configuration Reference

Complete configuration options for [tool name].

**Referenced from**: [skill-name.md](../../skills/category/skill-name.md)

---

## Table of Contents

- [Configuration File Location](#configuration-file-location)
- [Basic Configuration](#basic-configuration)
- [Advanced Options](#advanced-options)
- [Environment Variables](#environment-variables)

---

## Configuration File Location

[Where config files live]

**Lookup order:**
1. [Location 1]
2. [Location 2]
3. [Location 3]

---

## Basic Configuration

Minimal required configuration:

```[format]
[Minimal config example]
```

**Required fields:**
- `field1` - [Description]
- `field2` - [Description]

---

## Advanced Options

### Option Category 1

**`option.name`**
- **Type:** [string/number/boolean/object]
- **Default:** `[default value]`
- **Description:** [What it does]

**Example:**
```[format]
option:
  name: value
```

---

## Environment Variables

[Environment variable reference]

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `VAR_NAME` | string | `default` | [Description] |

---

## Examples

### Example 1: [Scenario]

```[format]
[Complete config example]
```

### Example 2: [Scenario]

```[format]
[Complete config example]
```

---

## Related Resources

**Official docs:** [Link]

**Related config:**
- [related-config.md](related-config.md)
```

---

## Syntax Reference Template

For documenting language syntax:

```markdown
# [Language] - [Feature] Syntax

Complete syntax reference for [feature] in [language].

**Referenced from**: [skill-name.md](../../skills/category/skill-name.md)

---

## Overview

[Brief overview of the feature]

**When to use:** [Use cases]

**When not to use:** [Anti-patterns]

---

## Basic Syntax

```[language]
[Basic syntax example]
```

**Explanation:**
- [Element 1] - [What it does]
- [Element 2] - [What it does]

---

## Variations

### Variation 1: [Name]

```[language]
[Syntax]
```

**Use when:** [Scenario]

### Variation 2: [Name]

```[language]
[Syntax]
```

**Use when:** [Scenario]

---

## Advanced Usage

### Pattern 1: [Name]

```[language]
[Advanced example]
```

### Pattern 2: [Name]

```[language]
[Advanced example]
```

---

## Common Pitfalls

### Pitfall 1: [Description]

**Bad:**
```[language]
[Incorrect usage]
```

**Good:**
```[language]
[Correct usage]
```

---

## Related Syntax

- [related-feature.md](related-feature.md) - [Related feature]
```

---

## Framework Feature Reference Template

For documenting framework features:

```markdown
# [Framework] - [Feature Name]

Complete reference for [feature] in [framework].

**Referenced from**: [skill-name.md](../../skills/category/skill-name.md)

**Official docs**: [Link]

---

## Overview

[What this feature does and when to use it]

**Key concepts:**
- [Concept 1]
- [Concept 2]

---

## Basic Usage

```[language]
[Basic example]
```

---

## API Reference

### Function/Method 1

**Signature:**
```[language]
function name(param1: type, param2: type): returnType
```

**Parameters:**
- `param1` - [Description]
- `param2` - [Description]

**Returns:** [Description]

**Example:**
```[language]
[Usage example]
```

---

## Advanced Patterns

[Advanced usage patterns]

---

## Integration

[How this integrates with other framework features]

---

## Performance Considerations

[Performance notes if applicable]

---

## Related Features

- [related-feature.md](related-feature.md) - [How related]
```

---

## Customization Guide

### Choosing the Right Template

**Use Basic Template when:**
- Simple reference (100-300 lines)
- Single topic
- Straightforward syntax/API

**Use Detailed Template when:**
- Comprehensive reference (200-500 lines)
- Multiple subtopics
- Needs table of contents

**Use API Reference when:**
- Documenting REST/GraphQL API
- Multiple endpoints
- Request/response examples needed

**Use Configuration Reference when:**
- Config files
- Environment variables
- Multiple config options

**Use Syntax Reference when:**
- Language syntax
- Multiple variations
- Common pitfalls

**Use Framework Feature when:**
- Framework-specific features
- Complex integrations
- Performance considerations

---

## Validation Checklist

Before finalizing context, verify:

- [ ] Title clearly describes the content
- [ ] "Referenced from" links to related skills
- [ ] Related files are cross-referenced
- [ ] Table of contents if >100 lines
- [ ] Code examples are correct and complete
- [ ] Official documentation linked (if applicable)
- [ ] Version specified (if version-specific)
- [ ] File follows naming convention (kebab-case.md)
- [ ] Located in correct knowledge category
- [ ] Token count is reasonable (~1,500-5,000)

---

## Tips

**Writing good reference documentation:**
- Be comprehensive but concise
- Include working code examples
- Explain parameters clearly
- Note version-specific features
- Link to official docs
- Cross-reference related topics

**Organizing content:**
- Start with overview
- Group related items
- Use consistent structure
- Add table of contents for >100 lines
- Put most-used info first

**Code examples:**
- Complete and runnable
- Commented where helpful
- Show real-world usage
- Include error cases

---

## Examples

See complete real-world examples:
- [examples/context-example.md](examples/context-example.md) - Complete context file
- `/Users/coreyyoung/Claude/context/knowledge/frameworks/fastify/routes-api.md` - API reference example

---

## Related Resources

**Other templates:**
- [skill-template.md](skill-template.md) - For methodology/patterns

**Guidelines:**
- [best-practices.md](best-practices.md) - Detailed best practices
- [structure.md](structure.md) - PAI organization
- [token-efficiency.md](token-efficiency.md) - Token optimization
