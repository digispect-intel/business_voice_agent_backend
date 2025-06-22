import asyncio
import logging
import webbrowser
from pathlib import Path

from watchfiles import run_process

from src.agents.agent import AgentVoice
from src.client import client
from src.functions.livekit_dispatch import livekit_dispatch
from src.functions.llm_chat import llm_chat

import os
from dotenv import load_dotenv

# Load environment variables at the very beginning
load_dotenv()

# Print environment variables for debugging
print(f"LIVEKIT_URL: {os.environ.get('LIVEKIT_URL')}")
print(f"LIVEKIT_API_URL: {os.environ.get('LIVEKIT_API_URL')}")
print(f"LIVEKIT_API_KEY set: {'Yes' if os.environ.get('LIVEKIT_API_KEY') else 'No'}")
print(f"LIVEKIT_API_SECRET set: {'Yes' if os.environ.get('LIVEKIT_API_SECRET') else 'No'}")

async def main() -> None:
    await client.start_service(
        agents=[AgentVoice],
        functions=[
            llm_chat,
            livekit_dispatch,
        ],
    )


def run_services() -> None:
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Service interrupted by user. Exiting gracefully.")


def watch_services() -> None:
    watch_path = Path.cwd()
    logging.info("Watching %s and its subdirectories for changes...", watch_path)
    webbrowser.open("http://localhost:5233")
    run_process(watch_path, recursive=True, target=run_services)


if __name__ == "__main__":
    run_services()
