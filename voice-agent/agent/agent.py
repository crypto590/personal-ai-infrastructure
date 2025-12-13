"""
LiveKit Vision Agent with Gemini Live
Voice + video agent implementation (Phase 4)
"""

from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentServer, AgentSession, Agent
from livekit.agents.voice import room_io
from livekit.plugins import google

# Load environment variables from parent directory
load_dotenv(dotenv_path="../.env")


class VisionAssistant(Agent):
    """Alex - an AI assistant with voice and vision capabilities powered by Gemini Live."""

    def __init__(self):
        super().__init__(
            instructions="""You are Alex, a helpful AI assistant with vision capabilities.
You are friendly, professional, and conversational.
Keep your responses concise and natural for voice interaction.
When asked who you are, introduce yourself as Alex.

You can see through the user's camera. When they ask you to look at something,
describe what you see accurately. If asked about visual details, reference what
you observe. Be proactive about mentioning relevant things you notice that could
help the conversation.""",
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
    """Main entrypoint for the voice agent."""
    # Create agent session
    session = AgentSession()

    # Start the session with video input enabled
    await session.start(
        agent=VisionAssistant(),
        room=ctx.room,
        room_options=room_io.RoomOptions(
            video_input=True,
        ),
    )


if __name__ == "__main__":
    agents.cli.run_app(server)
