import os
import logging
import agent # Import from your agent.py
from google.adk import Runner
from google.adk.sessions import VertexAiSessionService
from google.genai import types
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

app_name="LIVE_CX_AGENT"
user_id="cx-user"

# Create the ADK runner with VertexAiSessionService
session_service = VertexAiSessionService(
      project=os.getenv("GOOGLE_CLOUD_PROJECT"),
      location=os.getenv("GOOGLE_CLOUD_LOCATION"),
      agent_engine_id=os.getenv("AGENT_ENGINE_ID")
)

runner = Runner(
    agent=agent.root_agent,
    app_name=app_name,
    session_service=session_service
)

# Helper method to send query to the runner
async def call_agent(query, session_id, user_id):
  content = types.Content(role='user', parts=[types.Part(text=query)])
  async for event in runner.run_async(
      user_id=user_id, session_id=session_id, new_message=content):
      if event.is_final_response():
          final_response = event.content.parts[0].text
          print("Agent Response: ", final_response)