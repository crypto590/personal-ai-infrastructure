# PAI External Resources

Links to external documentation, repositories, and articles about Personal AI Infrastructure and Skills.

---

## Daniel Miessler's PAI

### Current Repository
**[github.com/danielmiessler/PAI](https://github.com/danielmiessler/PAI)**

Daniel's production PAI system including:
- Skills framework
- Commands system
- Agents (Perplexity, Claude, Gemini researchers)
- Voice system (macOS native voices)
- MCP integrations

### Articles
**[Building a Personal AI Infrastructure](https://danielmiessler.com/blog/personal-ai-infrastructure)**

Comprehensive walkthrough of:
- Why PAI matters
- Architecture decisions
- His personal system "Kai"
- Real-world usage examples

### Key Takeaways from Daniel's Work

**Philosophy:**
- AI should augment humans, not replace them
- Your PAI should be uniquely yours
- Transparency and portability matter

**Architecture:**
- Progressive disclosure (92.5% token reduction)
- Skills-based modular design
- Plain text, filesystem-based

**Evolution:**
- Started with context files
- Migrated to Anthropic Skills
- Continuously refined based on real usage

---

## Anthropic Official Documentation

**Note:** Anthropic-specific technical details for creating Skills are in:  
`~/Claude/skills/core/skill-creation/ANTHROPIC_REFERENCE.md`

### High-Level Resources
- [Agent Skills Overview](https://docs.anthropic.com/en/docs/agents-and-tools/agent-skills/overview)
- [Engineering Blog: Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

---

## Other PAI Implementations

### Daniel's Previous Versions
- [Personal_AI_Infrastructure](https://github.com/danielmiessler/Personal_AI_Infrastructure) - Earlier architecture

### Related Projects by Daniel
- [Fabric](https://github.com/danielmiessler/Fabric) - AI prompt framework (~30K stars)
- [Telos](https://github.com/danielmiessler/Telos) - Deep context framework

---

## Community Resources

- [Anthropic Skills Cookbook](https://github.com/anthropics/claude-cookbooks/tree/main/skills)
- [Claude Code Plugins](https://github.com/anthropics/claude-code-plugins)

---

## How This PAI Differs from Daniel's

**What we share:**
- Progressive disclosure philosophy
- Skills-based architecture
- ~/.claude directory structure
- "Build once, use everywhere"

**What's different:**
- This PAI: Skills + Context (knowledge management focus)
- Daniel's PAI: Skills + Commands + Agents + Voice + MCPs (full AI infrastructure)

**Both are valid!** Choose the complexity level you need.

---

## Updates

**Last updated:** November 4, 2025

**Check periodically for:**
- Daniel's PAI updates
- New Anthropic features
- Community contributions