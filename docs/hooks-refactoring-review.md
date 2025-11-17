# Hooks Refactoring Review

**Date**: November 16, 2025
**Reviewer**: Alex
**Topic**: Shell Script to Python Migration & Logging Strategy

---

## Current Hooks Inventory

### Shell Scripts (6)
1. `auto-restore.sh` - Auto-restore autopilot state on session start
2. `context-monitor.sh` - Monitor context usage and warn at threshold
3. `agent-voice.sh` - Voice notifications when agents complete tasks
4. `agent-voice-post-tool.sh` - PostToolUse voice notifications for Task tool
5. `permission-needed.sh` - Voice notification for permission requests
6. `user-input-needed.sh` - Voice notification before user input required

### Python Scripts (4)
1. `context-loader.py` - Context loading logic
2. `post_tool_use.py` - Post tool use processing
3. `pre_compact.py` - Pre-compaction hook
4. `pre_tool_use.py` - Pre tool use hook

---

## Refactoring Recommendations

### HIGH PRIORITY - Should Refactor to Python

**1. `agent-voice.sh`**
- **Why**: Complex JSON parsing using embedded Python snippets
- **Current Issues**:
  - Mixing shell and Python makes debugging harder
  - Regex pattern matching already in Python
  - Voice ID mapping would be cleaner in Python dict
- **Benefits**:
  - Single language for JSON handling
  - Better error handling with try/except
  - Easier to add logging
  - Voice ID configuration can use JSON file

**2. `agent-voice-post-tool.sh`**
- **Why**: Same complexity as agent-voice.sh
- **Current Issues**:
  - Embedded Python for JSON parsing
  - Complex pattern matching for completion messages
  - Voice mapping hardcoded
- **Benefits**:
  - Consistent with agent-voice.sh refactor
  - Could share voice mapping module
  - Better type safety with dataclasses

**3. `auto-restore.sh`**
- **Why**: JSON parsing with grep is fragile
- **Current Issues**:
  - Using grep with regex on JSON (breaks on complex values)
  - Error-prone string extraction from JSON
- **Benefits**:
  - Proper JSON parsing with Python's json module
  - Better validation of state file structure
  - Easier to extend with additional fields

---

### MEDIUM PRIORITY - Could Refactor

**4. `permission-needed.sh`**
- **Why**: Simple but uses embedded Python already
- **Benefits**: Consistency with other hooks

**5. `context-monitor.sh`**
- **Why**: Environment variable access simple in Python
- **Benefits**:
  - Better numeric comparison
  - Easier threshold configuration
  - Consistent logging with other hooks

---

### LOW PRIORITY - Keep as Shell (Optional)

**6. `user-input-needed.sh`**
- **Why**: Very simple, just sends notification
- **Note**: Has debug logging to /tmp already
- **Decision**: Could convert for uniformity, but not urgent

---

## Logging Recommendations

### Hooks That Need Logging

All hooks should have structured logging:

1. **auto-restore.sh**
   - Log state file detection
   - Log restoration prompts sent
   - Log state file issues (corrupt JSON, missing fields)

2. **context-monitor.sh**
   - Log context threshold checks
   - Log warning triggers
   - Log state file creation/existence

3. **agent-voice.sh**
   - Log agent name detection
   - Log voice ID selection
   - Log notification attempts (success/failure)
   - Log pattern matching failures

4. **agent-voice-post-tool.sh**
   - Log task completion extraction
   - Log voice routing decisions
   - Log notification delivery

5. **permission-needed.sh**
   - Log permission request events
   - Log notification delivery

6. **pre_tool_use.py**
   - Enhance existing logging if present
   - Log tool invocations

7. **post_tool_use.py**
   - Log tool completion events
   - Log any processing errors

8. **pre_compact.py**
   - Log compaction trigger events
   - Log context state before compaction

---

## Logging Strategy

### Directory Structure
```
~/.claude/logs/hooks/
├── auto-restore.log
├── context-monitor.log
├── voice-notifications.log  # Combined for all voice hooks
├── pre-tool-use.log
├── post-tool-use.log
└── pre-compact.log
```

### Log Format (Standardized)
```
[TIMESTAMP] [HOOK_NAME] [LEVEL] [EVENT_TYPE] Message: details
```

**Example:**
```
[2025-11-16 14:32:01] [auto-restore] [INFO] [STATE_DETECTED] State file found, task: "Build autopilot system"
[2025-11-16 14:32:01] [auto-restore] [INFO] [VOICE_SENT] Notification sent to voice server
[2025-11-16 14:33:15] [agent-voice] [INFO] [AGENT_COMPLETE] Agent: cto-advisor, VoiceID: lpcesEa7Zyjkgsrd7I32
[2025-11-16 14:33:15] [agent-voice] [ERROR] [VOICE_FAILED] Notification failed: Connection refused
```

### Log Levels
- **DEBUG**: Detailed diagnostic info (JSON parsing, regex matches)
- **INFO**: Normal operations (state detected, notifications sent)
- **WARN**: Unexpected but handled (missing fields, fallback voice ID)
- **ERROR**: Failures (JSON parse errors, notification failures)

### Rotation Strategy
- Use Python's `logging.handlers.RotatingFileHandler`
- Max size: 1MB per file
- Keep last 3 backup files
- Total max: ~4MB per hook (prevents bloat)

---

## Proposed Python Architecture

### Shared Utilities Module
Create `~/.claude/hooks/utils/` with:

**`voice.py`**
```python
"""Voice notification utilities"""
import json
import requests
from typing import Optional

VOICE_MAP = {
    'cto-advisor': 'lpcesEa7Zyjkgsrd7I32',
    'alex': 'O4lTuRmkE5LyjL2YhMIg',
    # ... other agents
}

def get_voice_id(agent_name: str) -> str:
    """Get voice ID for agent, fallback to Alex"""
    return VOICE_MAP.get(agent_name.lower(), VOICE_MAP['alex'])

def send_notification(message: str, voice_id: str, voice_enabled: bool = True) -> bool:
    """Send voice notification to local server"""
    try:
        response = requests.post(
            'http://localhost:8888/notify',
            json={'message': message, 'voice_id': voice_id, 'voice_enabled': voice_enabled},
            timeout=2
        )
        return response.status_code == 200
    except Exception as e:
        return False
```

**`logging_config.py`**
```python
"""Centralized logging configuration for hooks"""
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOGS_DIR = Path.home() / '.claude' / 'logs' / 'hooks'
LOGS_DIR.mkdir(parents=True, exist_ok=True)

def get_logger(hook_name: str) -> logging.Logger:
    """Get configured logger for hook"""
    logger = logging.getLogger(hook_name)
    logger.setLevel(logging.DEBUG)

    handler = RotatingFileHandler(
        LOGS_DIR / f'{hook_name}.log',
        maxBytes=1_000_000,  # 1MB
        backupCount=3
    )

    formatter = logging.Formatter(
        '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
```

**`json_utils.py`**
```python
"""JSON parsing utilities for hooks"""
import json
import sys
from typing import Any, Optional

def read_stdin_json() -> Optional[dict]:
    """Read and parse JSON from stdin"""
    try:
        return json.load(sys.stdin)
    except json.JSONDecodeError:
        return None
```

### Refactored Hook Structure

Each Python hook follows this pattern:

```python
#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["requests"]
# ///

"""Hook description"""
import sys
from pathlib import Path

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent / 'utils'))

from logging_config import get_logger
from voice import send_notification, get_voice_id
from json_utils import read_stdin_json

logger = get_logger('hook-name')

def main():
    logger.info("Hook triggered")

    # Hook logic here
    data = read_stdin_json()
    if not data:
        logger.error("Failed to parse JSON input")
        return

    # Process and send notification
    # ...

    logger.info("Hook completed")

if __name__ == '__main__':
    main()
```

---

## Migration Plan

### Phase 1: Infrastructure (Day 1)
- [ ] Create `~/.claude/hooks/utils/` directory
- [ ] Implement shared utilities:
  - [ ] `voice.py`
  - [ ] `logging_config.py`
  - [ ] `json_utils.py`
- [ ] Create `~/.claude/logs/hooks/` directory
- [ ] Test utilities in isolation

### Phase 2: High Priority Hooks (Days 2-3)
- [ ] Refactor `agent-voice.sh` → `agent-voice.py`
- [ ] Refactor `agent-voice-post-tool.sh` → `agent-voice-post-tool.py`
- [ ] Refactor `auto-restore.sh` → `auto-restore.py`
- [ ] Add comprehensive logging to each
- [ ] Test each hook in live environment
- [ ] Update `settings.json` hook configuration

### Phase 3: Medium Priority Hooks (Day 4)
- [ ] Refactor `permission-needed.sh` → `permission-needed.py`
- [ ] Refactor `context-monitor.sh` → `context-monitor.py`
- [ ] Add logging
- [ ] Test and update configuration

### Phase 4: Enhancement (Day 5)
- [ ] Add logging to existing Python hooks:
  - [ ] `pre_tool_use.py`
  - [ ] `post_tool_use.py`
  - [ ] `pre_compact.py`
- [ ] Optionally refactor `user-input-needed.sh`
- [ ] Add log rotation monitoring

### Phase 5: Cleanup (Day 6)
- [ ] Remove old `.sh` files after verification
- [ ] Document new hook architecture
- [ ] Create troubleshooting guide
- [ ] Update PAI documentation

---

## Benefits of Migration

### Code Quality
- **Single Language**: All hooks in Python (except optional simple ones)
- **Type Safety**: Use type hints and dataclasses
- **Error Handling**: Proper try/except instead of shell exit codes
- **Testing**: Easier to write unit tests

### Maintainability
- **Shared Code**: DRY principle with utils module
- **Configuration**: Central voice ID mapping
- **Debugging**: Structured logging across all hooks
- **Documentation**: Python docstrings

### Performance
- **Faster Startup**: No shell subprocess spawning for Python parsing
- **Better JSON**: Native JSON parsing vs grep regex
- **Async Capable**: Can add async/await if needed for notifications

### Operations
- **Log Rotation**: Automatic with Python logging
- **Monitoring**: Structured logs easier to parse/analyze
- **Debugging**: Better stack traces and error context

---

## Risks & Mitigations

### Risk: Breaking existing hooks during migration
**Mitigation**:
- Keep `.sh` files as backup during testing
- Test each hook thoroughly before removing shell version
- Update `settings.json` one hook at a time

### Risk: Python dependencies not available
**Mitigation**:
- Use uv inline script dependencies
- Only require `requests` (standard, reliable)
- Document Python version requirement

### Risk: Logging fills disk
**Mitigation**:
- Implement log rotation (1MB max, 3 backups)
- Monitor logs/ directory size
- Add cleanup to periodic maintenance

### Risk: Performance regression
**Mitigation**:
- Benchmark hook execution time before/after
- Ensure non-blocking notification sends
- Profile if needed

---

## Decision Required

**Recommended Approach**: Execute full migration (Phases 1-5)

**Rationale**:
1. Current shell scripts already embed Python - might as well go all-in
2. Logging is essential for debugging production issues
3. Uniformity makes maintenance easier
4. Shared utilities reduce code duplication
5. Better foundation for future hook development

**Alternative**: Minimal approach (just add logging to existing scripts)
- Faster to implement
- Less disruptive
- But misses opportunity for architectural improvement

---

## Next Steps

1. **Get approval** for full migration vs minimal approach
2. **Set timeline** - 6 days for full migration, or 2 days for logging only
3. **Create utils module** and test infrastructure
4. **Begin Phase 1** - infrastructure setup

---

**Decision**: Pending user approval
