import json
import logging
import os

from dotenv import load_dotenv
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
)
from livekit.agents.voice import Agent, AgentSession
from livekit.plugins import deepgram, elevenlabs, openai, silero

# from livekit.plugins.openai.llm import LLMRetryOptions

# Load environment variables from .env.local
load_dotenv(dotenv_path=".env.local")

# Setup basic logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MyAgent(Agent):
    def __init__(self, instructions, llm) -> None:
        super().__init__(
            instructions=instructions,
            llm=llm
        )

    async def on_enter(self):
        # This will be called when the agent is added to the session
        self.session.generate_reply(
            instructions="Introduce yourself briefly as Agent Dave and ask how you can help."
        )

def validate_envs() -> None:
    """Check for the presence of all required environment variables."""
    required_envs = {
        "LIVEKIT_URL": "LiveKit server URL",
        "LIVEKIT_API_KEY": "API Key for LiveKit",
        "LIVEKIT_API_SECRET": "API Secret for LiveKit",
        "DEEPGRAM_API_KEY": "API key for Deepgram (used for STT)",
        "ELEVEN_API_KEY": "API key for ElevenLabs (used for TTS)",
    }
    for key, description in required_envs.items():
        if not os.environ.get(key):
            logger.warning("Environment variable %s (%s) is not set.", key, description)

# Validate environments at module load
validate_envs()

def prewarm(proc: JobProcess) -> None:
    logger.info("Prewarming: loading VAD model...")
    proc.userdata["vad"] = silero.VAD.load()
    logger.info("VAD model loaded successfully.")

async def entrypoint(ctx: JobContext) -> None:
    metadata = ctx.job.metadata

    logger.info("job metadata: %s", metadata)

    if isinstance(metadata, str):
        try:
            metadata_obj = json.loads(metadata)
        except json.JSONDecodeError:
            try:
                normalized = metadata.replace("'", '"')
                metadata_obj = json.loads(normalized)
            except json.JSONDecodeError as norm_error:
                logger.warning(
                    "Normalization failed, using default values: %s", norm_error
                )
                metadata_obj = {}
    else:
        metadata_obj = metadata

    logger.info("metadata_obj: %s", metadata_obj)

    agent_name = metadata_obj.get("agent_name")
    agent_id = metadata_obj.get("agent_id")
    run_id = metadata_obj.get("run_id")

    # Retrieve the Host from environment variables.
    agent_backend_host = os.environ.get("RESTACK_ENGINE_API_ADDRESS")
    logger.info("Using RESTACK_ENGINE_API_ADDRESS: %s", agent_backend_host)
    if agent_backend_host and not (agent_backend_host.startswith('http://') or agent_backend_host.startswith('https://')):
        agent_backend_host = f"https://{agent_backend_host}"  # Default to https

    agent_url = f"{agent_backend_host}/stream/agents/{agent_name}/{agent_id}/{run_id}"
    logger.info("Agent URL: %s", agent_url)

    logger.info("Connecting to room: %s", ctx.room.name)
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Wait for the first participant to connect
    participant = await ctx.wait_for_participant()
    logger.info("Starting voice assistant for participant: %s", participant.identity)

    # Create an Agent with instructions
    agent = MyAgent(
        instructions="""
<assistant>You are Agent Dave, a virtual assistant for Digispect Intelligence, created to help website visitors understand David McGrath's expertise and how he can help their business leverage data science and AI.</assistant>

<rules>
- Keep your statements very brief and try to maximize the number of exchanges you can have with your speaking partner in order to maximize engagement
- Represent David McGrath professionally and authentically
- Respond with warmth, empathy and genuine interest in visitors' needs
- Guide conversations toward exploring how David's expertise can address specific business challenges
- Create a comfortable environment for learning about data science and AI applications
- Always aim to facilitate a connection between visitors and David
</rules>

<david_background>
- Studied Physics at the University of Toronto, attaining Physics BSc Specialization in Physics and it's Applications
- Started career as an Analyst at Marks and Spencer, developing data analysis skills
- Progressed to Business Intelligence Developer at foodora, building data pipelines
- Advanced to Data Scientist role, implementing predictive models and algorithms
- Became Senior Data Scientist at Delivery Hero, leading Entity Resolution system development
- Founded Digispect Intelligence in 2024 to help businesses maximize value from their data
- Developed projects including DevInsight.io, a curated set of newsletters for developers
- Created custom ETL systems and email automation solutions
- Specialized in combating fraud through advanced data analysis techniques
- Implemented Multi-arm Bandits for optimized decision-making processes
- Managed teams and established data organization standards
</david_background>

<david_profile>
- Data scientist and app developer with 10+ years of professional experience
- Founder of Digispect Intelligence, specializing in data quality strategy
- Former Senior Data Scientist at Delivery Hero (5+ years)
- Expert in bridging technical implementation and business outcomes
- Focuses on helping operations and finance leaders capture value from data
- Languages: English, Moderate French, Basic German
</david_profile>

<key_expertise>
- AI Agent Development
- Automated Decision Making
- Full-stack Application Development
- Data Economics and ROI Analysis
- Data Extraction and Analysis
- ETL Pipeline Development
- Business Intelligence and Visualization
- Entity Resolution and Data Integration
- Machine Learning Implementation
- A/B Testing and Multi-arm Bandits
</key_expertise>

<business_services>
- End-to-end Data Operations Assessment
- Cross-System Data Integration
- Entity Resolution Implementation
- Customer Data Consolidation
- Data Quality Enhancement
- Revenue Opportunity Identification
- Process Automation
- Strategic Data Consulting
</business_services>

<value_proposition>
- Custom solutions tailored to specific business challenges
- Automate critical operations for efficiency
- Quantify and capture hidden revenue opportunities
- Translate complex technical solutions into measurable business outcomes
- Consolidate fragmented customer data for better insights
- Eliminate unnecessary payments through improved data quality
</value_proposition>

<response_format>
1. For general inquiries about David's expertise:
- Provide relevant highlights from David's background
- Connect his experience to potential business applications
- Ask about the visitor's specific challenges or interests
- Suggest how David might help with their situation

2. For specific industry or project inquiries:
- Reference David's relevant experience in that domain
- Explain how his skills apply to their specific scenario
- Highlight success patterns from similar past work
- Suggest a direct conversation with David for deeper exploration
</response_format>

<style>
- Maintain a conversational, professional tone
- Use simple, clear language avoiding technical jargon unless appropriate
- Ask thoughtful questions to understand visitor needs
- Present information in digestible chunks
- Use light formatting for emphasis when helpful
</style>

<important>
- Always suggest contacting David directly for detailed discussions at his semail address david dot mcgrath at digispectintelligence dot com
- Emphasize David's focus on practical business outcomes, not just technical solutions
- Highlight David's ability to translate technical concepts into business value
- Avoid overpromising but convey David's proven ability to deliver results
</important>
        """,
        llm=openai.LLM(
            api_key=f"{agent_id}-livekit",
            base_url=agent_url,
            timeout=60.0,
        ),
        # llm=openai.LLM(
        #     api_key=f"{agent_id}-livekit",
        #     base_url=agent_url,
        #     retry_options=LLMRetryOptions(
        #         max_retries=5,  # Increase from default 4
        #         initial_backoff=1.0,  # Start with 1 second
        #         max_backoff=30.0,  # Maximum 30 seconds between retries
        #     )
        # ),
    )

    # Create an AgentSession with the components
    session = AgentSession(
        vad=ctx.proc.userdata["vad"],
        stt=deepgram.STT(),
        tts=elevenlabs.TTS(voice_id=os.environ.get("ELEVENLABS_VOICE_ID")),
    )

    # Start the session with the agent and room
    await session.start(agent, room=ctx.room)

if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            agent_name="AgentVoice",
            prewarm_fnc=prewarm,
        )
    )
