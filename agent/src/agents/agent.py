import os
from datetime import timedelta
import asyncio

from pydantic import BaseModel, Field
from restack_ai.agent import NonRetryableError, agent, import_functions, log

with import_functions():
    from src.functions.livekit_dispatch import LivekitDispatchInput, livekit_dispatch
    from src.functions.llm_chat import LlmChatInput, Message, llm_chat

DEFAULT_AGENT_TIMEOUT = int(os.getenv("DEFAULT_AGENT_TIMEOUT_MINUTES", "5"))

class MessagesEvent(BaseModel):
    messages: list[Message]


class EndEvent(BaseModel):
    end: bool


class AgentVoiceInput(BaseModel):
    room_id: str

@agent.defn()
class AgentVoice:
    def __init__(self) -> None:
        self.end = False
        self.messages: list[Message] = []

    @agent.event
    async def messages(self, messages_event: MessagesEvent) -> list[Message]:
        log.info(f"Received message: {messages_event.messages}")
        self.messages.extend(messages_event.messages)
        try:
            assistant_message = await agent.step(
                function=llm_chat,
                function_input=LlmChatInput(messages=self.messages),
                start_to_close_timeout=timedelta(minutes=2),
            )
        except Exception as e:
            error_message = f"Error during llm_chat: {e}"
            raise NonRetryableError(error_message) from e
        else:
            self.messages.append(Message(role="assistant", content=str(assistant_message)))
            return self.messages

    @agent.event
    async def end(self, end: EndEvent) -> EndEvent:
        log.info("Received end")
        self.end = True
        return end

    @agent.run
    async def run(self, agent_input: AgentVoiceInput = None) -> None:
        log.info(f"Received agent_input: {agent_input}")

        # Set a background task to cleanly end the agent after 5 minutes
        async def auto_end():
            await asyncio.sleep(DEFAULT_AGENT_TIMEOUT*60)
            log.info(f"Agent auto-ended after {DEFAULT_AGENT_TIMEOUT} minutes")
            self.end = True
        try:
            # End task successfully after timeout
            # asyncio.create_task(auto_end())
            await agent.step(function=livekit_dispatch, function_input=LivekitDispatchInput(room_id=agent_input.room_id))

            # End task with error after timeout
            # await agent.condition(lambda: self.end, timeout=timedelta(minutes=DEFAULT_AGENT_TIMEOUT))
        except Exception as e:
            raise NonRetryableError(f"Error: {e}") from e
        else:
            await agent.condition(lambda: self.end)
