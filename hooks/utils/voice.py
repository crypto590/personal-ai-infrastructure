"""
Shared voice utility — agent-aware voice via POST /speak.

Replaces per-hook hardcoded ALEX_VOICE_ID and VOICE_SERVER_URL.
Uses the voice server's agent routing (voices.json) instead of raw voice IDs.
"""

import subprocess

import requests

VOICE_SERVER_URL = "http://localhost:8888"

# Map Claude Code agents/subagent_types → voice server personas (from voices.json)
AGENT_VOICE_MAP = {
    # Main
    "alex": "alex",
    # Code/CTO group
    "code-review": "cto",
    "general-purpose": "cto",
    "react-developer": "cto",
    "nextjs-app-developer": "cto",
    "swift-specialist": "cto",
    "kotlin-specialist": "cto",
    "fastify-specialist": "cto",
    "code-simplifier": "cto",
    "devops-platform-engineer": "cto",
    "database-engineer": "cto",
    "github-manager": "cto",
    "performance-engineer": "cto",
    "tool-router": "cto",
    # Research group
    "research-specialist": "researcher",
    "Explore": "researcher",
    # Architecture group
    "plan-architect": "architect",
    "Plan": "architect",
    "plan-design": "architect",
    "plan-eng": "architect",
    "plan-product": "architect",
    # Security group
    "security-engineer": "pentester",
    "test-automation-engineer": "pentester",
    # Writer group
    "context-compactor": "writer",
}


def speak(message: str, agent: str = "alex", timeout: int = 3) -> bool:
    """Agent-aware voice via POST /speak (auto-selects voice from voices.json)."""
    try:
        voice_agent = AGENT_VOICE_MAP.get(agent, "alex")
        response = requests.post(
            f"{VOICE_SERVER_URL}/speak",
            json={"message": message, "agent": voice_agent},
            timeout=timeout,
        )
        return response.status_code == 200
    except Exception:
        return False


def notify_system(message: str, title: str = "Alex"):
    """macOS system notification banner alongside voice."""
    try:
        safe_msg = message.replace('"', '\\"').replace("'", "\\'")
        safe_title = title.replace('"', '\\"').replace("'", "\\'")
        subprocess.run(
            [
                "osascript", "-e",
                f'display notification "{safe_msg}" with title "{safe_title}"',
            ],
            timeout=5,
            capture_output=True,
        )
    except Exception:
        pass


def speak_and_notify(message: str, agent: str = "alex", title: str = "Alex") -> bool:
    """Send both voice and system notification."""
    notify_system(message, title=title)
    return speak(message, agent=agent)


def is_server_healthy(timeout: int = 2) -> bool:
    """Check if the voice server is running."""
    try:
        r = requests.get(f"{VOICE_SERVER_URL}/health", timeout=timeout)
        return r.status_code == 200
    except Exception:
        return False
