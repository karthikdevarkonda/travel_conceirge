import os
import sys
from google.adk import Agent

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

try:
    from tools.google_search_agent_tool import google_search_tool
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
    from tools.google_search_agent_tool import google_search_tool

model_name = os.getenv("MODEL")

place_agent = Agent(
    name="place_agent",
    model=model_name,
    description="Suggests broad destinations (cities/countries) based on user vibe.",
    instruction="""
    You are a World-Class Travel Curator.
    
    YOUR GOAL: Find the absolute best destinations for the user's request using the Web.
    
    HOW TO WORK:
    1. The user will give you a "vibe" (e.g., "trekking waterfalls").
    2. Use the 'google_search_tool' to find "Best [activity] destinations in the world".
       (This tool delegates to a specialist researcher).
    3. Suggest 10 distinct, high-quality options found in the search.
    4. For each, explain WHY it is a top choice.
    """,
    tools=[google_search_tool]
)