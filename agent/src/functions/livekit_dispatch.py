import os
from dataclasses import dataclass

from livekit import api
from livekit.protocol.agent_dispatch import AgentDispatch
from restack_ai.function import NonRetryableError, function, function_info

from dotenv import load_dotenv
# Load environment variables from a .env file
load_dotenv('.env')


@dataclass
class LivekitDispatchInput:
    room_id: str | None = None


@function.defn()
async def livekit_dispatch(function_input: LivekitDispatchInput) -> AgentDispatch:
    try:
        print("Starting livekit_dispatch function")
        print(f"Room ID: {function_input.room_id}")
        print(f"LIVEKIT_API_URL: {os.getenv('LIVEKIT_API_URL')}")
        print(f"LIVEKIT_URL: {os.getenv('LIVEKIT_URL')}")
        print(f"LIVEKIT_API_KEY set: {'Yes' if os.getenv('LIVEKIT_API_KEY') else 'No'}")
        print(f"LIVEKIT_API_SECRET set: {'Yes' if os.getenv('LIVEKIT_API_SECRET') else 'No'}")
        
        lkapi = api.LiveKitAPI(
            url=os.getenv("LIVEKIT_API_URL") or os.getenv("LIVEKIT_URL"),
            api_key=os.getenv("LIVEKIT_API_KEY"),
            api_secret=os.getenv("LIVEKIT_API_SECRET"),
        )
        print("Created LiveKit API client")

        agent_name = function_info().workflow_type
        agent_id = function_info().workflow_id
        run_id = function_info().workflow_run_id
        print(f"Agent name: {agent_name}, ID: {agent_id}, Run ID: {run_id}")

        metadata = {"agent_name": agent_name, "agent_id": agent_id, "run_id": run_id}
        print(f"Metadata: {metadata}")

        room = function_input.room_id or run_id
        print(f"Final room name: {room}")

        print("Creating dispatch...")
        dispatch = await lkapi.agent_dispatch.create_dispatch(
            api.CreateAgentDispatchRequest(
                agent_name=agent_name, room=room, metadata=str(metadata)
            )
        )
        print(f"Dispatch created: {dispatch}")

        await lkapi.aclose()
        print("LiveKit API client closed")
        return dispatch

    except Exception as e:
        error_message = f"Livekit dispatch failed: {str(e)}"
        print(f"ERROR: {error_message}")
        raise NonRetryableError(error_message) from e
