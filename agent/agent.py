import os
import uuid
import logging
import datetime
from dotenv import load_dotenv
from typing import Optional

import asyncio
import aiohttp
from datetime import datetime

from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext
from vertexai import agent_engines

from google.adk.sessions import VertexAiSessionService, Session
from google.adk.events import Event, EventActions
from google.genai import types

from .agent_monitor import AgentMonitor

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path=env_path)

# Constants
AGENT_ENGINE_ID = os.getenv("AGENT_ENGINE_ID")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

active_monitors = {}
session_service = VertexAiSessionService()

def call_api_tool(tool_context: ToolContext) -> str:
    """
    Starts the live agent transfer in the background and immediately
    returns a message indicating the transfer is in progress.
    """
    if not AGENT_ENGINE_ID:
        raise ValueError("AGENT_ENGINE_ID environment variable not set.")
    
    async def _long_running_api_call():
        """The actual API call logic that runs in the background."""
        logger.info("[Background Task] Starting live agent transfer...")
        
        # Simulate a long network delay before making the call
        await asyncio.sleep(5)

        async with aiohttp.ClientSession() as session:
            try:
                # This is a placeholder API. In a real scenario, this would
                # be the API endpoint for your live agent service.
                async with session.get("https://api.artic.edu/api/v1/artworks/129884") as response:
                    response.raise_for_status()
                    data = await response.json()

                    # Extract the artwork title from the response
                    title = data.get("data", {}).get("title", "Unknown Artwork")
                    
                    # Simulate adding an event to the session
                    _session = await session_service.get_session(
                        app_name=AGENT_ENGINE_ID,
                        user_id=tool_context.session.user_id,
                        session_id=tool_context.session.id
                    )

                    # Add content to add to the session event
                    _part = types.Part(text=f"{title}")
                    _content=types.Content(role="model", parts=[_part])

                    # (Optional) Define state changes to update the session's state based on the API result
                    state_changes = {
                        "title": title, # Update session state if needed
                    }

                    # --- Create Event with Actions ---
                    actions_with_update = EventActions(state_delta=state_changes)
                    # represent the event as a chat interaction
                    system_event = Event(
                        invocation_id=f"live_agent_{uuid.uuid4()}",
                        author="tool", # Or 'agent', 'tool' etc.
                        actions=actions_with_update,
                        timestamp=datetime.now().timestamp(),
                        content=_content
                        # content might be None or represent the action taken
                    )

                    # --- Append the Event (This updates the state) ---
                    await session_service.append_event(_session, system_event)
                    logger.info(f"`append_event` called with explicit state delta: {state_changes}")

                    logger.info(f"[Background Task] Artwork title: {title}")
                    # In a real application, you might use the result to notify
                    # the user through another channel or update a system's state.

            except aiohttp.ClientError as e:
                logger.error(f"[Background Task] Error during API call: {e}")

    # --- Start Monitor if not already running for this session ---
    session_id = tool_context.session.id
    if session_id not in active_monitors:
        logger.info(f"Starting monitor for session: {session_id}")

        async def monitor_callback(new_events, session):
            """Analyze new events and log interesting patterns."""
            for event in new_events:
                # Only react to events from the 'tool' author
                if event.author == "tool":
                    if event.content:
                        for part in event.content.parts:
                            if part.text:
                                return f"monitor callback: {part.text}"
            return None

        monitor = AgentMonitor(
            session_service=session_service,
            app_name=AGENT_ENGINE_ID,
            user_id=tool_context.session.user_id,
            session_id=tool_context.session.id,
            app=adk_app,
            monitor_interval=1.0,
        )
        
        loop = asyncio.get_running_loop()
        loop.create_task(monitor.start_monitoring(monitor_callback))
        active_monitors[session_id] = monitor

    # Get the current running asyncio event loop.
    loop = asyncio.get_running_loop()
    
    # Create a background task that runs independently on the event loop.
    # The current function will not wait for this task to complete.
    loop.create_task(_long_running_api_call())

    # Immediately return a confirmation message to the LLM.
    # The LLM will then use this to respond to the user, so the chat is not blocked.
    return f"I am now transferring you to a live agent."

def date_time_tool() -> str:
    """Returns the current date and time in YYYY-MM-DD HH:MM:SS format."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

root_agent = LlmAgent(
    name="live_cx_agent",
    model=MODEL_NAME,
    description="Agent demo of transferring to a live agent.",
    instruction="""You are a live chat agent. When an end user requests to be transferred to a live agent
    use the `call_api_tool` tool to transfer the user to a live agent. 
    Otherwise allow them to also call a date time tool to see the current date and time.
    """,
    tools=[call_api_tool, date_time_tool],
)

# Wrap the agent in an AdkApp object for Agent Engine deployment
adk_app = agent_engines.AdkApp(
    agent=root_agent,
    enable_tracing=True,
)

