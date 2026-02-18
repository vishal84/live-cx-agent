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

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

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
        app: agent_engines.AdkApp,
        monitor_interval: float = 1.0,
    ):
        self.session_service = session_service
        self.app_name = app_name
        self.user_id = user_id
        self.session_id = session_id
        self.monitor_interval = monitor_interval
        self.last_event_count = 0
        self.is_monitoring = False
        self.app = app
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
                        _content = types.Content(role="user", parts=[_part])

                        # Use async_stream_query to inject the message and trigger UI update
                        query_result = self.app.async_stream_query(
                            session_id=self.session_id,
                            user_id=self.user_id,
                            message=_content,
                        )
                        async for _ in query_result:
                            # Consuming the stream ensures the query is fully processed
                            pass
                        logger.info("Monitor injected message via async_stream_query")


                await asyncio.sleep(self.monitor_interval)

            except Exception as e:
                logger.error(f"Monitor error: {e}")
                await asyncio.sleep(self.monitor_interval)
