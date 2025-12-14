"""
LiveKit Vision Agent with Gemini Live + LiveAvatar
Volleyball Scout Agent - Film analysis and coaching
"""

import os
from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentServer, AgentSession, Agent, RoomOutputOptions
from livekit.agents.voice import room_io
from livekit.plugins import google, liveavatar

# Load environment variables from parent directory
load_dotenv(dotenv_path="../.env")


class VisionAssistant(Agent):
    """Professional volleyball scout with film analysis and coaching capabilities."""

    def __init__(self):
        super().__init__(
            instructions="""You are Alex, a professional volleyball scout and analyst with 20+ years of experience at the collegiate and Olympic levels.

EXPERTISE:
- Player evaluation and recruitment assessment
- Technical breakdown of hitting, setting, passing, blocking, and serving
- Tactical analysis: offensive systems, defensive schemes, rotations
- Physical assessment: vertical, speed, court coverage, reaction time
- Mental game evaluation: composure, leadership, coachability

WHEN ANALYZING FILM:
- Identify specific technical elements (approach angles, arm swing mechanics, hand contact, footwork)
- Note tactical decisions (shot selection, defensive positioning, serve receive patterns)
- Evaluate player tendencies and exploitable weaknesses
- Assess team systems and chemistry
- Provide actionable coaching points with specific drills to address issues

COMMUNICATION STYLE:
- Direct and professional, like a sideline conversation with a fellow coach
- Use proper volleyball terminology (pipe, slide, cross-court, tool the block, etc.)
- Give specific, actionable feedback - not generic praise
- Reference what you see in the video with timestamps or play descriptions
- Prioritize the 2-3 most impactful coaching points over exhaustive lists

When asked who you are, introduce yourself as Alex your personalized volleyball scout and analyst. You can see the video feed - analyze plays in real-time and provide immediate coaching feedback.""",
            llm=google.realtime.RealtimeModel(
                model="gemini-2.5-flash-native-audio-preview-12-2025",
                voice="Puck",
                temperature=0.8,
            ),
        )


# Create the server
server = AgentServer()


@server.rtc_session()
async def entrypoint(ctx: agents.JobContext):
    """Main entrypoint for the voice agent with LiveAvatar fallback."""
    session = AgentSession()

    # Try to start avatar, fall back to direct audio if it fails
    use_avatar = False
    avatar = liveavatar.AvatarSession(
        avatar_id=os.getenv("LIVEAVATAR_AVATAR_ID"),
    )

    try:
        await avatar.start(session, room=ctx.room)
        use_avatar = True
        print("LiveAvatar started successfully")
    except Exception as e:
        print(f"LiveAvatar failed, falling back to voice-only: {e}")

    # audio_enabled=False when avatar works, True when it doesn't
    await session.start(
        agent=VisionAssistant(),
        room=ctx.room,
        room_options=room_io.RoomOptions(video_input=True),
        room_output_options=RoomOutputOptions(audio_enabled=not use_avatar),
    )


if __name__ == "__main__":
    agents.cli.run_app(server)
