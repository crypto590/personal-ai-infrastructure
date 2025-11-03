/**
 * PAI Context Loader Hook
 *
 * This hook runs on user prompt submit to ensure Personal AI Infrastructure
 * context is properly loaded before processing requests.
 *
 * Based on Daniel Miessler's PAI architecture with progressive disclosure.
 */

import { Hook } from "@anthropic/claude-code";
import { readFileSync, existsSync } from "fs";
import { homedir } from "os";
import { join } from "path";

const hook: Hook = {
  name: "pai-context-loader",
  description: "Ensures PAI context is loaded before processing requests",

  // Run on every user prompt submit
  on: "user-prompt-submit",

  async run({ messages, updateSystemPrompt }) {
    const claudeHome = join(homedir(), ".claude");
    const contextDir = join(claudeHome, "context");

    // Core files that should always be loaded
    const coreFiles = [
      join(contextDir, "CLAUDE.md"),
      join(contextDir, "identity", "profile.md"),
      join(contextDir, "identity", "preferences.md"),
    ];

    // Check if core files exist
    const missingFiles: string[] = [];
    for (const file of coreFiles) {
      if (!existsSync(file)) {
        missingFiles.push(file);
      }
    }

    // If core files are missing, warn but don't block
    if (missingFiles.length > 0) {
      console.warn(
        `⚠️  PAI Warning: Core files not found:\n${missingFiles.join("\n")}\n` +
        `Please fill in your PAI identity files for optimal assistance.`
      );
      return { messages };
    }

    // Build context reminder for system prompt
    const contextReminder = `
# PAI Context Loaded

Before responding, ensure you have loaded:
- ~/.claude/context/CLAUDE.md (master PAI documentation)
- ~/.claude/context/identity/profile.md (user identity and expertise)
- ~/.claude/context/identity/preferences.md (working preferences)

Skills available at: ~/.claude/skills/
- Scan skill directories for metadata
- Load full skill content only when task requires it

Follow progressive disclosure principle:
1. Load skill metadata (always)
2. Load full skills (on demand)
3. Load deep context (as needed)
`;

    // Add context reminder to system prompt
    updateSystemPrompt((currentPrompt) => {
      return `${currentPrompt}\n\n${contextReminder}`;
    });

    return { messages };
  },
};

export default hook;
