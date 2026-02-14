import logging
from datetime import datetime
from google.adk.agents import LlmAgent

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Constants
MODEL_NAME = "gemini-2.5-flash"

def live_agent_transfer():
    """Transfers the user to a live agent."""
    return "Live agent transfer"


def date_time_tool() -> str:
    """Returns the current date and time in YYYY-MM-DD HH:MM:SS format."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


root_agent = LlmAgent(
    name="Reporter",
    model=MODEL_NAME,
    instruction="""You are a live chat agent. When an end user requests to be transferred to a live agent
    use the `live_agent_transfer` tool to transfer the user to a live agent. Otherwise allow them to also
    call a date time tool to see the current date and time.
    """,
    tools=[live_agent_transfer, date_time_tool]
)

from vertexai import agent_engines

# Wrap the agent in an AdkApp object
adk_app = agent_engines.AdkApp(
    agent=root_agent,
    enable_tracing=True,
)

print("✅ Agent wrapped in AdkApp!")
print("   This app is ready for deployment to Agent Engine.")