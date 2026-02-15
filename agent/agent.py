import os
import logging
import asyncio
from datetime import datetime
from google.adk.agents import LlmAgent
from pathlib import Path
from dotenv import load_dotenv
from vertexai import agent_engines

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Constants
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

async def live_agent_transfer() -> str:
    """Transfers the user to a live agent."""
    await asyncio.sleep(5)
    return "You're being transferred to a live agent."

def date_time_tool() -> str:
    """Returns the current date and time in YYYY-MM-DD HH:MM:SS format."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

root_agent = LlmAgent(
    name="Reporter",
    model=MODEL_NAME,
    description="Live agent",
    instruction="""You are a live chat agent. When an end user requests to be transferred to a live agent
    use the `live_agent_transfer` tool to transfer the user to a live agent. Otherwise allow them to also
    call a date time tool to see the current date and time.
    """,
    tools=[live_agent_transfer, date_time_tool]
)

# Wrap the agent in an AdkApp object for Agent Engine deployment
adk_app = agent_engines.AdkApp(
    agent=root_agent,
    enable_tracing=True,
)
