import os
from google.adk import Agent
from google.adk.tools import google_search
from google.adk.tools import AgentTool

model_name = os.getenv("MODEL")

_search_worker = Agent(
    name="google_search_tool", 
    model=model_name,
    description="Searches the web for live travel information, top 10 lists, and destination reviews.", 
    instruction="""
    You are a Google Search Specialist.
    1. Your ONLY job is to search the web for the user's query.
    2. Return a summary of the top results.
    3. Focus on "Best of" lists, travel guides, and top-rated destinations.
    """,
    tools=[google_search] 
)
google_search_tool = AgentTool(agent=_search_worker)