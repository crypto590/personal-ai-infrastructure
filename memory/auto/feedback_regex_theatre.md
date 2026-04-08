---
name: Regex theatre is not security
description: Pattern-based command blocks (e.g., rm -rf regex) feel safe but don't protect — structural path rules and audit logs are what matter
type: feedback
---

Do not propose command-pattern regex blocks as security. Don't add rules like `rm -rf`, `chmod 777`, or similar shell-pattern matchers to a security guard unless they meet BOTH criteria: irreversible AND zero legitimate use in the target environment. Almost nothing meets that bar in a dev environment.

**Why:** Frostbark crystallized it: "regex theatre feels safe but protects nothing." Pattern blocks on command shape are trivially bypassable (`rm --recursive --force`, `find -delete`, `perl unlink`, `python shutil.rmtree`, `node fs.rmSync`, etc.) and they block legitimate work. Also: Claude Code's native permission prompts are already the real approval gate — a regex layer on top is redundant theater for intentional use and useless against actual misuse. The related incident ($578 token cascade, March 17) was not prevented by *any* regex block — it happened via API subprocess spawning, a completely different class of failure.

**How to apply:**
- Structural protection beats pattern matching. `zero_access` on `~/.ssh`, `~/.gnupg`, AWS creds, keychain paths, `~/.claude/` (from outside it), etc. — these are what actually stop incidents. Strengthen these.
- `read_only` / `no_delete` path rules are also structural — keep and extend.
- Alert/audit tier is fine for notable patterns (`curl | sh`, `git push --force`, `drop table`) — logged but not blocked. Claude Code prompts the user; the guard leaves a trail.
- Block tier should contain ONLY: `mkfs.*`, fork bombs, `chmod -R 777 /` (tightened), and raw block-device writes. Tiny list, narrow regex, unambiguous.
- Never add a new command-pattern block to "fix" a specific incident. Ask: would structural path protection have caught it? That's the real fix.
- Red flag phrases: "block rm -rf", "prevent dangerous commands", "detect destructive patterns". Translate those to: "which path should be zero_access?"
