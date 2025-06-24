# Business Voice Agent - Backend

- **Live Example:** [AI Agent Dave](https://agent-dave.pla.sh)
- **Frontend Repository:** [business_voice_agent_frontend](https://github.com/digispect-intel/business_voice_agent_frontend)
- **Interest Form** [Share your interest by completing this form](https://forms.digispectintelligence.solutions/r4RzLd)

A voice-enabled AI assistant backend for David McGrath's business website (digispectintelligence.com). This backend powers Agent Dave, providing real-time voice interaction capabilities using Restack AI.

## Overview

Agent Dave is designed to assist visitors of Digispect Intelligence by providing information about David's profile, expertise, and services. This backend handles the voice processing pipeline, AI model integration, and real-time communication.

## Prerequisites

- Docker (for running Restack)
- Python 3.10 or higher
- Restack (docker image for local development and account for web hosting)
- Livekit account (for live chat)
- Deepgram account (for speech-to-text transcription)
- ElevenLabs account (for text-to-speech and voice cloning)
- OpenAI (for AI logic) 

## Configuration

1. Copy the `.env.example` file in the `agent` subfolder and the `.env.local.example` file in the `livekit_pipeline` subfolder (and rename by removing the `.example` suffixes):

2. Configure the following services and update the values in the above mentioned files:

   ### Livekit Setup
   - Sign up at [Livekit](https://livekit.io)
   - In your `.env` and `.env.local` files:
     - Set `LIVEKIT_URL` to `WEBSOCKET_URL` value
     - Set `LIVEKIT_API_KEY` to `API_KEY` value
     - Set `LIVEKIT_API_SECRET` to `API_SECRET` value

   ### Deepgram Setup
   - Sign up at [Deepgram](https://deepgram.com)
   - Obtain an API key and add to `DEEPGRAM_API_KEY` in `.env.local` file

   ### ElevenLabs Setup
   - Sign up at [ElevenLabs](https://try.elevenlabs.io/business_voice_agent)
   - Add `ELEVEN_API_KEY` and `ELEVENLABS_VOICE_ID`to `.env.local` file

   ### OpenAI Setup
   - Sign up at [OpenAI](https://platform.openai.com)
   - Add `OPENAI_API_KEY`to `.env` file

## Installation and Setup

**Note:** Make sure to also set up the [business_voice_agent_frontend](https://github.com/digispect-intel/business_voice_agent_frontend) repository for the complete system.

### 1. Start Restack

```bash
docker run -d --pull always --name restack -p 5233:5233 -p 6233:6233 -p 7233:7233 -p 9233:9233 -p 10233:10233 ghcr.io/restackio/restack:main
```

### 2. Start Restack Agent with Voice

#### Create Python environment

Using uv:
```bash
cd agent
uv venv && source .venv/bin/activate
uv sync
uv run dev
```

Using pip:
```bash
cd agent
python -m venv .venv && source .venv/bin/activate
pip install -e .
python -c "from src.services import watch_services; watch_services()"
```

### 3. Start Livekit Voice Pipeline

#### Create Python environment

Using uv:
```bash
cd livekit_pipeline
uv venv && source .venv/bin/activate
uv sync
uv run python src/pipeline.py dev
```

Using pip:
```bash
cd livekit_pipeline
python -m venv .venv && source .venv/bin/activate
pip install -e .
python src/pipeline.py dev
```

## Usage

This backend works in conjunction with the [business_voice_agent_frontend](https://github.com/digispect-intel/business_voice_agent_frontend). Please refer to the frontend repository for complete usage instructions on how to interact with the voice assistant system.

## Deployment

To deploy on Restack Cloud:
1. Create an account at https://console.restack.io
2. Follow the deployment instructions in the [Restack documentation](https://docs.restack.io/restack-cloud/introduction)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For questions or support, contact david.mcgrath@digispectintelligence.com

## References

This repo is based on the examples here:
- https://github.com/AnswerDotAI/fasthtml-example
- https://github.com/restackio/examples-python/tree/main/agent_voice/livekit
- https://github.com/livekit/agents/tree/main/examples/voice_agents
- https://github.com/livekit/client-sdk-js/tree/main/examples