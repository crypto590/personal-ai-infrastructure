# Voice Server Architecture Analysis

**Date:** 2025-11-16
**Status:** Under Review
**Decision:** Pending

---

## Current Implementation: Centralized Voice Server

### Architecture
```bash
curl -X POST http://localhost:8888/notify \
  -H "Content-Type: application/json" \
  -d '{"message":"Task complete","voice_id":"O4lTuRmkE5LyjL2YhMIg","voice_enabled":true}'
```

### Pros
- ✅ Centralized voice routing
- ✅ Per-agent voice ID customization
- ✅ Can add caching/queuing/rate-limiting
- ✅ Separates concerns (hooks → server → TTS)
- ✅ Single point for voice management

### Cons
- ❌ Requires voice server running (dependency)
- ❌ More complex infrastructure
- ❌ Another point of failure
- ❌ Network overhead for local calls

---

## Alternative: Direct TTS Utility (Disler's Approach)

**Reference:** https://github.com/disler/claude-code-hooks-mastery/tree/main/.claude/hooks/utils

### Architecture
```python
# hooks/utils/tts/elevenlabs_tts.py - Standalone script
# hooks/notification.py calls it directly
subprocess.run(["uv", "run", tts_script, "Your message"])
```

### Pros
- ✅ No server needed - direct API calls
- ✅ Simpler architecture - utilities in hooks/utils/
- ✅ Auto-selects TTS provider (ElevenLabs → OpenAI → pyttsx3)
- ✅ Works offline with pyttsx3 fallback
- ✅ Less infrastructure to maintain

### Cons
- ❌ API call latency on every notification
- ❌ No voice ID customization per agent (hardcoded in script)
- ❌ Less control over response format
- ❌ Would need multiple scripts for multiple voices

---

## Hybrid Approach (Potential Solution)

### Concept
Keep voice server for centralized control, but add utility wrapper for simpler calls:

```python
# ~/.claude/hooks/utils/notify.py
import subprocess
import json

def notify(message, voice_id="O4lTuRmkE5LyjL2YhMIg"):
    """Simple wrapper for voice server notifications"""
    subprocess.run([
        "curl", "-X", "POST", "http://localhost:8888/notify",
        "-H", "Content-Type: application/json",
        "-d", json.dumps({
            "message": message,
            "voice_id": voice_id,
            "voice_enabled": True
        })
    ])
```

### Usage in Hooks
```python
from utils.notify import notify
notify("Task complete")  # Uses default Alex voice
notify("Analysis done", voice_id="lpcesEa7Zyjkgsrd7I32")  # CTO voice
```

### Benefits
- ✅ Keeps centralized voice routing
- ✅ Simplifies hook code
- ✅ Maintains per-agent voice customization
- ✅ Easy to mock/disable for testing

---

## Key Files from Disler's Repo

### TTS Utilities
- `hooks/utils/tts/elevenlabs_tts.py` - ElevenLabs direct integration
- `hooks/utils/tts/openai_tts.py` - OpenAI TTS fallback
- `hooks/utils/tts/pyttsx3_tts.py` - Offline fallback

### Hook Integration
- `hooks/notification.py` - Auto-selects TTS provider based on API keys
- Smart provider selection: ElevenLabs → OpenAI → pyttsx3

### Code Sample
```python
# From notification.py
def get_tts_script_path():
    """Priority order: ElevenLabs > OpenAI > pyttsx3"""
    if os.getenv('ELEVENLABS_API_KEY'):
        return "hooks/utils/tts/elevenlabs_tts.py"
    if os.getenv('OPENAI_API_KEY'):
        return "hooks/utils/tts/openai_tts.py"
    return "hooks/utils/tts/pyttsx3_tts.py"
```

---

## Decision Points

### When to Use Voice Server (Current)
1. Need multiple distinct agent voices
2. Want centralized voice management
3. Plan to add caching/queuing
4. Voice routing logic is complex

### When to Use Direct Utilities (Disler's)
1. Single voice for all notifications
2. Minimize infrastructure dependencies
3. Want offline fallback support
4. Simpler setup for new users

### When to Use Hybrid
1. Want both centralized control AND simple API
2. Multiple agents with different voices
3. Need flexibility to switch implementations
4. Want to maintain upgrade path

---

## Current Voice Mapping

### Agent Voice IDs (ElevenLabs)
- Alex: `O4lTuRmkE5LyjL2YhMIg`
- cto-advisor: `lpcesEa7Zyjkgsrd7I32`
- claude-researcher: TBD
- gemini-researcher: TBD
- pentester: TBD
- engineer: TBD
- principal-engineer: TBD
- designer: TBD
- architect: TBD
- artist: TBD
- writer: TBD

---

## Next Steps (When Ready)

1. **Test Disler's approach** - Clone and test his utilities
2. **Measure latency** - Compare server vs direct API calls
3. **Prototype hybrid** - Build utility wrapper for voice server
4. **Document trade-offs** - Write migration guide
5. **Make decision** - Choose approach based on actual usage patterns

---

## Resources

- Disler's Repo: https://github.com/disler/claude-code-hooks-mastery
- ElevenLabs Turbo v2.5: Used in their implementation
- Voice Server Location: `http://localhost:8888/notify`

---

## Notes

- Voice server provides more control for multi-agent setup
- Disler's approach is simpler for single-voice scenarios
- Hybrid could provide best of both worlds
- Need actual usage data to make informed decision
