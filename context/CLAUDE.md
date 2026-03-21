# Personal AI Infrastructure (PAI)

Architecture based on Daniel Miessler's PAI: https://danielmiessler.com/blog/personal-ai-infrastructure

## Progressive Disclosure

Load only what's needed, when needed:

1. **Skill descriptions** — always loaded (~100 tokens each). Enough to know what's available.
2. **Skill body** — loads when invoked. Full implementation details.
3. **Context files** — load on demand when the task requires deeper knowledge.

## Directory Structure

```
~/.claude/
├── skills/                  # Capabilities (each is dir/SKILL.md)
│   ├── core/                # Alex identity + orchestration
│   └── [skill-name]/        # Domain-specific skills
├── context/                 # On-demand knowledge
│   ├── identity/            # User profile + preferences
│   │   ├── profile.md       # Background, expertise, current focus
│   │   └── preferences.md   # Communication, code style, problem solving
│   └── knowledge/           # Reference materials
│       ├── orchestration/   # Delegation guide, agent routing
│       ├── patterns/        # Clean code rules, design patterns
│       └── languages/       # Language-specific conventions
├── agents/                  # Agent definitions
├── hooks/                   # Event hooks
└── [system files]           # Runtime (git-ignored)
```

## Key Principles

- **Single source of truth** — knowledge lives in ONE place, projects reference PAI
- **Skills are folders** — use file system for progressive disclosure (references/, assets/, workflows/)
- **Context is on-demand** — only load identity/knowledge files when the task requires them
- **Modular and composable** — skills combine, context files cross-reference
