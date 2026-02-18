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

class AgentMonitor:
    """
    Monitors an agent session and can inject messages based on conditions.
    
    This pattern is useful for:
    - Safety monitoring (injecting warnings when risky behavior is detected)
    - Progress tracking (updating user on long-running tasks)
    - Multi-agent coordination (one agent monitoring another)
    - Real-time analysis and intervention
    """

    def __init__(
        self,
        session_service,
        app_name: str,
        user_id: str,
        session_id: str,
        monitor_interval: float = 1.0,
    ):
        self.session_service = session_service
        self.app_name = app_name
        self.user_id = user_id
        self.session_id = session_id
        self.monitor_interval = monitor_interval
        self.last_event_count = 0
        self.is_monitoring = False
        self.monitor_task: Optional[asyncio.Task] = None

    async def start_monitoring(self, on_new_events_callback):
        """
        Start background monitoring.
        
        Args:
            on_new_events_callback: Async function called with new events.
                                   Should return a message to inject (str) or None.
        """
        self.is_monitoring = True
        self.monitor_task = asyncio.create_task(
            self._monitor_loop(on_new_events_callback)
        )

    async def stop_monitoring(self):
        """Stop the background monitoring task."""
        self.is_monitoring = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass

    async def _monitor_loop(self, callback):
        """Internal monitoring loop."""
        while self.is_monitoring:
            try:
                # Get the current session state
                session = await self.session_service.get_session(
                    app_name=self.app_name,
                    user_id=self.user_id,
                    session_id=self.session_id,
                )

                if not session:
                    break

                current_count = len(session.events)

                # Check for new events
                if current_count > self.last_event_count:
                    new_events = session.events[self.last_event_count :]
                    self.last_event_count = current_count

                    # Call the callback to analyze new events
                    message_to_inject = await callback(new_events, session)

                    # If callback returns a message, inject it via async_stream_query
                    # to ensure the frontend updates in real-time.
                    if message_to_inject:
                        logger.info(f"Monitor wants to inject: {message_to_inject}")
                        
                        # Create a Content object to send as the message
                        _part = types.Part(text=message_to_inject)
                        _content = types.Content(role="model", parts=[_part])

                        # Use async_stream_query to inject the message and trigger UI update
                        query_result = adk_app.async_stream_query(
                            session_id=self.session_id,
                            user_id=self.user_id,
                            message=_content.to_dict(),
                        )
                        async for _ in query_result:
                            # Consuming the stream ensures the query is fully processed
                            pass
                        logger.info("Monitor injected message via async_stream_query")


                await asyncio.sleep(self.monitor_interval)

            except Exception as e:
                logger.error(f"Monitor error: {e}")
                await asyncio.sleep(self.monitor_interval)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path=env_path)

session_service = VertexAiSessionService()

# Constants
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

active_monitors = {}

def call_api_tool(tool_context: ToolContext) -> str:
    """
    Starts the live agent transfer in the background and immediately
    returns a message indicating the transfer is in progress.
    """
    
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
                    title = data.get("data", {}).get("title", "Unknown Artwork")
                    
                    # Simulate adding an event to the session
                    session = await session_service.get_session(
                        app_name=os.getenv("AGENT_ENGINE_ID"),
                        user_id=tool_context.session.user_id,
                        session_id=tool_context.session.id
                    )

                    _part = types.Part()
                    _part.text = f"{title}"

                    _content=types.Content()
                    _content.role = "model"
                    _content.parts = [ _part ]

                    state_changes = {
                        "title": title,# Update session state
                    }  

                    # --- Create Event with Actions ---
                    actions_with_update = EventActions(state_delta=state_changes)
                    # This event might represent an internal system action, not just an agent response
                    system_event = Event(
                        invocation_id=f"live_agent_{uuid.uuid4()}",
                        author="tool", # Or 'agent', 'tool' etc.
                        actions=actions_with_update,
                        timestamp=datetime.now().timestamp(),
                        content=_content
                        # content might be None or represent the action taken
                    )

                    # --- Append the Event (This updates the state) ---
                    await session_service.append_event(session, system_event)
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
            session_service,
            os.getenv("AGENT_ENGINE_ID"),
            tool_context.session.user_id,
            session_id,
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

