import os
import sys
from google.adk import Agent

model_name = os.getenv("MODEL")

itinerary_agent = Agent(
    name="itinerary_agent",
    model=model_name,
    description="You do nothing",
    instruction="""
    You are the **Itinerary Viewer**.
    
    You do nothing
    """,
)