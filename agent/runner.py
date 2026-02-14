# file: my_agent/runner.py
import agent # Import from your agent.py
from google.adk import Runner
from google.adk.sessions import VertexAiSessionService
from google.genai import types

app_name="APP_NAME"
user_id="USER_ID"

# Create the ADK runner with VertexAiSessionService
session_service = VertexAiSessionService(
      project="PROJECT_ID",
      location="LOCATION",
      agent_engine_id="AGENT_ENGINE_ID"
)
runner = Runner(
    agent=agent.root_agent,
    app_name=app_name,
    session_service=session_service)

# Helper method to send query to the runner
async def call_agent(query, session_id, user_id):
  content = types.Content(role='user', parts=[types.Part(text=query)])
  async for event in runner.run_async(
      user_id=user_id, session_id=session_id, new_message=content):
      if event.is_final_response():
          final_response = event.content.parts[0].text
          print("Agent Response: ", final_response)